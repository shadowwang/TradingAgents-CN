import os
import sys

from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.model.intent.core.response_generator import ResponseGenerator
from app.manager.deepseek_adapter import DeepSeekAdapter

load_dotenv()

def test_llm_response():
    # 使用DeepSeek适配器
    deepseek_adapter = DeepSeekAdapter(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=150
    )
    
    generator = ResponseGenerator(deepseek_adapter)
    
    # 测试不同情绪场景
    test_cases = [
        {
            "user_input": "我今天被领导批评了，觉得自己一无是处",
            "user_emotion": "sad",
            "emotion_intensity": 7.5
        },
        {
            "user_input": "明天要面试，我好紧张",
            "user_emotion": "anxious",
            "emotion_intensity": 6.0
        },
        {
            "user_input": "你好",
            "user_emotion": "neutral",
            "emotion_intensity": 3.0
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n===== 测试案例 {i} =====")
        print(f"用户输入: {test['user_input']}")
        print(f"情绪: {test['user_emotion']} (强度: {test['emotion_intensity']})")
        
        # 生成回复
        result = generator.generate_response(
            user_input=test['user_input'],
            user_emotion=test['user_emotion'],
            user_id="user_001",
            emotion_intensity=test['emotion_intensity']
        )
        
        # 获取结果
        print(f"\nAI回复: {result['response']}")
        print(f"生成方法: {result['generation_method']}")
        print(f"是否有效: {'是' if result['is_valid'] else '否'}")
        if result.get('warnings'):
            print(f"警告: {', '.join(result['warnings'])}")

if __name__ == "__main__":
    test_llm_response()