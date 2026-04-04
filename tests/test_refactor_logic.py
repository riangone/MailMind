import unittest
import os
import sys

# 将项目根目录加入路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.prompts import HELP_BODY, TEMPLATES
from ai.providers import get_ai_provider
from core.mail_client import get_archive_folder

class TestRefactor(unittest.TestCase):
    def test_prompts_loading(self):
        """验证多语言模板是否加载正常"""
        self.assertIn("zh", HELP_BODY)
        self.assertIn("【模板 1】", HELP_BODY["zh"])
        self.assertIn("en", TEMPLATES)
        self.assertTrue(len(TEMPLATES["zh"]) > 5)

    def test_ai_provider_dynamic_loading(self):
        """验证 AI 提供商是否能按需动态加载"""
        mock_backend_openai = {
            "type": "api_openai",
            "api_key": "sk-test-key",
            "model": "gpt-4o"
        }
        provider = get_ai_provider("test_ai", mock_backend_openai)
        from ai.providers.openai import OpenAIProvider
        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.backend["model"], "gpt-4o")

    def test_archive_folder_logic(self):
        """验证归档文件夹自动检测逻辑"""
        gmail_mb = {"imap_server": "imap.gmail.com"}
        self.assertEqual(get_archive_folder(gmail_mb), "[Gmail]/All Mail")
        
        custom_mb = {"imap_server": "imap.custom.com", "archive_folder": "MyArchive"}
        self.assertEqual(get_archive_folder(custom_mb), "MyArchive")

    def test_cli_provider_loading(self):
        """验证 CLI 提供商加载"""
        mock_backend_cli = {
            "type": "cli",
            "cmd": "ls",
            "args": ["-la"]
        }
        provider = get_ai_provider("test_cli", mock_backend_cli)
        from ai.providers.cli import CLIProvider
        self.assertIsInstance(provider, CLIProvider)

if __name__ == "__main__":
    unittest.main()
