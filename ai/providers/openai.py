import requests
import json
from ai.base import AIBase
from utils.logger import log

class OpenAIProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend

    def call(self, prompt: str, tools: list = None) -> str:
        try:
            url = self.backend.get("url", "https://api.openai.com/v1/chat/completions")
            headers = {
                "Authorization": f"Bearer {self.backend['api_key']}", 
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.backend["model"],
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if tools:
                data["tools"] = [tool.to_schema() for tool in tools]
            
            resp = requests.post(url, json=data, headers=headers, timeout=180)
            resp.raise_for_status()
            choice = resp.json()["choices"][0]
            return choice["message"]["content"].strip()
        except Exception as e:
            log.error(f"OpenAI 兼容 API 调用失败 ({self.backend.get('model')}): {e}")
            return f"AI 出错：{e}"
