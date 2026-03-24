"""DataExporter 属性基测试（hypothesis）。

使用 hypothesis 对 export_data 的导出往返一致性进行属性基测试。
"""

import tempfile
import os

import duckdb
import pandas as pd
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from panda_tools.exporter import export_data


# ---------------------------------------------------------------------------
# 辅助策略
# ---------------------------------------------------------------------------

# 生成合法列名：简单 ASCII 标识符
column_names = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=2,
    max_size=8,
)

# 字符串值策略：使用字母前缀确保不会被 CSV 读回时误解析为数值或 NaN
# （CSV 格式天然丢失类型信息，纯数字字符串如 "00" 会被读回为整数 0）
# （pandas read_csv 会将 "null", "na", "nan" 等解析为 NaN）
_NA_STRINGS = {"null", "na", "nan", "none", "n", ""}
string_values = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=2,
    max_size=15,
).filter(lambda s: s.lower() not in _NA_STRINGS)

# 数值策略：整数和有限浮点数
numeric_values = st.one_of(
    st.integers(min_value=-100000, max_value=100000),
    st.floats(
        min_value=-1e6,
        max_value=1e6,
        allow_nan=False,
        allow_infinity=False,
    ),
)


# ---------------------------------------------------------------------------
# Property 5: 数据导出往返一致性 (Export Round-Trip)
# Feature: skill-v2-optimization, Property 5: 数据导出往返一致性 (Export Round-Trip)
# **Validates: Requirements 4.2, 4.3, 4.4**
# ---------------------------------------------------------------------------


def _normalize_value(val):
    """归一化值用于比较：将所有值转为字符串后比较。"""
    if pd.isna(val):
        return ""
    return str(val)


def _assert_dataframes_equivalent(original: pd.DataFrame, readback: pd.DataFrame, fmt: str):
    """断言两个 DataFrame 在类型归一化后等价。"""
    # 相同列集合
    assert set(readback.columns) == set(original.columns), (
        f"[{fmt}] 列不一致: 期望 {set(original.columns)}, 实际 {set(readback.columns)}"
    )

    # 相同行数
    assert len(readback) == len(original), (
        f"[{fmt}] 行数不一致: 期望 {len(original)}, 实际 {len(readback)}"
    )

    # 逐列逐值比较（类型归一化后）
    for col in original.columns:
        for idx in range(len(original)):
            orig_val = original[col].iloc[idx]
            read_val = readback[col].iloc[idx]

            if isinstance(orig_val, float):
                # 浮点数：容差比较
                read_float = float(read_val)
                assert abs(orig_val - read_float) < 1e-4, (
                    f"[{fmt}] 列 {col} 行 {idx} 浮点值不一致: {orig_val} vs {read_float}"
                )
            else:
                # 其他类型：字符串化比较
                assert _normalize_value(orig_val) == _normalize_value(read_val), (
                    f"[{fmt}] 列 {col} 行 {idx} 值不一致: {orig_val!r} vs {read_val!r}"
                )


