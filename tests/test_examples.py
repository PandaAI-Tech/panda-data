"""示例脚本验证测试。

验证 panda-data-skill/scripts/ 下新增的示例脚本：
1. 语法正确性（py_compile）
2. 错误处理示例包含必要的 try-except 模式

Validates: Requirements 3.1, 3.6
"""

import py_compile
from pathlib import Path

import pytest

# 项目根目录（panda-data-tools 的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "panda-data-skill" / "scripts"

# 新增的示例脚本列表
NEW_SCRIPTS = [
    "error_handling_example.py",
    "cache_example.py",
    "export_example.py",
]


# ---------------------------------------------------------------------------
# 1. 语法正确性验证
# ---------------------------------------------------------------------------


class TestScriptSyntax:
    """验证所有新增示例脚本无语法错误。"""

    @pytest.mark.parametrize("script_name", NEW_SCRIPTS)
    def test_script_compiles(self, script_name: str) -> None:
        """脚本应能通过 py_compile 编译，无语法错误。"""
        script_path = SCRIPTS_DIR / script_name
        assert script_path.exists(), f"Script not found: {script_path}"
        # py_compile.compile raises py_compile.PyCompileError on syntax error
        py_compile.compile(str(script_path), doraise=True)


# ---------------------------------------------------------------------------
# 2. 错误处理示例内容验证 (Requirements 3.1, 3.6)
# ---------------------------------------------------------------------------


class TestErrorHandlingExample:
    """验证 error_handling_example.py 包含必要的异常处理模式。"""

    @pytest.fixture()
    def content(self) -> str:
        path = SCRIPTS_DIR / "error_handling_example.py"
        assert path.exists(), f"error_handling_example.py not found at {path}"
        return path.read_text(encoding="utf-8")

    def test_contains_try_except(self, content: str) -> None:
        """脚本应包含 try-except 块。"""
        assert "try:" in content, "Should contain 'try:' block"
        assert "except" in content, "Should contain 'except' block"

    def test_contains_error_format(self, content: str) -> None:
        """脚本应包含统一错误格式 'API 调用失败'。"""
        assert "API 调用失败" in content, (
            "Should contain error format pattern 'API 调用失败'"
        )

    def test_demonstrates_retry_pattern(self, content: str) -> None:
        """脚本应演示重试模式。"""
        has_retry = "retry" in content.lower() or "重试" in content
        assert has_retry, (
            "Should demonstrate retry pattern (contain 'retry' or '重试')"
        )
