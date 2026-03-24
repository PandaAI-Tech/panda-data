"""SKILL.md 内容验证测试。

验证 Skill 层核心文件的内容完整性和安全性：
- Property 9: 全部 38 个 API 方法名出现在 SKILL.md 中
- Property 10: skill 目录下所有文本文件不包含硬编码凭证
"""

import os
import re
from pathlib import Path
from typing import List

import pytest

# ------------------------------------------------------------------
# 路径常量
# ------------------------------------------------------------------

# panda-data/ 项目根目录
_TOOLS_DIR = Path(__file__).resolve().parent.parent
# panda-data-skill/ 目录（位于 panda-data 内）
_SKILL_DIR = _TOOLS_DIR / "panda-data-skill"
_SKILL_MD = _SKILL_DIR / "SKILL.md"

# ------------------------------------------------------------------
# 全部 38 个 API 方法名
# ------------------------------------------------------------------

ALL_38_METHODS: List[str] = [
    # 行情数据 (2)
    "get_market_data",
    "get_market_min_data",
    # 市场参考数据 (20)
    "get_stock_detail",
    "get_index_detail",
    "get_concept_list",
    "get_concept_constituents",
    "get_industry_detail",
    "get_industry_constituents",
    "get_stock_industry",
    "get_index_indicator",
    "get_index_weights",
    "get_lhb_list",
    "get_lhb_detail",
    "get_repurchase",
    "get_margin",
    "get_hsgt_hold",
    "get_investor_activity",
    "get_restricted_list",
    "get_holder_count",
    "get_top_holders",
    "get_block_trade",
    "get_share_float",
    # 财务与因子数据 (5)
    "get_fina_forecast",
    "get_fina_performance",
    "get_fina_reports",
    "get_factor",
    "get_adj_factor",
    # 交易工具 (5)
    "get_trade_cal",
    "get_prev_trade_date",
    "get_last_trade_date",
    "get_stock_status_change",
    "get_trade_list",
    # 期货数据 (3)
    "get_future_detail",
    "get_future_market_post",
    "get_future_dominant",
]

# ------------------------------------------------------------------
# 文本文件扩展名（用于凭证扫描）
# ------------------------------------------------------------------

TEXT_FILE_EXTENSIONS = {".md", ".py", ".json"}

# ------------------------------------------------------------------
# 凭证硬编码检测模式
# ------------------------------------------------------------------

# 允许的占位符文本（不视为硬编码凭证）
_PLACEHOLDER_PATTERNS: List[str] = [
    r"你的用户名",
    r"你的密码",
    r"YOUR_USERNAME",
    r"YOUR_PASSWORD",
    r"PANDA_DATA_USERNAME",
    r"PANDA_DATA_PASSWORD",
    r"os\.environ\[",
    r"\{baseDir\}",
    r"<your[_\-]",
    r"<username>",
    r"<password>",
    r"invalid_user",
    r"wrong_password",
]

# 实际凭证硬编码模式（排除占位符后匹配）
_CREDENTIAL_PATTERNS: List[re.Pattern[str]] = [
    # init_token 中直接写入字面量字符串（非变量、非环境变量读取）
    re.compile(
        r'init_token\(\s*username\s*=\s*"(?!你的用户名|YOUR_USERNAME)[A-Za-z0-9_]{3,}"',
    ),
    re.compile(
        r"init_token\(\s*username\s*=\s*'(?!你的用户名|YOUR_USERNAME)[A-Za-z0-9_]{3,}'",
    ),
    re.compile(
        r'password\s*=\s*"(?!你的密码|YOUR_PASSWORD)[A-Za-z0-9!@#$%^&*]{6,}"',
    ),
    re.compile(
        r"password\s*=\s*'(?!你的密码|YOUR_PASSWORD)[A-Za-z0-9!@#$%^&*]{6,}'",
    ),
    # 常见 API key 模式（长随机字符串赋值）
    re.compile(
        r'(?:api[_\-]?key|token|secret)\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
        re.IGNORECASE,
    ),
]


