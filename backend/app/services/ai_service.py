from typing import List, Optional, AsyncGenerator
import os
import json
import aiohttp
from .model_manager import ModelManager
from .document_processor import DocumentProcessor

class AIService:
    def __init__(self):
        self.model_manager = ModelManager()
        self.document_processor = DocumentProcessor()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

    async def process_query_stream(
        self,
        query: str,
        model_provider: str,
        model_name: str,
        document_id: Optional[str] = None,
        use_rag: bool = True
    ) -> AsyncGenerator[str, None]:
        """处理查询，支持RAG和流式输出"""
        # 如果启用RAG且指定了文档ID，获取相关上下文
        context = ""
        if use_rag and document_id:
            similar_texts = self.document_processor.search_similar(query, k=3, document_id=document_id)
            if similar_texts:
                context = "\n\n".join(similar_texts)

        # 构建提示词
        if context:
            prompt = f"""基于以下上下文回答问题。如果上下文中没有相关信息，请说明无法从文档中找到相关信息。

上下文：
{context}

问题：{query}"""
        else:
            prompt = query

        # 根据不同的模型提供商处理请求
        if model_provider == "deepseek":
            async for chunk in self._call_deepseek_stream(prompt, model_name):
                yield chunk
        elif model_provider == "groq":
            async for chunk in self._call_groq_stream(prompt, model_name):
                yield chunk
        elif model_provider == "ollama":
            async for chunk in self._call_ollama_stream(prompt, model_name):
                yield chunk
        else:
            raise ValueError(f"不支持的模型提供商: {model_provider}")

    async def _call_deepseek_stream(self, prompt: str, model_name: str) -> AsyncGenerator[str, None]:
        """调用DeepSeek API（流式）"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"DeepSeek API调用失败: {await response.text()}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        if line == 'data: [DONE]':
                            break
                        try:
                            data = json.loads(line[6:])
                            if content := data.get('choices', [{}])[0].get('delta', {}).get('content'):
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def _call_groq_stream(self, prompt: str, model_name: str) -> AsyncGenerator[str, None]:
        """调用GROQ API（流式）"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"GROQ API调用失败: {await response.text()}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        if line == 'data: [DONE]':
                            break
                        try:
                            data = json.loads(line[6:])
                            if content := data.get('choices', [{}])[0].get('delta', {}).get('content'):
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def _call_ollama_stream(self, prompt: str, model_name: str) -> AsyncGenerator[str, None]:
        """调用Ollama API（流式）"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API调用失败: {await response.text()}")
                
                async for line in response.content:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                    except json.JSONDecodeError:
                        continue

    def process_document(self, file_path: str, document_id: str) -> str:
        """处理文档"""
        return self.document_processor.process_document(file_path, document_id)

    def delete_document(self, document_id: str):
        """删除文档"""
        self.document_processor.delete_document(document_id)
