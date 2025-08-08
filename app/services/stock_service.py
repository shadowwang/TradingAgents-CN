import uuid
from datetime import datetime
from typing import List, Dict, Any

from app.model.stock_analysis_info import StockAnalysisInfo
from tradingagents.api.stock_api import search_stocks
from tradingagents.dataflows import search_china_stocks_tushare
from tradingagents.dataflows.interface import search_stocks_tushare
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph import TradingAgentsGraph
from tradingagents.utils.logging_manager import get_logger
from tradingagents.utils.stock_validator import get_stock_preparer
logger = get_logger('server')

# 添加配置管理器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
    logger.info("✅ Token跟踪功能已启用")
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    logger.warning("⚠️ Token跟踪功能未启用")

class StockService:

    def get_team_members(self) -> list[dict[str, int | str]]:
        return [
            {
                id: 1,
                "name": '基本面分析师',
                "icon": '/fundamental-analyst.svg'
            },
            {
                id: 2,
                "name": '舆情分析师',
                "icon": '/social-analyst.svg'
            },
            {
                id: 3,
                "name": '市场分析师',
                "icon": '/market-analyst.svg'
            },
            {
                id: 4,
                "name": '资讯分析师',
                "icon": '/news-analyst.svg'
            }
        ]

    def get_stock_data(self, stock_code: str)-> str:
        return search_stocks_tushare(stock_code)

    def run_stock_analysis(self, stockanalysis_info: StockAnalysisInfo, progress_callback=None):
        try:
            def update_progress(message, step=None, total_steps=None):
                """更新进度"""
                if progress_callback:
                    progress_callback(message, step, total_steps)
                logger.info(f"[进度] {message}")

            # 生成会话ID用于Token跟踪和日志关联
            session_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 1. 数据预获取和验证阶段
            update_progress("🔍 验证股票代码并预获取数据...", 1, 10)

            preparer = get_stock_preparer()
            preparation_result = preparer.prepare_stock_data(stockanalysis_info.stock_code)
            if not preparation_result.is_valid:
                return {
                    'success': False,
                    'error': preparation_result.error_message,
                    'suggestion': preparation_result.suggestion,
                    'stock_symbol': stockanalysis_info.stock_code,
                    'analysis_date': stockanalysis_info.analysis_date,
                    'state': None,
                    'decision': None,
                }
        except Exception as e:
            error_msg = f"❌ 数据预获取过程中发生错误: {str(e)}"
            logger.error(f" {error_msg}")

            return {
                'success': False,
                'error': error_msg,
                'suggestion': "请检查网络连接或稍后重试",
                'stock_symbol': stockanalysis_info.stock_code,
                'analysis_date': stockanalysis_info.analysis_date,
                'state': None,
                'decision': None,
            }

        # 数据预获取成功
        success_msg = f"✅ 数据准备完成: {preparation_result.stock_name} ({preparation_result.market_type})"
        update_progress(success_msg)  # 使用智能检测，不再硬编码步骤

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "deepseek"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-chat"
        if stockanalysis_info.research_depth == 1:  # 1级 - 快速分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            # 保持内存功能启用，因为内存操作开销很小但能显著提升分析质量
            config["memory_enabled"] = True

            # 统一使用在线工具，避免离线工具的各种问题
            config["online_tools"] = True  # 所有市场都使用统一工具
        elif stockanalysis_info.research_depth == 2:  # 2级 - 基础分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif stockanalysis_info.research_depth == 3:  # 3级 - 标准分析 (默认)
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif stockanalysis_info.research_depth == 4:  # 4级 - 深度分析
            config["max_debate_rounds"] = 2
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
        else:  # 5级 - 全面分析
            config["max_debate_rounds"] = 3
            config["max_risk_discuss_rounds"] = 3
            config["memory_enabled"] = True
            config["online_tools"] = True

        # 默认基本面
        # analysts = "fundamentals"
        update_progress(f"📊 开始分析 {stockanalysis_info.stock_name} 股票，这可能需要几分钟时间...")

        graph = TradingAgentsGraph(stockanalysis_info.analysts, config=config, debug=False)
        state, decision = graph.propagate(stockanalysis_info.stock_code, stockanalysis_info.analysis_date)

        risk_assessment = self.extract_risk_assessment(state)
        # 将风险评估添加到状态中
        if risk_assessment:
            state['risk_assessment'] = risk_assessment


        results = {
            'stock_symbol': stockanalysis_info.stock_code,
            'analysis_date': stockanalysis_info.analysis_date,
            'analysts': stockanalysis_info.analysts,
            'research_depth': stockanalysis_info.research_depth,
            'state': state,
            'decision': decision,
            'success': True,
            'suggestion': None,
        }

        update_progress("✅ 分析成功完成！")

        return results

    def extract_risk_assessment(self, state):
        """从分析状态中提取风险评估数据"""
        try:
            risk_debate_state = state.get('risk_debate_state', {})

            if not risk_debate_state:
                return None

            # 提取各个风险分析师的观点并进行中文化
            risky_analysis = self.translate_analyst_labels(risk_debate_state.get('risky_history', ''))
            safe_analysis = self.translate_analyst_labels(risk_debate_state.get('safe_history', ''))
            neutral_analysis = self.translate_analyst_labels(risk_debate_state.get('neutral_history', ''))
            judge_decision = self.translate_analyst_labels(risk_debate_state.get('judge_decision', ''))

            # 格式化风险评估报告
            risk_assessment = f"""
            ## ⚠️ 风险评估报告
        
            ### 🔴 激进风险分析师观点
            {risky_analysis if risky_analysis else '暂无激进风险分析'}
        
            ### 🟡 中性风险分析师观点
            {neutral_analysis if neutral_analysis else '暂无中性风险分析'}
        
            ### 🟢 保守风险分析师观点
            {safe_analysis if safe_analysis else '暂无保守风险分析'}
        
            ### 🏛️ 风险管理委员会最终决议
            {judge_decision if judge_decision else '暂无风险管理决议'}
        
            ---
            *风险评估基于多角度分析，请结合个人风险承受能力做出投资决策*
                    """.strip()

            return risk_assessment

        except Exception as e:
            logger.info(f"提取风险评估数据时出错: {e}")
            return None

    def translate_analyst_labels(self, text):
        """将分析师的英文标签转换为中文"""
        if not text:
            return text

        # 分析师标签翻译映射
        translations = {
            'Bull Analyst:': '看涨分析师:',
            'Bear Analyst:': '看跌分析师:',
            'Risky Analyst:': '激进风险分析师:',
            'Safe Analyst:': '保守风险分析师:',
            'Neutral Analyst:': '中性风险分析师:',
            'Research Manager:': '研究经理:',
            'Portfolio Manager:': '投资组合经理:',
            'Risk Judge:': '风险管理委员会:',
            'Trader:': '交易员:'
        }

        # 替换所有英文标签
        for english, chinese in translations.items():
            text = text.replace(english, chinese)

        return text