# test_memory_system.py
import os
from app.model.rag.core.chroma_memory_manager import ChromaMemoryManager
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def chat_with_memory(user_id: str, user_input: str, memory_manager: ChromaMemoryManager):
    """
    带记忆的聊天函数

    Args:
        user_id: 用户ID
        user_input: 用户输入
        memory_manager: 记忆管理器
    """
    # 1. 检索相关记忆
    print("\n🔍 检索用户记忆...")
    relevant_memories = memory_manager.retrieve_memories(
        user_id=user_id,
        query=user_input,
        top_k=3
    )

    # 2. 构建记忆上下文
    context = ""
    if relevant_memories:
        context = "以下是用户过去提到的相关内容：\n"
        for i, mem in enumerate(relevant_memories, 1):
            emotion = mem['metadata'].get('emotion', '未知')
            datetime_str = mem['metadata'].get('datetime', '未知时间')
            context += f"{i}. [{datetime_str}] [{emotion}] {mem['text']}\n"

    # 3. 构建 prompt
    prompt = f"""你是一位温暖的心理陪伴者"心语"。请结合用户当前输入和历史记忆进行回应。

历史记忆：
{context if context else "（这是用户第一次对话，暂无历史记忆）"}

当前输入：
{user_input}

请以共情、支持的语气回应，避免机械重复。如果历史记忆中有相关内容，请自然地关联起来，展现你对用户情况的了解和关心。
"""

    # 4. 调用大模型
    print("\n🤖 生成回复...")
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    answer = response.choices[0].message.content

    # 5. 保存当前对话到记忆
    print("\n💾 保存对话记忆...")

    # 保存用户输入（可选：先进行情感分析）
    emotion = predict_emotion(user_input)  # 需要实现情感分析
    memory_manager.save_memory(
        user_id=user_id,
        text=user_input,
        metadata={
            "role": "user",
            "emotion": emotion,
            "type": "user_message"
        }
    )

    # 保存AI回复
    memory_manager.save_memory(
        user_id=user_id,
        text=answer,
        metadata={
            "role": "assistant",
            "type": "ai_response"
        }
    )

    return answer, relevant_memories

def predict_emotion(text: str) -> str:
    """
    简单的情感预测（实际项目中应使用更复杂的模型）
    """
    # 这里可以集成情感分析模型
    # 为演示，使用简单的关键词匹配
    keywords = {
        "焦虑": ["焦虑", "担心", "紧张", "害怕"],
        "压力大": ["压力", "累", "疲惫", "撑不住"],
        "悲伤": ["难过", "伤心", "悲伤", "痛苦"],
        "愤怒": ["生气", "愤怒", "气愤", "恼火"],
        "快乐": ["开心", "高兴", "快乐", "愉快"]
    }

    for emotion, kws in keywords.items():
        if any(kw in text for kw in kws):
            return emotion

    return "平静"

def test_memory_system():
    """测试记忆系统"""
    print("=" * 70)
    print(" 心语机器人 - Chroma 记忆系统测试")
    print("=" * 70)

    # 初始化记忆管理器
    memory_manager = ChromaMemoryManager(persist_directory="./chroma_db/test_memory")

    user_id = "test_user_001"

    # 第一轮对话
    print("\n【第1轮对话】")
    print("-" * 70)
    user_input_1 = "最近工作压力好大，每天都加班到很晚。"
    print(f"用户: {user_input_1}")

    response_1, memories_1 = chat_with_memory(user_id, user_input_1, memory_manager)
    print(f"\n心语: {response_1}")

    # 第二轮对话
    print("\n\n【第2轮对话】")
    print("-" * 70)
    user_input_2 = "我觉得自己快撑不住了，感觉身体也吃不消了。"
    print(f"用户: {user_input_2}")

    response_2, memories_2 = chat_with_memory(user_id, user_input_2, memory_manager)
    print(f"\n心语: {response_2}")

    # 第三轮对话（测试记忆检索）
    print("\n\n【第3轮对话 - 测试记忆检索】")
    print("-" * 70)
    user_input_3 = "项目快上线了，这周又要天天熬夜了。"
    print(f"用户: {user_input_3}")

    response_3, memories_3 = chat_with_memory(user_id, user_input_3, memory_manager)
    print(f"\n心语: {response_3}")

    # 显示检索到的记忆
    print("\n\n【检索到的历史记忆】")
    print("-" * 70)
    for i, mem in enumerate(memories_3, 1):
        print(f"{i}. {mem['text']}")
        print(f"   时间: {mem['metadata']['datetime']}")
        print(f"   情绪: {mem['metadata'].get('emotion', '未知')}")
        print()

    print("=" * 70)
    print("测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    test_memory_system()