"""
tests/test_skills.py - 技能系统测试

测试范围：
1. 技能加载（MD 文件解析）
2. 技能指令渲染（模板变量替换）
3. 安全约束注入
4. 多语言支持
"""
import unittest
import os
import sys

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSkillLoading(unittest.TestCase):
    """测试技能加载"""

    def test_load_all_skills(self):
        from skills.loader import load_all_skills
        skills = load_all_skills()
        self.assertGreater(len(skills), 0, "应该至少加载一个技能")

    def test_required_skills_exist(self):
        """核心技能文件应该存在"""
        from skills.loader import get_skill

        required = [
            'stock', 'news_briefing', 'system_status',
            'ai_job', 'translate', 'summarize',
            'code_executor', 'code_review', 'shell_exec',
            'calendar_skill', 'github', 'invoice', 'ticket',
        ]
        for name in required:
            skill = get_skill(name)
            self.assertIsNotNone(skill, f"技能 '{name}' 应该存在")

    def test_skill_metadata(self):
        """每个技能应该有基本元数据"""
        from skills.loader import load_all_skills
        skills = load_all_skills()

        for name, sk in skills.items():
            self.assertTrue(sk.name, f"技能 '{name}' 应该有 name")
            self.assertTrue(sk.description, f"技能 '{name}' 应该有 description")
            self.assertTrue(sk.instruction, f"技能 '{name}' 应该有 instruction")
            self.assertIn(sk.category, ['general', 'communication', 'coding', 'search', 'automation'],
                          f"技能 '{name}' 的 category 应该有效")


class TestSkillInstructionRendering(unittest.TestCase):
    """测试技能指令渲染"""

    def test_variable_replacement(self):
        """模板变量应该被替换"""
        from skills.loader import get_skill

        skill = get_skill('translate')
        self.assertIsNotNone(skill)

        result = skill.run({
            'text': 'Hello World',
            'target_lang': '中文',
        })
        self.assertIn('Hello World', result)
        self.assertIn('中文', result)

    def test_missing_variable_filled_with_default(self):
        """缺失变量应该使用默认值或空字符串"""
        from skills.loader import get_skill

        skill = get_skill('stock')
        result = skill.run({})  # 不提供任何参数
        # 应该有默认 query
        self.assertIn('股市行情', result)

    def test_optional_variable_not_required(self):
        """可选变量不传递时不应报错"""
        from skills.loader import get_skill

        skill = get_skill('system_status')
        result = skill.run({})  # 不提供 query
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


class TestSecurityConstraints(unittest.TestCase):
    """测试安全约束注入"""

    def _get_all_instructions(self):
        from skills.loader import load_all_skills
        skills = load_all_skills()
        return {name: sk.instruction for name, sk in skills.items()}

    def test_forbid_filesystem_exploration(self):
        """所有技能应该包含禁止探索文件系统的约束"""
        instructions = self._get_all_instructions()
        for name, instr in instructions.items():
            self.assertIn('禁止探索文件系统', instr,
                          f"技能 '{name}' 应该包含'禁止探索文件系统'约束")

    def test_forbid_task_modification(self):
        """所有技能应该包含禁止创建/修改任务的约束"""
        instructions = self._get_all_instructions()
        for name, instr in instructions.items():
            self.assertIn('禁止创建/修改任务', instr,
                          f"技能 '{name}' 应该包含'禁止创建/修改任务'约束")

    def test_output_only_final_result(self):
        """所有技能应该包含只输出最终结果的约束"""
        instructions = self._get_all_instructions()
        for name, instr in instructions.items():
            self.assertIn('只输出最终结果', instr,
                          f"技能 '{name}' 应该包含'只输出最终结果'约束")


class TestMultiLanguageSupport(unittest.TestCase):
    """测试多语言支持"""

    def test_stock_multilingual(self):
        """stock 技能应该有中日英描述"""
        from skills.loader import get_skill
        skill = get_skill('stock')

        self.assertTrue(skill.description)
        self.assertTrue(skill.description_ja)
        self.assertTrue(skill.description_en)

    def test_system_status_multilingual(self):
        """system_status 技能应该有中日英描述"""
        from skills.loader import get_skill
        skill = get_skill('system_status')

        self.assertTrue(skill.description)
        self.assertTrue(skill.description_ja)
        self.assertTrue(skill.description_en)


class TestSystemStatusSkill(unittest.TestCase):
    """测试 system_status 技能的完整性"""

    def test_allows_safe_commands(self):
        """应该包含允许的安全命令"""
        from skills.loader import get_skill
        skill = get_skill('system_status')

        # 应该包含关键系统命令
        for cmd_fragment in ['free -h', 'df -h', 'uptime', 'top']:
            self.assertIn(cmd_fragment, skill.instruction,
                          f"system_status 应该包含命令 '{cmd_fragment}'")

    def test_has_output_structure(self):
        """应该定义输出结构要求"""
        from skills.loader import get_skill
        skill = get_skill('system_status')

        for section in ['系统概览', 'CPU', '内存', '磁盘', '网络']:
            self.assertIn(section, skill.instruction,
                          f"system_status 应该包含'{section}'输出要求")


class TestStockSkill(unittest.TestCase):
    """测试 stock 技能的完整性"""

    def test_has_output_structure(self):
        """应该定义输出结构要求"""
        from skills.loader import get_skill
        skill = get_skill('stock')

        for section in ['市场概况', '热点板块', '驱动因素']:
            self.assertIn(section, skill.instruction,
                          f"stock 应该包含'{section}'输出要求")


class TestNewsBriefingSkill(unittest.TestCase):
    """测试 news_briefing 技能的完整性"""

    def test_has_required_params(self):
        """应该有必填参数 query"""
        from skills.loader import get_skill
        skill = get_skill('news_briefing')

        self.assertIn('query', skill.params)

    def test_has_output_structure(self):
        """应该有输出结构建议"""
        from skills.loader import get_skill
        skill = get_skill('news_briefing')

        self.assertIn('核心要点', skill.instruction)


if __name__ == "__main__":
    unittest.main()