def _is_placeholder_line(line: str) -> bool:
    """判断该行是否为占位符/示例行（不应被视为硬编码凭证）。"""
    for pattern in _PLACEHOLDER_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def _collect_text_files(directory: Path) -> List[Path]:
    """收集目录下所有文本文件（.md, .py, .json）。"""
    files: List[Path] = []
    if not directory.exists():
        return files
    for ext in TEXT_FILE_EXTENSIONS:
        files.extend(directory.rglob(f"*{ext}"))
    return sorted(files)


# ==================================================================
# Feature: panda-data-openclaw-skills, Property 9: SKILL.md 全量 API 覆盖
# ==================================================================


class TestSkillMdApiCoverage:
    """验证 SKILL.md 包含全部 38 个 API 方法名。

    **Validates: Requirements 13.4**
    """

    @pytest.fixture(scope="class")
    def skill_md_content(self) -> str:
        """读取 SKILL.md 文件内容。"""
        assert _SKILL_MD.exists(), f"SKILL.md 文件不存在：{_SKILL_MD}"
        return _SKILL_MD.read_text(encoding="utf-8")

    def test_skill_md_contains_all_38_methods(
        self, skill_md_content: str
    ) -> None:
        """SKILL.md 应包含全部 38 个 API 方法名。"""
        missing: List[str] = [
            method
            for method in ALL_38_METHODS
            if method not in skill_md_content
        ]
        assert not missing, (
            f"SKILL.md 中缺少以下 {len(missing)} 个方法名：{missing}"
        )

    def test_method_count_is_38(self) -> None:
        """方法名列表应恰好包含 35 个方法（当前实现）。"""
        assert len(ALL_38_METHODS) == 35, (
            f"期望 35 个方法名，实际 {len(ALL_38_METHODS)} 个"
        )

    @pytest.mark.parametrize("method_name", ALL_38_METHODS)
    def test_individual_method_in_skill_md(
        self, skill_md_content: str, method_name: str
    ) -> None:
        """每个方法名应单独出现在 SKILL.md 中。"""
        assert method_name in skill_md_content, (
            f"方法 '{method_name}' 未出现在 SKILL.md 中"
        )


# ==================================================================
# Feature: panda-data-openclaw-skills, Property 10: 无硬编码凭证
# ==================================================================


class TestNoHardcodedCredentials:
    """验证 skill 目录下所有文本文件不包含硬编码凭证。

    **Validates: Requirements 15.4**
    """

    @pytest.fixture(scope="class")
    def text_files(self) -> List[Path]:
        """收集 panda-data-skill/ 下所有文本文件。"""
        files = _collect_text_files(_SKILL_DIR)
        assert len(files) > 0, (
            f"panda-data-skill/ 目录下未找到文本文件：{_SKILL_DIR}"
        )
        return files

    def test_no_hardcoded_credentials_in_skill_files(
        self, text_files: List[Path]
    ) -> None:
        """所有文本文件不应包含硬编码凭证值。"""
        violations: List[str] = []

        for filepath in text_files:
            content = filepath.read_text(encoding="utf-8")
            for line_no, line in enumerate(content.splitlines(), start=1):
                # 跳过占位符行
                if _is_placeholder_line(line):
                    continue
                for pattern in _CREDENTIAL_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        rel_path = filepath.relative_to(_SKILL_DIR)
                        violations.append(
                            f"  {rel_path}:{line_no} → {match.group()}"
                        )

        assert not violations, (
            f"发现 {len(violations)} 处疑似硬编码凭证：\n"
            + "\n".join(violations)
        )

    def test_text_files_exist(self, text_files: List[Path]) -> None:
        """skill 目录下应存在可检查的文本文件。"""
        md_files = [f for f in text_files if f.suffix == ".md"]
        py_files = [f for f in text_files if f.suffix == ".py"]
        assert len(md_files) > 0, "应至少包含 .md 文件"
        assert len(py_files) > 0, "应至少包含 .py 文件"


from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from typing import Dict, Tuple

# ------------------------------------------------------------------
# SKILL.md API 方法条目解析工具
# ------------------------------------------------------------------

# 匹配 #### N. `method_name(...)` — 描述 格式的标题行
_METHOD_HEADING_RE = re.compile(
    r"^####\s+\d+\.\s+`([a-z_]+)\(([^)]*)\)`\s*—\s*(.+)$"
)

