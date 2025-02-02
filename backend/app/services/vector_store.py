import os
from typing import List, Optional
import numpy as np
from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType
)
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self):
        self.host = os.getenv("MILVUS_HOST", "localhost")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.collection_name = "document_chunks"
        self.dim = 768  # sentence-transformers维度
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self._connect()
        self._init_collection()

    def _connect(self):
        """连接到Milvus服务器"""
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )

    def _init_collection(self):
        """初始化集合，如果不存在则创建"""
        if utility.exists_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        schema = CollectionSchema(fields=fields, description="文档块存储")
        self.collection = Collection(self.collection_name, schema)
        
        # 创建索引
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

    def add_texts(self, texts: List[str], document_id: str):
        """添加文本到向量存储"""
        if not texts:
            return
        
        # 生成嵌入
        embeddings = self.encoder.encode(texts)
        
        # 准备数据
        entities = [
            {
                "document_id": [document_id] * len(texts),
                "content": texts,
                "embedding": embeddings.tolist()
            }
        ]
        
        # 插入数据
        self.collection.insert(entities)
        self.collection.flush()

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        document_id: Optional[str] = None
    ) -> List[str]:
        """执行相似性搜索"""
        # 生成查询向量
        query_embedding = self.encoder.encode([query])[0]
        
        # 准备搜索参数
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        # 执行搜索
        self.collection.load()
        expr = f"document_id == '{document_id}'" if document_id else None
        results = self.collection.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=k,
            expr=expr,
            output_fields=["content"]
        )
        
        # 返回结果
        return [hit.entity.get('content') for hit in results[0]]

    def delete_by_document_id(self, document_id: str):
        """删除指定文档ID的所有记录"""
        expr = f"document_id == '{document_id}'"
        self.collection.delete(expr)
        self.collection.flush()