@given(data=st.data())
@settings(max_examples=100, deadline=None)
def test_export_round_trip(data) -> None:
    """对于任意有效的 pandas DataFrame（含字符串和数值列），以及 csv/excel/duckdb
    三种导出格式，导出后读回数据应等价（类型归一化后）：相同列、相同行数、相同值。
    """
    # 生成随机列配置
    num_str_cols = data.draw(st.integers(min_value=0, max_value=3), label="num_str_cols")
    num_num_cols = data.draw(st.integers(min_value=0, max_value=3), label="num_num_cols")
    total_cols = num_str_cols + num_num_cols
    assume(total_cols >= 1)

    num_rows = data.draw(st.integers(min_value=1, max_value=20), label="num_rows")

    # 生成唯一列名
    col_names = data.draw(
        st.lists(column_names, min_size=total_cols, max_size=total_cols, unique=True),
        label="col_names",
    )

    # 构建 DataFrame
    df_data = {}
    for i in range(num_str_cols):
        col_vals = data.draw(
            st.lists(string_values, min_size=num_rows, max_size=num_rows),
            label=f"str_col_{i}",
        )
        df_data[col_names[i]] = col_vals

    for i in range(num_num_cols):
        col_vals = data.draw(
            st.lists(numeric_values, min_size=num_rows, max_size=num_rows),
            label=f"num_col_{i}",
        )
        df_data[col_names[num_str_cols + i]] = col_vals

    df = pd.DataFrame(df_data)

    # 选择导出格式
    fmt = data.draw(st.sampled_from(["csv", "excel", "duckdb"]), label="format")

    table_name = "exported_data"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 构建输出路径
        if fmt == "csv":
            out_path = os.path.join(tmp_dir, "output.csv")
        elif fmt == "excel":
            out_path = os.path.join(tmp_dir, "output.xlsx")
        else:
            out_path = os.path.join(tmp_dir, "output.duckdb")

        # 导出
        result_msg = export_data(df, out_path, format=fmt, table_name=table_name)
        assert "已导出" in result_msg, f"[{fmt}] 导出失败: {result_msg}"

        # 读回
        if fmt == "csv":
            readback = pd.read_csv(out_path, encoding="utf-8-sig")
        elif fmt == "excel":
            readback = pd.read_excel(out_path)
        else:
            conn = duckdb.connect(out_path)
            try:
                readback = conn.execute(f'SELECT * FROM "{table_name}"').fetchdf()
            finally:
                conn.close()

        # 验证等价性
        _assert_dataframes_equivalent(df, readback, fmt)


# ---------------------------------------------------------------------------
# Property 6: 导出成功消息包含路径和行数
# Feature: skill-v2-optimization, Property 6: 导出成功消息包含路径和行数
# **Validates: Requirements 4.5**
# ---------------------------------------------------------------------------


@given(data=st.data())
@settings(max_examples=100, deadline=None)
def test_export_success_message_contains_path_and_row_count(data) -> None:
    """对于任意非空 DataFrame 的成功导出操作，返回的成功消息字符串应包含
    输出文件路径和导出行数（整数的字符串表示）。
    """
    # 生成随机列配置（至少 1 列）
    num_str_cols = data.draw(st.integers(min_value=0, max_value=3), label="num_str_cols")
    num_num_cols = data.draw(st.integers(min_value=0, max_value=3), label="num_num_cols")
    total_cols = num_str_cols + num_num_cols
    assume(total_cols >= 1)

    # 非空 DataFrame：至少 1 行
    num_rows = data.draw(st.integers(min_value=1, max_value=20), label="num_rows")

    # 生成唯一列名
    col_names = data.draw(
        st.lists(column_names, min_size=total_cols, max_size=total_cols, unique=True),
        label="col_names",
    )

    # 构建 DataFrame
    df_data = {}
    for i in range(num_str_cols):
        col_vals = data.draw(
            st.lists(string_values, min_size=num_rows, max_size=num_rows),
            label=f"str_col_{i}",
        )
        df_data[col_names[i]] = col_vals

    for i in range(num_num_cols):
        col_vals = data.draw(
            st.lists(numeric_values, min_size=num_rows, max_size=num_rows),
            label=f"num_col_{i}",
        )
        df_data[col_names[num_str_cols + i]] = col_vals

    df = pd.DataFrame(df_data)

    # 选择导出格式
    fmt = data.draw(st.sampled_from(["csv", "excel", "duckdb"]), label="format")

    with tempfile.TemporaryDirectory() as tmp_dir:
        if fmt == "csv":
            out_path = os.path.join(tmp_dir, "output.csv")
        elif fmt == "excel":
            out_path = os.path.join(tmp_dir, "output.xlsx")
        else:
            out_path = os.path.join(tmp_dir, "output.duckdb")

        result_msg = export_data(df, out_path, format=fmt)

        # 验证消息不是错误消息
        assert not result_msg.startswith("导出失败"), f"导出应成功但失败了: {result_msg}"

        # 验证消息包含文件路径
        assert out_path in result_msg, (
            f"[{fmt}] 成功消息应包含文件路径 '{out_path}'，实际消息: {result_msg}"
        )

        # 验证消息包含导出行数（整数的字符串表示）
        row_count_str = str(len(df))
        assert row_count_str in result_msg, (
            f"[{fmt}] 成功消息应包含行数 '{row_count_str}'，实际消息: {result_msg}"
        )