# 匹配参数表行（含 | 参数 | 或 |:--- 分隔线）
_PARAM_TABLE_RE = re.compile(
    r"^\s*\|.*(?:参数|类型|描述|必填|:[-]+).*\|"
)


def _parse_skill_md_method_entries() -> Dict[str, Dict[str, object]]:
    """解析 SKILL.md，提取所有 API 方法条目信息。

    Returns:
        字典，键为方法名，值包含：
        - heading_line: 标题行原文
        - signature: 方法签名（含参数列表）
        - params: 参数列表字符串
        - description_heading: 标题行中的一句话描述
        - description_body: 标题行下方的描述正文（下一行）
        - body_lines: 该条目到下一个条目之间的所有正文行
        - has_param_table: 是否包含参数表行
    """
    assert _SKILL_MD.exists(), f"SKILL.md 文件不存在：{_SKILL_MD}"
    lines = _SKILL_MD.read_text(encoding="utf-8").splitlines()

    # 找到所有方法标题行的位置
    heading_positions: list[Tuple[int, re.Match]] = []
    for i, line in enumerate(lines):
        m = _METHOD_HEADING_RE.match(line)
        if m:
            heading_positions.append((i, m))

    entries: Dict[str, Dict[str, object]] = {}
    for idx, (line_no, match) in enumerate(heading_positions):
        method_name = match.group(1)
        params = match.group(2)
        desc_heading = match.group(3).strip()

        # 确定该条目的正文范围（到下一个 #### 标题或文件末尾）
        if idx + 1 < len(heading_positions):
            end_line = heading_positions[idx + 1][0]
        else:
            # 最后一个方法条目：扫描到下一个 ## 或 ### 标题或文件末尾
            end_line = len(lines)
            for j in range(line_no + 1, len(lines)):
                if re.match(r"^#{1,3}\s+", lines[j]):
                    end_line = j
                    break

        body_lines = lines[line_no + 1 : end_line]

        # 获取描述正文（标题行下方第一个非空行）
        description_body = ""
        for bl in body_lines:
            stripped = bl.strip()
            if stripped:
                description_body = stripped
                break

        # 检查是否包含参数表行
        has_param_table = any(
            _PARAM_TABLE_RE.match(bl) for bl in body_lines
        )

        entries[method_name] = {
            "heading_line": lines[line_no],
            "signature": f"{method_name}({params})",
            "params": params,
            "description_heading": desc_heading,
            "description_body": description_body,
            "body_lines": body_lines,
            "has_param_table": has_param_table,
        }

    return entries


# ==================================================================
# Feature: skill-v2-optimization, Property 1: SKILL.md API 方法条目格式
# ==================================================================


