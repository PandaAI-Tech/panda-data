"""CHANGELOG.md 格式单元测试。

验证 panda-data-skill 和 panda-data 两个 CHANGELOG.md 文件
遵循 Keep a Changelog 格式，包含 v1.0.0 和 v2.0.0 版本条目。

Validates: Requirements 5.2, 5.3, 5.4
"""

import re
from pathlib import Path

import pytest

# 项目根目录（panda-data-tools 的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SKILL_CHANGELOG = PROJECT_ROOT / "panda-data" / "panda-data-skill" / "CHANGELOG.md"
TOOLS_CHANGELOG = PROJECT_ROOT / "panda-data" / "CHANGELOG.md"

CHANGELOG_FILES = [
    pytest.param(SKILL_CHANGELOG, id="skill-changelog"),
    pytest.param(TOOLS_CHANGELOG, id="tools-changelog"),
]


@pytest.fixture(params=CHANGELOG_FILES)
def changelog_path(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture
def changelog_content(changelog_path: Path) -> str:
    assert changelog_path.exists(), f"CHANGELOG not found: {changelog_path}"
    return changelog_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. 文件存在性
# ---------------------------------------------------------------------------


class TestChangelogExists:
    """验证 CHANGELOG.md 文件存在。"""

    def test_skill_changelog_exists(self) -> None:
        assert SKILL_CHANGELOG.exists(), (
            f"panda-data-skill/CHANGELOG.md not found at {SKILL_CHANGELOG}"
        )

    def test_tools_changelog_exists(self) -> None:
        assert TOOLS_CHANGELOG.exists(), (
            f"panda-data/CHANGELOG.md not found at {TOOLS_CHANGELOG}"
        )


# ---------------------------------------------------------------------------
# 2. 版本条目存在性 (Requirements 5.2, 5.3)
# ---------------------------------------------------------------------------


class TestVersionEntries:
    """验证 v1.0.0 和 v2.0.0 版本条目存在。"""

    def test_contains_v1_entry(self, changelog_content: str) -> None:
        """CHANGELOG 应包含 [1.0.0] 版本条目。"""
        assert re.search(r"##\s*\[1\.0\.0\]", changelog_content), (
            "CHANGELOG should contain a [1.0.0] version entry"
        )

    def test_contains_v2_entry(self, changelog_content: str) -> None:
        """CHANGELOG 应包含 [2.0.0] 版本条目。"""
        assert re.search(r"##\s*\[2\.0\.0\]", changelog_content), (
            "CHANGELOG should contain a [2.0.0] version entry"
        )

    def test_v2_before_v1(self, changelog_content: str) -> None:
        """v2.0.0 条目应出现在 v1.0.0 之前（新版本在上）。"""
        v2_pos = changelog_content.find("[2.0.0]")
        v1_pos = changelog_content.find("[1.0.0]")
        assert v2_pos < v1_pos, "v2.0.0 entry should appear before v1.0.0"


# ---------------------------------------------------------------------------
# 3. Keep a Changelog 格式 (Requirement 5.4)
# ---------------------------------------------------------------------------


class TestKeepAChangelogFormat:
    """验证 CHANGELOG 遵循 Keep a Changelog 格式。"""

    def test_has_changelog_title(self, changelog_content: str) -> None:
        """文件应以 '# Changelog' 标题开头。"""
        assert re.search(r"^#\s+Changelog", changelog_content, re.MULTILINE), (
            "CHANGELOG should start with '# Changelog' heading"
        )

    def test_has_added_or_changed_section(self, changelog_content: str) -> None:
        """CHANGELOG 应包含 '### Added' 或 '### Changed' 小节。"""
        has_added = "### Added" in changelog_content
        has_changed = "### Changed" in changelog_content
        assert has_added or has_changed, (
            "CHANGELOG should contain '### Added' or '### Changed' sections"
        )

    def test_v1_has_added_section(self, changelog_content: str) -> None:
        """v1.0.0 条目应包含 '### Added' 小节。"""
        v1_match = re.search(r"##\s*\[1\.0\.0\].*", changelog_content)
        assert v1_match, "v1.0.0 entry not found"
        v1_section = changelog_content[v1_match.start():]
        assert "### Added" in v1_section, (
            "v1.0.0 section should contain '### Added'"
        )

    def test_v2_has_added_section(self, changelog_content: str) -> None:
        """v2.0.0 条目应包含 '### Added' 小节。"""
        v2_match = re.search(r"##\s*\[2\.0\.0\].*", changelog_content)
        assert v2_match, "v2.0.0 entry not found"
        v1_match = re.search(r"##\s*\[1\.0\.0\].*", changelog_content)
        end = v1_match.start() if v1_match else len(changelog_content)
        v2_section = changelog_content[v2_match.start():end]
        assert "### Added" in v2_section, (
            "v2.0.0 section should contain '### Added'"
        )

    def test_version_entries_have_dates(self, changelog_content: str) -> None:
        """版本条目应包含日期（YYYY-MM-DD 格式）。"""
        version_lines = re.findall(
            r"##\s*\[\d+\.\d+\.\d+\].*", changelog_content
        )
        assert len(version_lines) >= 2, "Should have at least 2 version entries"
        for line in version_lines:
            assert re.search(r"\d{4}-\d{2}-\d{2}", line), (
                f"Version entry should contain a date: {line}"
            )

    def test_contains_keep_a_changelog_reference(
        self, changelog_content: str
    ) -> None:
        """CHANGELOG 应包含 Keep a Changelog 参考链接。"""
        assert "keepachangelog.com" in changelog_content, (
            "CHANGELOG should contain a reference link to keepachangelog.com"
        )
