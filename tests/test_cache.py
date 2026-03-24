"""CacheManager 属性基测试（hypothesis）。

使用 hypothesis 对 CacheManager 的缓存存取往返一致性进行属性基测试。
"""

import tempfile

import pandas as pd
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from panda_tools.cache import CacheManager


# ---------------------------------------------------------------------------
# 辅助策略
# ---------------------------------------------------------------------------

# 生成合法列名：简单 ASCII 标识符，避免 DuckDB 保留字冲突
column_names = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=2,
    max_size=8,
)

# 生成单元格值策略：字符串和数值混合
string_values = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=0,
    max_size=20,
)

numeric_values = st.one_of(
    st.integers(min_value=-100000, max_value=100000),
    st.floats(
        min_value=-1e6,
        max_value=1e6,
        allow_nan=False,
        allow_infinity=False,
    ),
)

# 生成合法表名
table_names = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz_",
    min_size=2,
    max_size=16,
)


# ---------------------------------------------------------------------------
# Property 2: 缓存存取往返一致性 (Cache Save/Read Round-Trip)
# Feature: skill-v2-optimization, Property 2: 缓存存取往返一致性 (Cache Save/Read Round-Trip)
# **Validates: Requirements 2.2, 2.3**
# ---------------------------------------------------------------------------


@given(data=st.data())
@settings(max_examples=100, deadline=None)
def test_cache_save_read_round_trip(data) -> None:
    """对于任意有效的 pandas DataFrame（含字符串和数值列），以及任意合法表名，
    将 DataFrame 存入 CacheManager 后再读取（不带过滤条件），应返回等价数据：
    相同列、相同行数、相同值。
    """
    # 生成随机列配置
    num_str_cols = data.draw(st.integers(min_value=0, max_value=3), label="num_str_cols")
    num_num_cols = data.draw(st.integers(min_value=0, max_value=3), label="num_num_cols")
    total_cols = num_str_cols + num_num_cols
    assume(total_cols >= 1)

    num_rows = data.draw(st.integers(min_value=1, max_value=30), label="num_rows")

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

    # 生成表名
    tbl = data.draw(table_names, label="table_name")

    # 使用临时 DuckDB 文件（每次迭代独立）
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/test_cache.duckdb"
        cache = CacheManager(db_path=db_path)

        try:
            # 存入缓存
            result_msg = cache.save(tbl, df)
            assert "已缓存" in result_msg

            # 读取缓存
            read_df = cache.read(tbl)

            # 验证：相同列集合
            assert set(read_df.columns) == set(df.columns), (
                f"列不一致: 期望 {set(df.columns)}, 实际 {set(read_df.columns)}"
            )

            # 验证：相同行数
            assert len(read_df) == len(df), (
                f"行数不一致: 期望 {len(df)}, 实际 {len(read_df)}"
            )

            # 验证：相同值（按列对齐后逐列比较）
            for col in df.columns:
                original = df[col].tolist()
                cached = read_df[col].tolist()
                for idx, (orig_val, cached_val) in enumerate(zip(original, cached)):
                    if isinstance(orig_val, float):
                        # 浮点数比较容差
                        assert abs(orig_val - float(cached_val)) < 1e-6, (
                            f"列 {col} 行 {idx} 值不一致: {orig_val} vs {cached_val}"
                        )
                    else:
                        assert str(orig_val) == str(cached_val), (
                            f"列 {col} 行 {idx} 值不一致: {orig_val!r} vs {cached_val!r}"
                        )
        finally:
            cache.close()


# ---------------------------------------------------------------------------
# Property 3: 缓存过滤查询正确性 (Cache Read with Filters)
# Feature: skill-v2-optimization, Property 3: 缓存过滤查询正确性 (Cache Read with Filters)
# **Validates: Requirements 2.4**
# ---------------------------------------------------------------------------


