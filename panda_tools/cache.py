"""DuckDB 本地数据缓存管理器模块。

提供 CacheManager 类，基于 DuckDB 实现查询结果的本地持久化存储和读取。
DuckDB 未安装时优雅降级，所有方法返回空结果，不抛异常。
"""

import logging
from typing import Any, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class CacheManager:
    """DuckDB 本地数据缓存管理器。

    使用 DuckDB 作为本地存储引擎，提供查询结果的持久化缓存能力。
    DuckDB 未安装时自动降级，所有方法返回空结果或提示信息。
    """

    def __init__(self, db_path: str = "./panda_data_cache.duckdb") -> None:
        """初始化缓存管理器。

        Args:
            db_path: DuckDB 数据库文件路径，默认 ./panda_data_cache.duckdb。
        """
        self._available = False
        self._conn = None
        self._db_path = db_path

        try:
            import duckdb

            self._conn = duckdb.connect(db_path)
            self._available = True
        except ImportError:
            logger.warning(
                "DuckDB 未安装，缓存功能不可用。请运行 pip install duckdb 安装。"
            )
        except Exception as e:
            logger.warning(f"DuckDB 连接失败：{type(e).__name__}: {e}")

    def save(self, table_name: str, df: pd.DataFrame) -> str:
        """将 DataFrame 存入 DuckDB 表（追加模式）。

        Args:
            table_name: 表名，通常为 API 方法名（如 "get_market_data"）。
            df: 要缓存的 DataFrame。

        Returns:
            成功信息，包含表名和行数。
        """
        if not self._available:
            return "缓存不可用：DuckDB 未安装"

        try:
            # 使用唯一别名注册 DataFrame，避免与表名冲突（如表名恰好为 "df"）
            _alias = "__panda_cache_tmp_df__"
            self._conn.register(_alias, df)
            self._conn.execute(
                f"CREATE TABLE IF NOT EXISTS \"{table_name}\" AS SELECT * FROM \"{_alias}\" WHERE 1=0"
            )
            self._conn.execute(f"INSERT INTO \"{table_name}\" SELECT * FROM \"{_alias}\"")
            self._conn.unregister(_alias)
            return f"已缓存 {len(df)} 行数据到表 {table_name}"
        except Exception as e:
            return f"缓存写入失败：{type(e).__name__}: {e}"

    def read(self, table_name: str, **filters: Any) -> pd.DataFrame:
        """从 DuckDB 读取缓存数据，支持可选过滤条件。

        Args:
            table_name: 表名。
            **filters: 过滤条件，键为列名，值为筛选值。

        Returns:
            查询结果 DataFrame，表不存在时返回空 DataFrame。
        """
        if not self._available:
            return pd.DataFrame()

        try:
            # 检查表是否存在
            tables = self._conn.execute("SHOW TABLES").fetchall()
            table_names = [t[0] for t in tables]
            if table_name not in table_names:
                return pd.DataFrame()

            # 获取表的实际列名，用于过滤无效列
            columns_info = self._conn.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = ?",
                [table_name],
            ).fetchall()
            valid_columns = {row[0] for row in columns_info}

            # 构建 WHERE 子句，忽略不存在的列
            where_clauses = []
            params = []
            for col, val in filters.items():
                if col in valid_columns:
                    where_clauses.append(f"\"{col}\" = ?")
                    params.append(val)

            query = f"SELECT * FROM \"{table_name}\""
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            result = self._conn.execute(query, params).fetchdf()
            return result
        except Exception as e:
            logger.warning(f"缓存读取失败：{type(e).__name__}: {e}")
            return pd.DataFrame()

    def clear(self, table_name: Optional[str] = None) -> str:
        """清除缓存数据。

        Args:
            table_name: 指定表名则只清除该表；None 则清除所有表。

        Returns:
            成功信息。
        """
        if not self._available:
            return "缓存不可用：DuckDB 未安装"

        try:
            if table_name is not None:
                self._conn.execute(f"DROP TABLE IF EXISTS \"{table_name}\"")
                return f"已清除缓存表 {table_name}"
            else:
                tables = self._conn.execute("SHOW TABLES").fetchall()
                for t in tables:
                    self._conn.execute(f"DROP TABLE IF EXISTS \"{t[0]}\"")
                return "已清除所有缓存表"
        except Exception as e:
            return f"缓存清除失败：{type(e).__name__}: {e}"

    def list_tables(self) -> List[str]:
        """列出所有缓存表名。

        Returns:
            表名列表。
        """
        if not self._available:
            return []

        try:
            tables = self._conn.execute("SHOW TABLES").fetchall()
            return [t[0] for t in tables]
        except Exception as e:
            logger.warning(f"缓存表列表获取失败：{type(e).__name__}: {e}")
            return []

    def close(self) -> None:
        """关闭 DuckDB 连接。"""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
            self._available = False