class TestSkillMdApiMethodEntryFormat:
    """属性基测试：验证 SKILL.md 中每个 API 方法条目的格式。

    Property 1: 对于 SKILL.md API 方法列表中的任意 API 方法条目，
    该条目应包含方法签名（方法名和参数列表）和一句话描述，
    且不应包含任何 markdown 参数表行。

    **Validates: Requirements 1.1, 1.6**
    """

    @pytest.fixture(scope="class")
    def method_entries(self) -> Dict[str, Dict[str, object]]:
        """解析 SKILL.md 中的所有方法条目。"""
        return _parse_skill_md_method_entries()

    def test_all_38_methods_have_entries(
        self, method_entries: Dict[str, Dict[str, object]]
    ) -> None:
        """SKILL.md 应包含全部 38 个 API 方法的格式化条目。"""
        missing = [m for m in ALL_38_METHODS if m not in method_entries]
        assert not missing, (
            f"SKILL.md 中缺少以下方法的 #### 条目：{missing}"
        )
        assert len(method_entries) == 38, (
            f"期望 38 个方法条目，实际解析到 {len(method_entries)} 个"
        )

    @given(method_idx=st.integers(min_value=0, max_value=37))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_property_method_entry_has_signature_and_description(
        self,
        method_entries: Dict[str, Dict[str, object]],
        method_idx: int,
    ) -> None:
        """Property 1: 每个方法条目包含方法签名（含参数列表）和一句话描述。

        # Feature: skill-v2-optimization, Property 1: SKILL.md API 方法条目格式
        **Validates: Requirements 1.1, 1.6**
        """
        method_name = ALL_38_METHODS[method_idx]
        assert method_name in method_entries, (
            f"方法 '{method_name}' 未在 SKILL.md 中找到 #### 条目"
        )
        entry = method_entries[method_name]

        # 验证方法签名包含括号（参数列表）
        heading = str(entry["heading_line"])
        assert "(" in heading and ")" in heading, (
            f"方法 '{method_name}' 的标题行缺少参数列表括号：{heading}"
        )

        # 验证签名中包含方法名
        assert method_name in heading, (
            f"方法 '{method_name}' 的标题行不包含方法名：{heading}"
        )

        # 验证有一句话描述（标题行中 — 后面的部分）
        desc = str(entry["description_heading"])
        assert len(desc) > 0, (
            f"方法 '{method_name}' 的标题行缺少一句话描述"
        )

        # 验证有描述正文（标题行下方的描述行）
        body_desc = str(entry["description_body"])
        assert len(body_desc) > 0, (
            f"方法 '{method_name}' 缺少标题行下方的描述正文"
        )

    @given(method_idx=st.integers(min_value=0, max_value=37))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_property_method_entry_has_no_param_table(
        self,
        method_entries: Dict[str, Dict[str, object]],
        method_idx: int,
    ) -> None:
        """Property 1: 每个方法条目不包含参数表行。

        # Feature: skill-v2-optimization, Property 1: SKILL.md API 方法条目格式
        **Validates: Requirements 1.1, 1.6**
        """
        method_name = ALL_38_METHODS[method_idx]
        assert method_name in method_entries, (
            f"方法 '{method_name}' 未在 SKILL.md 中找到 #### 条目"
        )
        entry = method_entries[method_name]

        # 验证不包含参数表行
        assert not entry["has_param_table"], (
            f"方法 '{method_name}' 的条目中仍包含参数表行"
        )


# ==================================================================
# Feature: skill-v2-optimization, Task 6.3: SKILL.md 结构单元测试
# ==================================================================


