from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time
from datetime import datetime

class LangChainMemoryManager:
    """使用 LangChain 的记忆管理器"""

    def __init__(self, persist_directory="./chroma_db/user_memory"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        # 创建或加载 Chroma 向量存储
        self.vectorstore = Chroma(
            collection_name="emotion_chat_memory",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

        # 初始化 LLM
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    def save_memory(self, user_id: str, text: str, metadata: dict = None):
        """保存记忆"""
        if metadata is None:
            metadata = {}

        metadata.update({
            "user_id": user_id,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        })

        # 使用 LangChain 的方式添加文档
        self.vectorstore.add_texts(
            texts=[text],
            metadatas=[metadata]
        )

        # 持久化
        self.vectorstore.persist()

    def retrieve_memories(self, user_id: str, query: str, k: int = 3):
        """检索记忆"""
        # 使用 LangChain 的相似度搜索
        # 注意：LangChain 的 Chroma 集成不直接支持元数据过滤
        # 需要手动过滤或使用底层 Chroma 客户端

        docs = self.vectorstore.similarity_search(
            query=query,
            k=k * 3  # 多检索一些，然后手动过滤
        )

        # 过滤属于该用户的记忆
        user_docs = [
            doc for doc in docs
            if doc.metadata.get('user_id') == user_id
        ][:k]

        return user_docs

    def chat(self, user_id: str, user_input: str):
        """带记忆的聊天"""
        # 检索记忆
        memories = self.retrieve_memories(user_id, user_input)

        # 构建记忆上下文
        memory_context = "\n".join([
            f"- [{m.metadata.get('datetime', '未知')}] {m.page_content}"
            for m in memories
        ])

        # 创建 prompt 模板
        prompt = PromptTemplate(
            template="""你是一位温暖的心理陪伴者"心语"。请结合用户的历史记忆进行回应。

历史记忆：
{memory_context}

当前输入：
{user_input}

请以共情、支持的语气回应。
""",
            input_variables=["memory_context", "user_input"]
        )

        # 使用 LCEL 方式创建链
        chain = prompt | self.llm | StrOutputParser()

        # 生成回复
        response = chain.invoke({
            "memory_context": memory_context if memory_context else "（暂无历史记忆）",
            "user_input": user_input
        })

        # 保存记忆
        self.save_memory(user_id, user_input, {"role": "user"})
        self.save_memory(user_id, response, {"role": "assistant"})

        return response