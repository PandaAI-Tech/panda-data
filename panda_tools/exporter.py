"""PandaAI 数据导出模块。

提供 export_data 函数，支持将 DataFrame 导出为 CSV、Excel、DuckDB 三种格式。
导出失败时返回结构化错误消息，不抛异常。
"""

import os

import pandas as pd


def export_data(
    df: pd.DataFrame,
    path: str,
    format: str = "csv",
    table_name: str = "exported_data",
) -> str:
    """将 DataFrame 导出为指定格式的文件。

    Args:
        df: 要导出的 DataFrame。
        path: 输出文件路径（CSV/Excel）或 DuckDB 数据库路径。
        format: 导出格式，可选 "csv"、"excel"、"duckdb"。
        table_name: DuckDB 导出时的表名，默认 "exported_data"。

    Returns:
        成功信息，包含文件路径和导出行数。
        失败时返回 "导出失败：{ErrorType}: {message}"。
    """
    try:
        # 自动创建输出目录
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        if format == "csv":
            return _export_csv(df, path)
        elif format == "excel":
            return _export_excel(df, path)
        elif format == "duckdb":
            return _export_duckdb(df, path, table_name)
        else:
            return f"导出失败：ValueError: 不支持的格式 '{format}'，可选：csv, excel, duckdb"
    except Exception as e:
        return f"导出失败：{type(e).__name__}: {e}"


def _export_csv(df: pd.DataFrame, path: str) -> str:
    """导出为 CSV 文件（UTF-8 with BOM 编码）。"""
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return f"已导出 {len(df)} 行数据到 {path}"


def _export_excel(df: pd.DataFrame, path: str) -> str:
    """导出为 Excel 文件（openpyxl 引擎）。"""
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        return "导出失败：ImportError: Excel 导出需要安装 openpyxl"

    df.to_excel(path, index=False, engine="openpyxl")
    return f"已导出 {len(df)} 行数据到 {path}"


def _export_duckdb(df: pd.DataFrame, path: str, table_name: str) -> str:
    """导出为 DuckDB 表。"""
    try:
        import duckdb
    except ImportError:
        return "导出失败：ImportError: DuckDB 导出需要安装 duckdb"

    conn = duckdb.connect(path)
    try:
        conn.execute(f'CREATE OR REPLACE TABLE "{table_name}" AS SELECT * FROM df')
        return f"已导出 {len(df)} 行数据到 {path}"
    finally:
        conn.close()
