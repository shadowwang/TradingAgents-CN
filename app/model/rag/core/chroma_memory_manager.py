import chromadb
from chromadb.config import Settings
import os
import time
import uuid
from datetime import datetime

from app.model.rag.core.embedding_service import EmbeddingService


# 配置 Chroma 客户端
class ChromaMemoryManager:
    """Chroma 记忆管理器"""

    def __init__(self, persist_directory="./chroma_db/user_memory"):
        """
        初始化 Chroma 客户端

        Args:
            persist_directory: 数据持久化目录
        """
        self.persist_directory = persist_directory

        # 使用新版Chroma的PersistentClient替代旧的Client方式
        self.client = chromadb.PersistentClient(path=persist_directory)

        # 获取或创建集合（Collection）
        # 相当于 Pinecone 中的 Index
        self.collection = self.client.get_or_create_collection(
            name="emotion_chat_memory",
            metadata={"description": "心语机器人用户记忆系统"}
        )

        print(f"✓ Chroma 初始化成功")
        print(f"  存储路径: {persist_directory}")
        print(f"  集合名称: emotion_chat_memory")

        self.embedding_service = EmbeddingService()

    def save_memory(self, user_id: str, text: str, metadata: dict = None):
        """
        保存用户记忆

        Args:
            user_id: 用户ID
            text: 记忆内容
            metadata: 元数据（情绪、时间戳等）
        """
        # 生成向量
        vector = self.embedding_service.get_embedding(text)

        # 构建元数据
        if metadata is None:
            metadata = {}

        metadata.update({
            "user_id": user_id,
            "text": text,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        })

        # 生成唯一ID
        memory_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

        # 存储到 Chroma
        self.collection.add(
            ids=[memory_id],
            embeddings=[vector],
            metadatas=[metadata],
            documents=[text]  # Chroma 支持同时存储原始文本
        )

        print(f"✓ 记忆已保存: {memory_id}")
        return memory_id

    def retrieve_memories(self, user_id: str, query: str, top_k: int = 3):
        """
        检索相关记忆

        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            相关记忆列表
        """
        # 生成查询向量
        query_vector = self.embedding_service.get_embedding(query)

        # 在 Chroma 中检索
        # Chroma 支持 where 过滤器，类似 Pinecone 的 filter
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where={"user_id": user_id}  # 过滤特定用户的记忆
        )

        # 提取记忆内容
        memories = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memory = {
                    'id': results['ids'][0][i],
                    'text': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                memories.append(memory)

        print(f"✓ 检索到 {len(memories)} 条相关记忆")
        return memories