# ---------------------------------------------------------------------------
# Property 7: 导出失败返回结构化错误消息
# Feature: skill-v2-optimization, Property 7: 导出失败返回结构化错误消息
# **Validates: Requirements 4.7**
# ---------------------------------------------------------------------------

import re
import platform


# 构建无效路径策略：根据操作系统选择一定会触发 OSError 的路径
def _invalid_paths_for_format(fmt: str) -> list[str]:
    """返回一组对于给定格式一定会导致写入失败的路径。"""
    if platform.system() == "Linux":
        base = "/proc/nonexistent/deep/path"
    else:
        # macOS / Windows fallback
        base = "/nonexistent_dir_xyz_no_access/deep/nested"
    ext_map = {"csv": ".csv", "excel": ".xlsx", "duckdb": ".duckdb"}
    ext = ext_map.get(fmt, ".csv")
    return [f"{base}/output{ext}"]


# 错误消息正则：导出失败：{ErrorType}: {message}
# ErrorType 是合法的 Python 异常类名（字母数字下划线，首字母大写）
_ERROR_MSG_RE = re.compile(r"^导出失败：([A-Z]\w*Error|[A-Z]\w*Exception|ValueError|OSError|PermissionError|FileNotFoundError|ImportError): .+")


@given(
    fmt=st.sampled_from(["csv", "excel", "duckdb"]),
    data=st.data(),
)
@settings(max_examples=100, deadline=None)
def test_export_failure_returns_structured_error_message(fmt, data) -> None:
    """对于任意导出操作失败（如无效路径），返回的错误消息应匹配
    "导出失败：{ErrorType}: {message}" 格式，其中 ErrorType 是合法的 Python 异常类名。
    """
    # 构建一个简单的 DataFrame
    num_rows = data.draw(st.integers(min_value=1, max_value=5), label="num_rows")
    df = pd.DataFrame({"col_a": [f"val_{i}" for i in range(num_rows)]})

    # 使用无效路径触发失败
    invalid_paths = _invalid_paths_for_format(fmt)
    path = data.draw(st.sampled_from(invalid_paths), label="invalid_path")

    result_msg = export_data(df, path, format=fmt)

    # 验证错误消息以 "导出失败：" 开头
    assert result_msg.startswith("导出失败："), (
        f"[{fmt}] 错误消息应以 '导出失败：' 开头，实际: {result_msg}"
    )

    # 验证错误消息匹配 "导出失败：{ErrorType}: {message}" 格式
    # 拆分验证：冒号分隔至少 3 部分（"导出失败"、ErrorType、message）
    parts = result_msg.split("：", 2)  # 使用全角冒号分割
    assert len(parts) >= 2, (
        f"[{fmt}] 错误消息格式不正确，应包含至少两个全角冒号分隔部分，实际: {result_msg}"
    )

    # ErrorType 部分（parts[1]）应包含 ": message" 用半角冒号分隔
    error_and_msg = parts[1] if len(parts) == 2 else parts[1]
    # 完整的 ErrorType: message 部分
    error_detail = result_msg[len("导出失败："):]
    colon_idx = error_detail.find(": ")
    assert colon_idx > 0, (
        f"[{fmt}] 错误详情应包含 ': ' 分隔 ErrorType 和 message，实际: {error_detail}"
    )

    error_type = error_detail[:colon_idx]
    message = error_detail[colon_idx + 2:]

    # ErrorType 应是合法的 Python 标识符（异常类名）
    assert error_type.isidentifier(), (
        f"[{fmt}] ErrorType 应是合法的 Python 标识符，实际: {error_type!r}"
    )

    # message 不应为空
    assert len(message) > 0, (
        f"[{fmt}] 错误消息的 message 部分不应为空"
    )


