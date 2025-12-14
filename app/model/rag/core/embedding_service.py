import os
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """文本嵌入服务"""

    def __init__(self):
        # 使用sentence-transformers作为嵌入模型
        # 这是一个开源的多语言嵌入模型，适合中文文本
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✓ 使用sentence-transformers嵌入模型")
        except Exception as e:
            print(f"加载sentence-transformers失败: {e}")
            # 备选方案：使用OpenAI嵌入模型
            from openai import OpenAI
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            self.use_openai = True
            self.model_name = "text-embedding-ada-002"
            print("✓ 使用OpenAI嵌入模型作为备选")

    def get_embedding(self, text: str) -> list:
        """
        获取文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            向量列表
        """
        if hasattr(self, 'use_openai') and self.use_openai:
            # 使用OpenAI嵌入模型
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name
            )
            return response.data[0].embedding
        else:
            # 使用sentence-transformers
            embedding = self.model.encode(text)
            return embedding.tolist()