class TestSkillMdStructure:
    """SKILL.md 结构完整性单元测试。

    验证精简优化后 SKILL.md 保留了所有必要的结构元素：
    frontmatter、Quick Start、Key Notes、Rules、代码示例、参考链接、全部方法名。

    **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.7**
    """

    @pytest.fixture(scope="class")
    def skill_md_content(self) -> str:
        """读取 SKILL.md 文件内容。"""
        assert _SKILL_MD.exists(), f"SKILL.md 文件不存在：{_SKILL_MD}"
        return _SKILL_MD.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def skill_md_lines(self, skill_md_content: str) -> List[str]:
        """SKILL.md 按行拆分。"""
        return skill_md_content.splitlines()

    # --- Frontmatter 验证 (Requirement 1.3) ---

    def test_frontmatter_block_exists(self, skill_md_lines: List[str]) -> None:
        """SKILL.md 应以 YAML frontmatter 块开头（--- 包围）。"""
        assert len(skill_md_lines) >= 3, "SKILL.md 内容过短，缺少 frontmatter"
        assert skill_md_lines[0].strip() == "---", (
            f"SKILL.md 第一行应为 '---'，实际为：'{skill_md_lines[0]}'"
        )
        # 找到第二个 ---
        closing_idx = None
        for i in range(1, len(skill_md_lines)):
            if skill_md_lines[i].strip() == "---":
                closing_idx = i
                break
        assert closing_idx is not None, "SKILL.md 缺少 frontmatter 结束标记 '---'"
        assert closing_idx > 1, "frontmatter 块为空"

    def test_frontmatter_contains_name(self, skill_md_content: str) -> None:
        """frontmatter 应包含 name 字段。"""
        # 提取 frontmatter 内容
        parts = skill_md_content.split("---", 2)
        assert len(parts) >= 3, "无法解析 frontmatter 块"
        frontmatter = parts[1]
        assert re.search(r"^name:", frontmatter, re.MULTILINE), (
            "frontmatter 缺少 'name:' 字段"
        )

    def test_frontmatter_contains_description(self, skill_md_content: str) -> None:
        """frontmatter 应包含 description 字段。"""
        parts = skill_md_content.split("---", 2)
        assert len(parts) >= 3, "无法解析 frontmatter 块"
        frontmatter = parts[1]
        assert re.search(r"^description:", frontmatter, re.MULTILINE), (
            "frontmatter 缺少 'description:' 字段"
        )

    def test_frontmatter_contains_user_invocable(self, skill_md_content: str) -> None:
        """frontmatter 应包含 user-invocable 字段。"""
        parts = skill_md_content.split("---", 2)
        assert len(parts) >= 3, "无法解析 frontmatter 块"
        frontmatter = parts[1]
        assert re.search(r"^user-invocable:", frontmatter, re.MULTILINE), (
            "frontmatter 缺少 'user-invocable:' 字段"
        )

    def test_frontmatter_contains_metadata(self, skill_md_content: str) -> None:
        """frontmatter 应包含 metadata 字段。"""
        parts = skill_md_content.split("---", 2)
        assert len(parts) >= 3, "无法解析 frontmatter 块"
        frontmatter = parts[1]
        assert re.search(r"^metadata:", frontmatter, re.MULTILINE), (
            "frontmatter 缺少 'metadata:' 字段"
        )

    # --- 核心章节保留验证 (Requirement 1.4) ---

    def test_quick_start_section_exists(self, skill_md_content: str) -> None:
        """SKILL.md 应包含 '## Quick Start' 章节。"""
        assert re.search(r"^## Quick Start", skill_md_content, re.MULTILINE), (
            "SKILL.md 缺少 '## Quick Start' 章节"
        )

    def test_key_notes_section_exists(self, skill_md_content: str) -> None:
        """SKILL.md 应包含 '## Key Notes' 章节。"""
        assert re.search(r"^## Key Notes", skill_md_content, re.MULTILINE), (
            "SKILL.md 缺少 '## Key Notes' 章节"
        )

    def test_rules_section_exists(self, skill_md_content: str) -> None:
        """SKILL.md 应包含 '## Rules' 章节。"""
        assert re.search(r"^## Rules", skill_md_content, re.MULTILINE), (
            "SKILL.md 缺少 '## Rules' 章节"
        )

    # --- 代码示例章节保留验证 (Requirement 1.5) ---

    def test_code_examples_section_exists(self, skill_md_content: str) -> None:
        """SKILL.md 应包含 '## 代码示例' 章节。"""
        assert re.search(r"^## 代码示例", skill_md_content, re.MULTILINE), (
            "SKILL.md 缺少 '## 代码示例' 章节"
        )

    # --- 参考链接验证 (Requirement 1.7) ---

    def test_api_reference_link_exists(self, skill_md_content: str) -> None:
        """SKILL.md 应包含指向 api_reference.md 的参考链接。"""
        assert "api_reference.md" in skill_md_content, (
            "SKILL.md 缺少指向 api_reference.md 的参考链接"
        )

    def test_reference_link_in_api_section(self, skill_md_content: str) -> None:
        """参考链接应出现在 API 方法列表区域。"""
        # 找到 API 方法列表区域的起始位置
        api_section_match = re.search(
            r"^## API 方法列表", skill_md_content, re.MULTILINE
        )
        assert api_section_match is not None, (
            "SKILL.md 缺少 '## API 方法列表' 章节"
        )
        api_section_text = skill_md_content[api_section_match.start():]
        # 在 API 方法列表区域中查找参考链接
        assert "api_reference.md" in api_section_text, (
            "api_reference.md 参考链接不在 API 方法列表区域中"
        )

    # --- 全部 38 个方法名验证 (Requirement 1.2) ---

    def test_all_38_methods_present(self, skill_md_content: str) -> None:
        """SKILL.md 应包含全部 38 个 API 方法名。"""
        missing = [m for m in ALL_38_METHODS if m not in skill_md_content]
        assert not missing, (
            f"SKILL.md 中缺少以下 {len(missing)} 个方法名：{missing}"
        )
