import os
import subprocess
import requests
import logging
from ai.base import AIBase
from utils.logger import log

class CLIProvider(AIBase):
    def __init__(self, name: str, backend: dict):
        self.name = name
        self.backend = backend

    def call(self, prompt: str) -> str:
        try:
            env = os.environ.copy()
            if self.name == "qwen":
                for key in ["TAVILY_API_KEY", "GOOGLE_API_KEY", "GOOGLE_SEARCH_ENGINE_ID"]:
                    val = os.environ.get(key, "")
                    if val: env[key] = val
            
            return subprocess.run(
                [self.backend["cmd"]] + self.backend["args"] + [prompt],
                capture_output=True,
                text=True,
                timeout=180,
                env=env
            ).stdout.strip()
        except Exception as e:
            log.error(f"CLI AI 调用失败: {e}")
            return f"AI 出错: {e}"

class OpenAIProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend

    def call(self, prompt: str) -> str:
        try:
            url = self.backend.get("url", "https://api.openai.com/v1/chat/completions")
            headers = {"Authorization": f"Bearer {self.backend['api_key']}", "Content-Type": "application/json"}
            data = {"model": self.backend["model"], "messages": [{"role": "user", "content": prompt}]}
            resp = requests.post(url, json=data, headers=headers, timeout=180)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log.error(f"OpenAI API 调用失败: {e}")
            return f"AI 出错: {e}"

class AnthropicProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend

    def call(self, prompt: str) -> str:
        try:
            headers = {"x-api-key": self.backend["api_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
            data = {"model": self.backend["model"], "max_tokens": 8096, "messages": [{"role": "user", "content": prompt}]}
            resp = requests.post("https://api.anthropic.com/v1/messages", json=data, headers=headers, timeout=180)
            resp.raise_for_status()
            return resp.json()["content"][0]["text"].strip()
        except Exception as e:
            log.error(f"Anthropic API 调用失败: {e}")
            return f"AI 出错: {e}"

class GeminiAPIProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend

    def call(self, prompt: str) -> str:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.backend['model']}:generateContent?key={self.backend['api_key']}"
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=data, timeout=180)
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            log.error(f"Gemini API 调用失败: {e}")
            return f"AI 出错: {e}"

class QwenAPIProvider(AIBase):
    def __init__(self, backend: dict):
        self.backend = backend

    def call(self, prompt: str) -> str:
        try:
            headers = {"Authorization": f"Bearer {self.backend['api_key']}", "Content-Type": "application/json"}
            data = {"model": self.backend["model"], "messages": [{"role": "user", "content": prompt}]}
            resp = requests.post("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", json=data, headers=headers, timeout=180)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log.error(f"Qwen API 调用失败: {e}")
            return f"AI 出错: {e}"

def get_ai_provider(ai_name: str, backend: dict) -> AIBase:
    t = backend["type"]
    if t == "cli": return CLIProvider(ai_name, backend)
    if t == "api_openai": return OpenAIProvider(backend)
    if t == "api_anthropic": return AnthropicProvider(backend)
    if t == "api_gemini": return GeminiAPIProvider(backend)
    if t == "api_qwen": return QwenAPIProvider(backend)
    raise ValueError(f"未知 AI 类型: {t}")
