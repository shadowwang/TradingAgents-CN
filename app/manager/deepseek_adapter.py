#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek适配器
DeepSeek Adapter

功能：
- 适配DeepSeek API的特殊要求
- 处理DeepSeek特定的Prompt格式
- 管理DeepSeek模型参数
"""

import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class DeepSeekAdapter:
    """DeepSeek API适配器"""
    
    def __init__(self, 
                 api_key: str,
                 base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat",
                 temperature: float = 0.7,
                 max_tokens: int = 150):
        """
        初始化DeepSeek适配器
        
        Args:
            api_key: DeepSeek API密钥
            base_url: DeepSeek API基础URL
            model: 模型名称
            temperature: 生成温度
            max_tokens: 最大生成token数
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 创建OpenAI客户端，但使用DeepSeek的API
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        logger.info(f"✓ DeepSeek适配器已初始化 (model={model})")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        调用DeepSeek聊天补全API
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}]
            temperature: 生成温度（可选）
            max_tokens: 最大token数（可选）
            
        Returns:
            API响应
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            return response
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    def simple_chat(self, prompt: str) -> str:
        """
        简单聊天接口
        
        Args:
            prompt: 用户输入
            
        Returns:
            模型回复
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages)
        return response.choices[0].message.content.strip()
    
    def is_deepseek_model(self) -> bool:
        """是否为DeepSeek模型"""
        return True
    
    def get_optimized_prompt(self, 
                           base_prompt: str, 
                           emotion: str, 
                           user_input: str) -> str:
        """
        获取针对DeepSeek优化的Prompt
        
        Args:
            base_prompt: 基础Prompt
            emotion: 用户情绪
            user_input: 用户输入
            
        Returns:
            优化后的Prompt
        """
        # DeepSeek对角色扮演反应良好，强化角色身份
        optimized_prompt = base_prompt
        
        # 添加DeepSeek特定的优化
        deepseek_enhancement = """
        
# DeepSeek特别说明
请以"心语"的身份回复，始终记住你是一个真实的人，而不是AI。
你的回复应该自然、温暖，就像一个真实的朋友在倾诉。
避免使用任何可能暴露你是AI的表达方式。
"""
        
        # 将增强说明添加到基础Prompt中
        if "DeepSeek特别说明" not in optimized_prompt:
            optimized_prompt += deepseek_enhancement
        
        return optimized_prompt
    
    def adapt_temperature_for_emotion(self, emotion: str, emotion_intensity: float) -> float:
        """
        根据情绪调整生成温度
        
        Args:
            emotion: 情绪类型
            emotion_intensity: 情绪强度
            
        Returns:
            调整后的温度
        """
        # 基础温度
        base_temp = self.temperature
        
        # 根据情绪类型调整
        emotion_adjustments = {
            "sad": -0.1,      # 悲伤时更稳定，减少随机性
            "anxious": -0.2,  # 焦虑时更稳定，提供确定性
            "angry": -0.2,    # 愤怒时更稳定，避免激化
            "happy": 0.1,     # 高兴时可以更活跃
            "excited": 0.2,   # 兴奋时可以更有活力
        }
        
        # 根据情绪强度调整
        intensity_adjustment = (emotion_intensity - 5) * 0.02  # -0.1 到 +0.1
        
        # 计算最终温度
        final_temp = base_temp + emotion_adjustments.get(emotion, 0) + intensity_adjustment
        
        # 限制在合理范围内
        final_temp = max(0.1, min(1.0, final_temp))
        
        return final_temp
    
    def adapt_max_tokens_for_emotion(self, emotion: str) -> int:
        """
        根据情绪调整最大token数
        
        Args:
            emotion: 情绪类型
            
        Returns:
            调整后的最大token数
        """
        # 基础token数
        base_tokens = self.max_tokens
        
        # 根据情绪类型调整
        emotion_adjustments = {
            "sad": -20,       # 悲伤时回复可以简短
            "anxious": -10,   # 焦虑时回复不要太长
            "angry": -15,     # 愤怒时回复简短
            "high_risk_depression": -30,  # 危机情况回复简短
        }
        
        # 计算最终token数
        final_tokens = base_tokens + emotion_adjustments.get(emotion, 0)
        
        # 限制在合理范围内
        final_tokens = max(50, min(300, final_tokens))
        
        return final_tokens


def create_deepseek_adapter(api_key: str, 
                           model: str = "deepseek-chat",
                           temperature: float = 0.7,
                           max_tokens: int = 150) -> DeepSeekAdapter:
    """
    创建DeepSeek适配器实例
    
    Args:
        api_key: DeepSeek API密钥
        model: 模型名称
        temperature: 生成温度
        max_tokens: 最大生成token数
        
    Returns:
        DeepSeekAdapter实例
    """
    return DeepSeekAdapter(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


# 测试代码
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 创建适配器
    adapter = create_deepseek_adapter(
        api_key=os.getenv("DEEPSEEK_API_KEY", "test_key"),
        temperature=0.7,
        max_tokens=150
    )
    
    # 测试优化Prompt
    test_prompt = """你是心语，一位28岁的女性心理陪伴者，性格温柔、耐心、富有同理心。"""
    user_input = "我今天被领导批评了，觉得自己一无是处"
    emotion = "sad"
    
    optimized_prompt = adapter.get_optimized_prompt(test_prompt, emotion, user_input)
    print("===== DeepSeek优化Prompt =====")
    print(optimized_prompt)
    
    # 测试温度调整
    temp = adapter.adapt_temperature_for_emotion("sad", 7.5)
    print(f"\n===== 温度调整 =====")
    print(f"原始温度: 0.7, 调整后: {temp:.2f}")
    
    # 测试token数调整
    tokens = adapter.adapt_max_tokens_for_emotion("sad")
    print(f"\n===== Token数调整 =====")
    print(f"原始token: 150, 调整后: {tokens}")