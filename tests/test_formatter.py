"""formatter.py 属性基测试（hypothesis）。

使用 hypothesis 对 format_result 和 safe_call 进行属性基测试，验证
DataFrame 格式化与截断、字符串值直接透传和异常捕获与结构化错误三个核心属性。
"""

from unittest.mock import patch, MagicMock

import pandas as pd
from hypothesis import given, settings, assume
from hypothesis import strategies as st

import panda_tools.credential as credential_module
from panda_tools.formatter import format_result, safe_call


# ---------------------------------------------------------------------------
# 辅助策略
# ---------------------------------------------------------------------------

# 生成列名策略：简单 ASCII 标识符
column_names = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz_",
    min_size=1,
    max_size=8,
)

# 生成单元格值策略
cell_values = st.one_of(
    st.integers(min_value=-10000, max_value=10000),
    st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    st.text(min_size=0, max_size=10),
)


def build_dataframe(num_rows: int, num_cols: int, cols, vals):
    """根据给定参数构建 DataFrame。"""
    data = {}
    for i in range(num_cols):
        col_name = cols[i]
        col_data = [vals[i * num_rows + j] for j in range(num_rows)]
        data[col_name] = col_data
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Property 5: DataFrame 格式化与截断
# Feature: panda-data-openclaw-skills, Property 5: DataFrame 格式化与截断
# **Validates: Requirements 3.4, 10.1, 10.2**
# ---------------------------------------------------------------------------

@given(data=st.data())
@settings(max_examples=100)
def test_dataframe_format_and_truncation(data) -> None:
    """对于任意 pandas DataFrame，format_result 应满足：
    (a) 空 DataFrame 或 None 返回"未查询到数据"；
    (b) 行数 ≤ 20 的 DataFrame 返回包含所有行数据的字符串；
    (c) 行数 > 20 的 DataFrame 返回仅包含前 20 行数据的字符串，且附带总行数提示。
    """
    # 选择测试场景：None、空 DataFrame、≤20 行、>20 行
    scenario = data.draw(st.sampled_from(["none", "empty", "small", "large"]))

    if scenario == "none":
        result = format_result(None)
        assert result == "未查询到数据"

    elif scenario == "empty":
        num_cols = data.draw(st.integers(min_value=0, max_value=5))
        if num_cols == 0:
            df = pd.DataFrame()
        else:
            cols = data.draw(
                st.lists(column_names, min_size=num_cols, max_size=num_cols, unique=True)
            )
            df = pd.DataFrame({c: pd.Series(dtype="object") for c in cols})
        result = format_result(df)
        assert result == "未查询到数据"

    elif scenario == "small":
        num_rows = data.draw(st.integers(min_value=1, max_value=20))
        num_cols = data.draw(st.integers(min_value=1, max_value=4))
        cols = data.draw(
            st.lists(column_names, min_size=num_cols, max_size=num_cols, unique=True)
        )
        vals = data.draw(
            st.lists(cell_values, min_size=num_rows * num_cols, max_size=num_rows * num_cols)
        )
        df = build_dataframe(num_rows, num_cols, cols, vals)
        result = format_result(df)

        # 应包含所有行数据 — 通过检查 to_string 输出一致来验证
        expected = df.to_string(index=False)
        assert result == expected

    else:  # large
        num_rows = data.draw(st.integers(min_value=21, max_value=50))
        num_cols = data.draw(st.integers(min_value=1, max_value=4))
        cols = data.draw(
            st.lists(column_names, min_size=num_cols, max_size=num_cols, unique=True)
        )
        vals = data.draw(
            st.lists(cell_values, min_size=num_rows * num_cols, max_size=num_rows * num_cols)
        )
        df = build_dataframe(num_rows, num_cols, cols, vals)
        result = format_result(df)

        # 应仅包含前 20 行
        truncated = df.head(20).to_string(index=False)
        assert truncated in result
        # 应附带总行数提示
        assert str(num_rows) in result
        assert "20" in result


# ---------------------------------------------------------------------------
# Property 6: 字符串值直接透传
# Feature: panda-data-openclaw-skills, Property 6: 字符串值直接透传
# **Validates: Requirements 10.3**
# ---------------------------------------------------------------------------

@given(s=st.text(min_size=1))
@settings(max_examples=100)
def test_string_passthrough(s: str) -> None:
    """对于任意非空字符串值，format_result 应原样返回该字符串，不做任何修改。"""
    result = format_result(s)
    assert result == s


# ---------------------------------------------------------------------------
# Property 7: 异常捕获与结构化错误
# Feature: panda-data-openclaw-skills, Property 7: 异常捕获与结构化错误
# **Validates: Requirements 10.4**
# ---------------------------------------------------------------------------

exception_types = st.sampled_from([
    ValueError, TypeError, ConnectionError, RuntimeError,
    OSError, PermissionError, TimeoutError,
])


@given(
    exc_type=exception_types,
    exc_msg=st.text(min_size=1).filter(lambda s: s.strip() != ""),
)
@settings(max_examples=100)
def test_exception_capture_and_structured_error(exc_type, exc_msg) -> None:
    """对于任意异常类型和消息，当函数抛出异常时，safe_call 返回的字符串
    应同时包含异常的类型名称和异常的消息文本。"""

    # 重置凭证模块标志位
    credential_module._initialized = False

    def failing_func(**kwargs):
        raise exc_type(exc_msg)

    with patch("panda_tools.formatter.CredentialManager") as mock_cm:
        # Mock ensure_initialized 避免真实认证
        mock_cm.ensure_initialized.return_value = True

        result = safe_call(failing_func)

        # 返回的错误信息应包含异常类型名称
        assert exc_type.__name__ in result
        # 返回的错误信息应包含异常消息内容
        assert exc_msg in result
