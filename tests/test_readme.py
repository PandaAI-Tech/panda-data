"""README 内容单元测试。

验证 panda-data-skill 和 panda-data 两个 README.md 文件
包含必要章节和内容。

Validates: Requirements 6.1, 6.2, 6.4
"""

import re
from pathlib import Path

import pytest

# 项目根目录（panda-data-tools 的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SKILL_README = PROJECT_ROOT / "panda-data" / "panda-data-skill" / "README.md"
TOOLS_README = PROJECT_ROOT / "panda-data" / "README.md"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def skill_readme() -> str:
    assert SKILL_README.exists(), f"Skill README not found: {SKILL_README}"
    return SKILL_README.read_text(encoding="utf-8")


@pytest.fixture
def tools_readme() -> str:
    assert TOOLS_README.exists(), f"Tools README not found: {TOOLS_README}"
    return TOOLS_README.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Skill 层 README 必要章节 (Requirement 6.1)
# ---------------------------------------------------------------------------


class TestSkillReadmeSections:
    """验证 Skill 层 README 包含必要章节。"""

    @pytest.mark.parametrize(
        "heading",
        [
            "目录结构",
            "安装",
            "凭证配置",
            "快速开始",
            "API 分类概览",
            "示例脚本",
            "功能对比",
            "版本信息",
        ],
    )
    def test_contains_section(self, skill_readme: str, heading: str) -> None:
        """Skill README 应包含指定章节。"""
        assert heading in skill_readme, (
            f"Skill README should contain section: {heading}"
        )

    def test_contains_changelog_link(self, skill_readme: str) -> None:
        """Skill README 应包含 CHANGELOG 链接。"""
        assert "CHANGELOG" in skill_readme, (
            "Skill README should contain a CHANGELOG reference"
        )

    def test_contains_project_title(self, skill_readme: str) -> None:
        """Skill README 应包含项目标题。"""
        assert re.search(r"^#\s+.+", skill_readme, re.MULTILINE), (
            "Skill README should contain a top-level heading"
        )


# ---------------------------------------------------------------------------
# 2. Skill 层 README 功能对比表 (Requirement 6.4)
# ---------------------------------------------------------------------------


class TestSkillReadmeComparisonTable:
    """验证 Skill 层 README 包含 v1.0.0 vs v2.0.0 功能对比表。"""

    def test_contains_comparison_heading(self, skill_readme: str) -> None:
        """应包含功能对比章节标题。"""
        assert "功能对比" in skill_readme, (
            "Skill README should contain a feature comparison section"
        )

    def test_comparison_mentions_v1(self, skill_readme: str) -> None:
        """功能对比表应提及 v1.0.0。"""
        assert "v1.0.0" in skill_readme, (
            "Skill README comparison table should mention v1.0.0"
        )

    def test_comparison_mentions_v2(self, skill_readme: str) -> None:
        """功能对比表应提及 v2.0.0。"""
        assert "v2.0.0" in skill_readme, (
            "Skill README comparison table should mention v2.0.0"
        )

    def test_comparison_table_has_rows(self, skill_readme: str) -> None:
        """功能对比表应包含 markdown 表格行。"""
        # 找到功能对比章节，提取到下一个同级标题之前的内容
        match = re.search(r"##[^#]*功能对比[^\n]*\n([\s\S]*?)(?=\n## |\Z)", skill_readme)
        assert match, "Feature comparison section should contain content"
        section_text = match.group(1)
        # 表格至少有表头行 + 分隔行 + 1 数据行 = 3 行
        table_lines = [l for l in section_text.strip().split("\n") if l.strip().startswith("|")]
        assert len(table_lines) >= 3, (
            f"Comparison table should have at least 3 rows (header + separator + data), got {len(table_lines)}"
        )


# ---------------------------------------------------------------------------
# 3. Tool 层 README 必要章节 (Requirement 6.2)
# ---------------------------------------------------------------------------


class TestToolsReadmeSections:
    """验证 Tool 层 README 包含必要章节。"""

    @pytest.mark.parametrize(
        "heading",
        [
            "安装",
            "使用",
            "项目结构",
            "测试",
        ],
    )
    def test_contains_section(self, tools_readme: str, heading: str) -> None:
        """Tools README 应包含指定章节。"""
        assert heading in tools_readme, (
            f"Tools README should contain section: {heading}"
        )

    def test_contains_v2_features_section(self, tools_readme: str) -> None:
        """Tools README 应包含 v2.0.0 新特性或新增功能章节。"""
        has_new_features = "新特性" in tools_readme or "新增功能" in tools_readme
        assert has_new_features, (
            "Tools README should contain v2.0.0 new features section (新特性 or 新增功能)"
        )

    def test_contains_changelog_link(self, tools_readme: str) -> None:
        """Tools README 应包含 CHANGELOG 链接。"""
        assert "CHANGELOG" in tools_readme, (
            "Tools README should contain a CHANGELOG reference"
        )


# ---------------------------------------------------------------------------
# 4. Tool 层 README 模块和依赖提及 (Requirement 6.2, 6.5)
# ---------------------------------------------------------------------------


class TestToolsReadmeContent:
    """验证 Tool 层 README 提及新增模块和依赖。"""

    def test_mentions_cache_module(self, tools_readme: str) -> None:
        """Tools README 应提及 cache.py 模块。"""
        assert "cache.py" in tools_readme or "cache" in tools_readme.lower(), (
            "Tools README should mention cache.py module"
        )

    def test_mentions_exporter_module(self, tools_readme: str) -> None:
        """Tools README 应提及 exporter.py 模块。"""
        assert "exporter.py" in tools_readme or "exporter" in tools_readme.lower(), (
            "Tools README should mention exporter.py module"
        )

    def test_mentions_duckdb_dependency(self, tools_readme: str) -> None:
        """Tools README 应提及 duckdb 依赖。"""
        assert "duckdb" in tools_readme.lower(), (
            "Tools README should mention duckdb dependency"
        )