@given(data=st.data())
@settings(max_examples=100, deadline=None)
def test_cache_read_with_filters(data) -> None:
    """对于任意缓存的 DataFrame 和任意有效的过滤条件（列名和数据中存在的值），
    调用 read(table_name, **filters) 应仅返回过滤列匹配过滤值的行，
    等价于 df[df[col] == value]。
    """
    # 生成随机列配置：至少 1 个字符串列用于过滤
    num_str_cols = data.draw(st.integers(min_value=1, max_value=3), label="num_str_cols")
    num_num_cols = data.draw(st.integers(min_value=0, max_value=2), label="num_num_cols")
    total_cols = num_str_cols + num_num_cols

    num_rows = data.draw(st.integers(min_value=2, max_value=30), label="num_rows")

    # 生成唯一列名
    col_names = data.draw(
        st.lists(column_names, min_size=total_cols, max_size=total_cols, unique=True),
        label="col_names",
    )

    # 使用有限值域的字符串，确保过滤条件能命中多行
    limited_string_values = st.sampled_from(["alpha", "beta", "gamma", "delta", "epsilon"])

    # 构建 DataFrame
    df_data = {}
    str_col_names = []
    for i in range(num_str_cols):
        col_vals = data.draw(
            st.lists(limited_string_values, min_size=num_rows, max_size=num_rows),
            label=f"str_col_{i}",
        )
        df_data[col_names[i]] = col_vals
        str_col_names.append(col_names[i])

    for i in range(num_num_cols):
        col_vals = data.draw(
            st.lists(
                st.integers(min_value=-1000, max_value=1000),
                min_size=num_rows,
                max_size=num_rows,
            ),
            label=f"num_col_{i}",
        )
        df_data[col_names[num_str_cols + i]] = col_vals

    df = pd.DataFrame(df_data)

    # 随机选择一个字符串列作为过滤列
    filter_col = data.draw(st.sampled_from(str_col_names), label="filter_col")

    # 从该列的实际值中随机选择一个作为过滤值
    actual_values = df[filter_col].unique().tolist()
    filter_value = data.draw(st.sampled_from(actual_values), label="filter_value")

    # 生成表名
    tbl = data.draw(table_names, label="table_name")

    # 计算期望结果：pandas 原生过滤
    expected_df = df[df[filter_col] == filter_value].reset_index(drop=True)

    # 使用临时 DuckDB 文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/test_cache.duckdb"
        cache = CacheManager(db_path=db_path)

        try:
            # 存入缓存
            result_msg = cache.save(tbl, df)
            assert "已缓存" in result_msg

            # 带过滤条件读取
            filtered_df = cache.read(tbl, **{filter_col: filter_value})

            # 验证：相同列集合
            assert set(filtered_df.columns) == set(df.columns), (
                f"列不一致: 期望 {set(df.columns)}, 实际 {set(filtered_df.columns)}"
            )

            # 验证：行数与 pandas 过滤结果一致
            assert len(filtered_df) == len(expected_df), (
                f"过滤后行数不一致: 期望 {len(expected_df)}, 实际 {len(filtered_df)}"
            )

            # 验证：过滤列的所有值都等于过滤值
            if len(filtered_df) > 0:
                for val in filtered_df[filter_col].tolist():
                    assert str(val) == str(filter_value), (
                        f"过滤列 {filter_col} 包含非预期值: {val!r}, 期望 {filter_value!r}"
                    )

            # 验证：逐列比较值与期望 DataFrame 一致
            filtered_sorted = filtered_df.sort_values(
                by=list(df.columns)
            ).reset_index(drop=True)
            expected_sorted = expected_df.sort_values(
                by=list(df.columns)
            ).reset_index(drop=True)

            for col in df.columns:
                for idx in range(len(expected_sorted)):
                    orig_val = expected_sorted[col].iloc[idx]
                    cached_val = filtered_sorted[col].iloc[idx]
                    if isinstance(orig_val, float):
                        assert abs(orig_val - float(cached_val)) < 1e-6, (
                            f"列 {col} 行 {idx} 值不一致: {orig_val} vs {cached_val}"
                        )
                    else:
                        assert str(orig_val) == str(cached_val), (
                            f"列 {col} 行 {idx} 值不一致: {orig_val!r} vs {cached_val!r}"
                        )
        finally:
            cache.close()


# ---------------------------------------------------------------------------
# Property 4: 缓存清除有效性 (Cache Clear)
# Feature: skill-v2-optimization, Property 4: 缓存清除有效性 (Cache Clear)
# **Validates: Requirements 2.5**
# ---------------------------------------------------------------------------


