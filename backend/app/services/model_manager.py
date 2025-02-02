import os
import aiohttp
import ollama
from typing import List, Dict
import asyncio
from datetime import datetime, timedelta

class ModelManager:
    def __init__(self):
        self._models = {}
        self._last_update = None
        self._update_interval = timedelta(minutes=30)
        self._lock = asyncio.Lock()

    async def get_models(self) -> Dict[str, List[str]]:
        """获取所有可用的AI模型列表"""
        if self._should_update():
            async with self._lock:
                if self._should_update():  # 双重检查
                    await self._update_models()
        return self._models

    def _should_update(self) -> bool:
        """检查是否需要更新模型列表"""
        return (
            not self._last_update or 
            datetime.now() - self._last_update > self._update_interval
        )

    async def _update_models(self):
        """更新所有AI服务商的模型列表"""
        tasks = [
            self._update_deepseek_models(),
            self._update_ollama_models(),
            self._update_groq_models()
        ]
        await asyncio.gather(*tasks)
        self._last_update = datetime.now()

    async def _update_deepseek_models(self):
        """获取DeepSeek可用模型列表"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.deepseek.com/v1/models",
                    headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._models["deepseek"] = [
                            model["id"] for model in data.get("data", [])
                        ]
                    else:
                        self._models["deepseek"] = ["deepseek-chat"]
        except Exception:
            self._models["deepseek"] = ["deepseek-chat"]

    async def _update_ollama_models(self):
        """获取Ollama可用模型列表"""
        try:
            models = ollama.list()
            self._models["ollama"] = [model["name"] for model in models.get("models", [])]
        except Exception:
            self._models["ollama"] = ["llama2"]

    async def _update_groq_models(self):
        """获取GROQ可用模型列表"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.groq.com/v1/models",
                    headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._models["groq"] = [
                            model["id"] for model in data.get("data", [])
                        ]
                    else:
                        self._models["groq"] = ["mixtral-8x7b-32768"]
        except Exception:
            self._models["groq"] = ["mixtral-8x7b-32768"]

model_manager = ModelManager()
