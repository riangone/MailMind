import requests
from ai.base import AIBase
from utils.logger import log


class OllamaProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend
        base_url = backend.get("base_url", "http://localhost:11434").rstrip("/")
        self.url = f"{base_url}/v1/chat/completions"
        self.model = backend.get("model", "")

    def call(self, prompt: str, tools: list = None) -> str:
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        try:
            resp = requests.post(self.url, json=data, timeout=300)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log.error(f"Ollama 调用失败 ({self.model}): {e}")
            return f"AI 出错：{e}"