@given(data=st.data())
@settings(max_examples=100, deadline=None)
def test_cache_clear_single_table(data) -> None:
    """对于多个已缓存的表，调用 clear(table_name) 清除指定表后，
    read(table_name) 应返回空 DataFrame，而其他表的数据不受影响。
    """
    # 生成 2~4 个唯一表名
    num_tables = data.draw(st.integers(min_value=2, max_value=4), label="num_tables")
    tbl_names = data.draw(
        st.lists(table_names, min_size=num_tables, max_size=num_tables, unique=True),
        label="table_names",
    )

    # 为每个表生成一个简单 DataFrame
    dfs = {}
    for tbl in tbl_names:
        num_rows = data.draw(st.integers(min_value=1, max_value=10), label=f"rows_{tbl}")
        num_cols = data.draw(st.integers(min_value=1, max_value=3), label=f"cols_{tbl}")
        cols = data.draw(
            st.lists(column_names, min_size=num_cols, max_size=num_cols, unique=True),
            label=f"cols_list_{tbl}",
        )
        df_data = {}
        for col in cols:
            df_data[col] = data.draw(
                st.lists(
                    st.integers(min_value=-1000, max_value=1000),
                    min_size=num_rows,
                    max_size=num_rows,
                ),
                label=f"vals_{tbl}_{col}",
            )
        dfs[tbl] = pd.DataFrame(df_data)

    # 随机选择一个表作为清除目标
    target_tbl = data.draw(st.sampled_from(tbl_names), label="target_table")

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/test_cache.duckdb"
        cache = CacheManager(db_path=db_path)

        try:
            # 存入所有表
            for tbl, df in dfs.items():
                result_msg = cache.save(tbl, df)
                assert "已缓存" in result_msg

            # 清除目标表
            clear_msg = cache.clear(target_tbl)
            assert "已清除" in clear_msg

            # 验证：目标表读取返回空 DataFrame
            cleared_df = cache.read(target_tbl)
            assert len(cleared_df) == 0, (
                f"清除后表 {target_tbl} 仍有 {len(cleared_df)} 行数据"
            )

            # 验证：其他表数据不受影响
            for tbl in tbl_names:
                if tbl == target_tbl:
                    continue
                remaining_df = cache.read(tbl)
                expected_df = dfs[tbl]
                assert len(remaining_df) == len(expected_df), (
                    f"表 {tbl} 行数变化: 期望 {len(expected_df)}, 实际 {len(remaining_df)}"
                )
                assert set(remaining_df.columns) == set(expected_df.columns), (
                    f"表 {tbl} 列不一致: 期望 {set(expected_df.columns)}, 实际 {set(remaining_df.columns)}"
                )
        finally:
            cache.close()


@given(data=st.data())
@settings(max_examples=100, deadline=None)
def test_cache_clear_all_tables(data) -> None:
    """对于多个已缓存的表，调用 clear(None) 全量清除后，
    所有表的 read 应返回空 DataFrame。
    """
    # 生成 2~4 个唯一表名
    num_tables = data.draw(st.integers(min_value=2, max_value=4), label="num_tables")
    tbl_names = data.draw(
        st.lists(table_names, min_size=num_tables, max_size=num_tables, unique=True),
        label="table_names",
    )

    # 为每个表生成一个简单 DataFrame
    dfs = {}
    for tbl in tbl_names:
        num_rows = data.draw(st.integers(min_value=1, max_value=10), label=f"rows_{tbl}")
        num_cols = data.draw(st.integers(min_value=1, max_value=3), label=f"cols_{tbl}")
        cols = data.draw(
            st.lists(column_names, min_size=num_cols, max_size=num_cols, unique=True),
            label=f"cols_list_{tbl}",
        )
        df_data = {}
        for col in cols:
            df_data[col] = data.draw(
                st.lists(
                    st.integers(min_value=-1000, max_value=1000),
                    min_size=num_rows,
                    max_size=num_rows,
                ),
                label=f"vals_{tbl}_{col}",
            )
        dfs[tbl] = pd.DataFrame(df_data)

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/test_cache.duckdb"
        cache = CacheManager(db_path=db_path)

        try:
            # 存入所有表
            for tbl, df in dfs.items():
                result_msg = cache.save(tbl, df)
                assert "已缓存" in result_msg

            # 全量清除
            clear_msg = cache.clear(None)
            assert "已清除" in clear_msg

            # 验证：所有表读取返回空 DataFrame
            for tbl in tbl_names:
                cleared_df = cache.read(tbl)
                assert len(cleared_df) == 0, (
                    f"全量清除后表 {tbl} 仍有 {len(cleared_df)} 行数据"
                )

            # 验证：list_tables 返回空列表
            remaining_tables = cache.list_tables()
            assert len(remaining_tables) == 0, (
                f"全量清除后仍有表: {remaining_tables}"
            )
        finally:
            cache.close()


# ---------------------------------------------------------------------------
# 单元测试：CacheManager
# Requirements: 2.6, 2.7
# ---------------------------------------------------------------------------

from unittest.mock import patch
import os