# ---------------------------------------------------------------------------
# Property 8: 导出自动创建目录
# Feature: skill-v2-optimization, Property 8: 导出自动创建目录
# **Validates: Requirements 4.6**
# ---------------------------------------------------------------------------

# 策略：生成随机嵌套目录段（1~4 层），每段为短 ASCII 名称
_dir_segment = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=1,
    max_size=8,
)

_nested_dir_path = st.lists(
    _dir_segment,
    min_size=1,
    max_size=4,
).map(lambda parts: os.path.join(*parts))


@given(
    nested_dir=_nested_dir_path,
    fmt=st.sampled_from(["csv", "excel", "duckdb"]),
    data=st.data(),
)
@settings(max_examples=100, deadline=None)
def test_export_auto_creates_directory(nested_dir, fmt, data) -> None:
    """对于任意不存在的嵌套目录路径，export_data 应自动创建目录并成功写入文件，
    而不是抛出 FileNotFoundError。
    """
    # 生成一个简单的 DataFrame
    num_rows = data.draw(st.integers(min_value=1, max_value=10), label="num_rows")
    df = pd.DataFrame({"col_a": [f"val_{i}" for i in range(num_rows)]})

    ext_map = {"csv": ".csv", "excel": ".xlsx", "duckdb": ".duckdb"}
    filename = f"output{ext_map[fmt]}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 构建嵌套目录路径（该目录尚不存在）
        target_dir = os.path.join(tmp_dir, nested_dir)
        out_path = os.path.join(target_dir, filename)

        # 确认目录确实不存在
        assert not os.path.exists(target_dir), (
            f"目标目录不应预先存在: {target_dir}"
        )

        # 导出
        result_msg = export_data(df, out_path, format=fmt)

        # 验证导出成功（非错误消息）
        assert not result_msg.startswith("导出失败"), (
            f"[{fmt}] 导出应成功但失败了: {result_msg}"
        )

        # 验证目录已自动创建
        assert os.path.isdir(target_dir), (
            f"[{fmt}] 目录应被自动创建: {target_dir}"
        )

        # 验证文件已成功写入（存在于磁盘上）
        assert os.path.isfile(out_path), (
            f"[{fmt}] 文件应成功写入: {out_path}"
        )


# ---------------------------------------------------------------------------
# 单元测试：DataExporter 边界情况
# ---------------------------------------------------------------------------

from unittest.mock import patch


class TestExportEmptyDataFrame:
    """测试空 DataFrame 导出。"""

    def test_empty_dataframe_export_csv(self, tmp_path):
        """空 DataFrame 导出 CSV 应成功，返回包含 0 行的成功消息。"""
        df = pd.DataFrame()
        out_path = str(tmp_path / "empty.csv")
        result = export_data(df, out_path, format="csv")
        assert "已导出 0 行数据到" in result
        assert out_path in result


class TestExportUnsupportedFormat:
    """测试不支持的导出格式。"""

    def test_unsupported_format_json(self):
        """使用不支持的格式 'json' 应返回结构化错误消息。"""
        df = pd.DataFrame({"a": [1, 2]})
        result = export_data(df, "/tmp/test.json", format="json")
        assert result == "导出失败：ValueError: 不支持的格式 'json'，可选：csv, excel, duckdb"


class TestExportOpenpyxlNotInstalled:
    """测试 openpyxl 未安装时的错误消息。"""

    def test_openpyxl_import_error(self, tmp_path):
        """openpyxl 未安装时，Excel 导出应返回结构化错误消息。"""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "openpyxl":
                raise ImportError("No module named 'openpyxl'")
            return real_import(name, *args, **kwargs)

        df = pd.DataFrame({"a": [1, 2]})
        out_path = str(tmp_path / "test.xlsx")

        with patch("builtins.__import__", side_effect=mock_import):
            result = export_data(df, out_path, format="excel")

        assert result == "导出失败：ImportError: Excel 导出需要安装 openpyxl"
