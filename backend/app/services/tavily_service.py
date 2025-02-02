import os
from tavily import TavilyClient

class TavilySearchService:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Tavily API Key 未配置")
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5):
        """
        使用Tavily执行搜索
        """
        try:
            response = self.client.search(query=query, max_results=max_results)
            return response.get('results', [])
        except Exception as e:
            raise Exception(f"Tavily搜索失败: {str(e)}")