class TestCacheManagerGracefulDegradation:
    """测试 DuckDB 未安装时的优雅降级行为。

    Requirements: 2.7
    """

    def test_save_returns_unavailable_message(self):
        """DuckDB 未安装时，save 应返回不可用提示，不抛异常。"""
        with patch.dict("sys.modules", {"duckdb": None}):
            # 强制触发 ImportError：将 duckdb 模块设为 None 使 import 失败
            cache = CacheManager.__new__(CacheManager)
            cache._available = False
            cache._conn = None
            cache._db_path = "./test.duckdb"

            df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
            result = cache.save("test_table", df)
            assert "不可用" in result

    def test_read_returns_empty_dataframe(self):
        """DuckDB 未安装时，read 应返回空 DataFrame，不抛异常。"""
        cache = CacheManager.__new__(CacheManager)
        cache._available = False
        cache._conn = None
        cache._db_path = "./test.duckdb"

        result = cache.read("test_table")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_clear_returns_unavailable_message(self):
        """DuckDB 未安装时，clear 应返回不可用提示，不抛异常。"""
        cache = CacheManager.__new__(CacheManager)
        cache._available = False
        cache._conn = None
        cache._db_path = "./test.duckdb"

        result = cache.clear("test_table")
        assert "不可用" in result

        result_all = cache.clear(None)
        assert "不可用" in result_all

    def test_list_tables_returns_empty_list(self):
        """DuckDB 未安装时，list_tables 应返回空列表，不抛异常。"""
        cache = CacheManager.__new__(CacheManager)
        cache._available = False
        cache._conn = None
        cache._db_path = "./test.duckdb"

        result = cache.list_tables()
        assert result == []

    def test_close_no_error(self):
        """DuckDB 未安装时，close 不应抛异常。"""
        cache = CacheManager.__new__(CacheManager)
        cache._available = False
        cache._conn = None
        cache._db_path = "./test.duckdb"

        # 不应抛出任何异常
        cache.close()


class TestCacheManagerDbPath:
    """测试数据库路径配置。

    Requirements: 2.6
    """

    def test_custom_db_path(self):
        """CacheManager 应使用指定的 db_path。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_path = os.path.join(tmp_dir, "custom_cache.duckdb")
            cache = CacheManager(db_path=custom_path)
            try:
                assert cache._db_path == custom_path
                assert cache._available is True
                # 验证数据库文件已创建
                assert os.path.exists(custom_path)
            finally:
                cache.close()

    def test_default_db_path(self):
        """CacheManager 默认 db_path 应为 ./panda_data_cache.duckdb。"""
        # 不实际创建，只验证默认值
        cache = CacheManager.__new__(CacheManager)
        cache._available = False
        cache._conn = None
        cache._db_path = "./panda_data_cache.duckdb"
        assert cache._db_path == "./panda_data_cache.duckdb"


class TestCacheManagerListTables:
    """测试 list_tables 返回正确表名。

    Requirements: 2.6
    """

    def test_list_tables_after_saving_multiple(self):
        """保存多个表后，list_tables 应返回所有表名。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "test_list.duckdb")
            cache = CacheManager(db_path=db_path)
            try:
                df1 = pd.DataFrame({"col_a": [1, 2, 3]})
                df2 = pd.DataFrame({"col_b": ["x", "y"]})
                df3 = pd.DataFrame({"col_c": [1.1, 2.2]})

                cache.save("table_alpha", df1)
                cache.save("table_beta", df2)
                cache.save("table_gamma", df3)

                tables = cache.list_tables()
                assert set(tables) == {"table_alpha", "table_beta", "table_gamma"}
            finally:
                cache.close()

    def test_list_tables_empty_initially(self):
        """新建的 CacheManager 应返回空表列表。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "test_empty.duckdb")
            cache = CacheManager(db_path=db_path)
            try:
                tables = cache.list_tables()
                assert tables == []
            finally:
                cache.close()


class TestCacheManagerClose:
    """测试 close 后资源释放。

    Requirements: 2.7
    """

    def test_close_releases_resources(self):
        """close() 后 _available 应为 False，_conn 应为 None。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "test_close.duckdb")
            cache = CacheManager(db_path=db_path)

            # 确认初始状态
            assert cache._available is True
            assert cache._conn is not None

            cache.close()

            # 验证资源释放
            assert cache._available is False
            assert cache._conn is None

    def test_double_close_no_error(self):
        """连续调用两次 close() 不应抛异常。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "test_double_close.duckdb")
            cache = CacheManager(db_path=db_path)

            cache.close()
            # 第二次 close 不应报错
            cache.close()

            assert cache._available is False
            assert cache._conn is None
