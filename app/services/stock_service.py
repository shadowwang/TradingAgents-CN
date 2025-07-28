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

    def run_stock_analysis(self, stock_code: str, analysis_date:str, analysts:str, research_depth: int):
        try:
            preparer = get_stock_preparer()
            preparation_result = preparer.prepare_stock_data(stock_code)
            if not preparation_result.is_valid:
                return {
                    'success': False,
                    'error': preparation_result.error_message,
                    'suggestion': preparation_result.suggestion,
                    'stock_symbol': stock_code,
                    'analysis_date': analysis_date,
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
                'stock_symbol': stock_code,
                'analysis_date': analysis_date,
                'state': None,
                'decision': None,
            }

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "deepseek"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-chat"
        if research_depth == 1:  # 1级 - 快速分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            # 保持内存功能启用，因为内存操作开销很小但能显著提升分析质量
            config["memory_enabled"] = True

            # 统一使用在线工具，避免离线工具的各种问题
            config["online_tools"] = True  # 所有市场都使用统一工具
        elif research_depth == 2:  # 2级 - 基础分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif research_depth == 3:  # 3级 - 标准分析 (默认)
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif research_depth == 4:  # 4级 - 深度分析
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
        graph = TradingAgentsGraph(analysts, config=config, debug=False)
        state, decision = graph.propagate(stock_code, analysis_date)

        risk_assessment = self.extract_risk_assessment(state)
        # 将风险评估添加到状态中
        if risk_assessment:
            state['risk_assessment'] = risk_assessment


        results = {
            'stock_symbol': stock_code,
            'analysis_date': analysis_date,
            'analysts': analysts,
            'research_depth': research_depth,
            'state': state,
            'decision': decision,
            'success': True,
            'suggestion': None,
        }


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