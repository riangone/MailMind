import time
import requests
import json
from ai.base import AIBase
from utils.logger import log

class OpenAIProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend

    def call(self, prompt: str, tools: list = None) -> str:
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

        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=data, headers=headers, timeout=180)
                # 429 限流：指数退避
                if resp.status_code == 429:
                    wait = 2 ** attempt
                    log.warning(f"API 限流，{wait} 秒后重试 ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                # 5xx 服务器错误：重试
                if resp.status_code >= 500:
                    wait = 2 ** attempt
                    log.warning(f"服务器错误 ({resp.status_code})，{wait} 秒后重试 ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                choice = resp.json()["choices"][0]
                return choice["message"]["content"].strip()
            except requests.exceptions.Timeout:
                wait = 2 ** attempt
                log.warning(f"请求超时，{wait} 秒后重试 ({attempt+1}/{max_retries})")
                time.sleep(wait)
            except requests.exceptions.RequestException as e:
                log.error(f"OpenAI 兼容 API 调用失败 ({self.backend.get('model')}): {e}")
                return f"AI 出错：{e}"
            except Exception as e:
                log.error(f"OpenAI 兼容 API 调用失败 ({self.backend.get('model')}): {e}")
                return f"AI 出错：{e}"

        return f"AI 出错：重试 {max_retries} 次后仍然失败"
