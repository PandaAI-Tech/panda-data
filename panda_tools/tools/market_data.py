"""行情数据 Tool 模块。

包含 2 个 tool：
- get_market_data：获取日线行情数据（股票/指数/期货）
- get_market_min_data：获取分钟级行情数据（股票/指数/期货）
"""

from typing import Any, Dict, List, Optional, Union

from panda_tools.formatter import safe_call
from panda_tools.sdk import resolve_panda_fn

CATEGORY: str = "market_data"


# ------------------------------------------------------------------
# Tool 函数
# ------------------------------------------------------------------


def get_market_data(
    start_date: str = "",
    end_date: str = "",
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    type: Optional[str] = None,
    indicator: Optional[str] = None,
    st: Optional[bool] = None,
) -> str:
    """获取日线行情数据（股票/指数/期货）。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if type is not None:
        kwargs["type"] = type
    if indicator is not None:
        kwargs["indicator"] = indicator
    if st is not None:
        kwargs["st"] = st
    return safe_call(resolve_panda_fn("get_market_data"), **kwargs)


def get_market_min_data(
    start_date: str = "",
    end_date: str = "",
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    symbol_type: Optional[str] = None,
    time_zone: Optional[tuple] = None,
    frequency: Optional[str] = None,
) -> str:
    """获取分钟级行情数据（股票/指数/期货）。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if symbol_type is not None:
        kwargs["symbol_type"] = symbol_type
    if time_zone is not None:
        kwargs["time_zone"] = tuple(time_zone) if not isinstance(time_zone, tuple) else time_zone
    if frequency is not None:
        kwargs["frequency"] = frequency
    return safe_call(resolve_panda_fn("get_market_min_data"), **kwargs)


# ------------------------------------------------------------------
# 联合类型 schema 复用
# ------------------------------------------------------------------

_STR_OR_LIST_SCHEMA: Dict[str, Any] = {
    "oneOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string"}},
    ]
}

_TIME_ZONE_SCHEMA: Dict[str, Any] = {
    "type": "array",
    "items": {"type": "string"},
    "minItems": 2,
    "maxItems": 2,
    "description": (
        "时间段过滤，格式为 (\"HH:MM\", \"HH:MM\")，"
        "例如 (\"10:00\", \"11:00\")。以数组形式传入两个时间字符串"
    ),
}

# ------------------------------------------------------------------
# Tool 定义列表
# ------------------------------------------------------------------

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_market_data",
        "description": (
            "获取日线行情数据，支持股票、指数、期货。"
            "返回 DataFrame 包含日期、代码、开高低收、成交量等字段。"
            "股票代码格式：A股 \"000001.SZ\"、港股 \"0001.HK\"、美股 \"AAPL.NB\"；"
            "期货代码格式：\"A2501.DCE\"、\"ZN_DOMINANT.SHF\"，"
            "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE；"
            "指数代码格式：\"000001.SH\"、\"000300.SH\"。"
            "开始日期与结束日期间隔不超过5年。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250702\"。与结束日期间隔不超过5年",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250702\"。与开始日期间隔不超过5年",
                },
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "股票/指数/期货代码，支持单个字符串或字符串数组。"
                        "A股示例：\"000001.SZ\"；期货示例：\"A2501.DCE\"；"
                        "指数示例：\"000001.SH\"。"
                        "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE"
                    ),
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "type": {
                    "type": "string",
                    "description": "产品类型，可选值：\"stock\"（股票，默认）、\"future\"（期货）、\"index\"（指数）",
                    "enum": ["stock", "future", "index"],
                    "default": "stock",
                },
                "indicator": {
                    "type": "string",
                    "description": (
                        "用作筛选指数成分股的指数代码，默认 \"000985\"。"
                        "可选值：000300、000905、000985、000852。仅在 type=\"stock\" 时有效"
                    ),
                    "default": "000985",
                },
                "st": {
                    "type": "boolean",
                    "description": "是否包含ST股，默认 True 表示包含。仅在 type=\"stock\" 时有效",
                    "default": True,
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_market_data,
    },
    {
        "name": "get_market_min_data",
        "description": (
            "获取分钟级行情数据，支持股票、指数、期货。"
            "返回 DataFrame 包含日期、分钟、代码、开高低收、成交量等字段。"
            "频率与日期范围限制：1m≈1个月, 5m≈6个月, 15m≈1年, 60m≈5年。"
            "指数仅支持 1m 频率。"
            "股票代码格式：A股 \"000001.SZ\"；"
            "期货代码格式：\"A2501.DCE\"、\"ZN_DOMINANT.SHF\"，"
            "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE；"
            "指数代码格式：\"000001.SH\"、\"000300.SH\"。"
            "注意：产品类型参数名为 symbol_type（非 type）。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250702\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250702\"",
                },
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "股票/指数/期货代码，支持单个字符串或字符串数组。"
                        "A股示例：\"000001.SZ\"；期货示例：\"A2501.DCE\"；"
                        "指数示例：\"000001.SH\"。"
                        "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE"
                    ),
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "symbol_type": {
                    "type": "string",
                    "description": (
                        "产品类型，可选值：\"stock\"（股票）、\"future\"（期货）、\"index\"（指数）。"
                        "注意参数名为 symbol_type 而非 type"
                    ),
                    "enum": ["stock", "future", "index"],
                },
                "time_zone": {
                    **_TIME_ZONE_SCHEMA,
                },
                "frequency": {
                    "type": "string",
                    "description": (
                        "数据频率，可选值：\"1m\"（1分钟，默认）、\"5m\"（5分钟）、\"15m\"（15分钟）、\"60m\"（60分钟）。"
                        "指数仅支持 1m。"
                        "频率与日期范围限制：1m≈1个月, 5m≈6个月, 15m≈1年, 60m≈5年"
                    ),
                    "enum": ["1m", "5m", "15m", "60m"],
                    "default": "1m",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_market_min_data,
    },
]
