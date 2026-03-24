"""交易工具 Tool 模块。

包含 5 个 tool：
- get_trade_cal：获取交易日历
- get_prev_trade_date：获取某一日期前第n个交易日（返回字符串）
- get_last_trade_date：获取最新交易日（返回字符串）
- get_stock_status_change：获取合约特殊处理数据
- get_trade_list：获取指定日期的在售股票列表
"""

from typing import Any, Dict, List, Optional, Union

from panda_tools.formatter import safe_call
from panda_tools.sdk import resolve_panda_fn

CATEGORY: str = "trade"


# ------------------------------------------------------------------
# 联合类型 schema 复用
# ------------------------------------------------------------------

_STR_OR_LIST_SCHEMA: Dict[str, Any] = {
    "oneOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string"}},
    ]
}


# ------------------------------------------------------------------
# Tool 函数
# ------------------------------------------------------------------


def get_trade_cal(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    exchange: Optional[str] = None,
    is_trading_day: Optional[int] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取交易日历。"""
    kwargs: Dict[str, Any] = {}
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if exchange is not None:
        kwargs["exchange"] = exchange
    if is_trading_day is not None:
        kwargs["is_trading_day"] = is_trading_day
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_trade_cal", "get_trading_calendar"), **kwargs)


def get_prev_trade_date(
    date: str = "",
    exchange: Optional[str] = None,
    n: Optional[int] = None,
) -> str:
    """获取某一日期前第n个交易日，返回日期字符串。"""
    kwargs: Dict[str, Any] = {"date": date}
    if exchange is not None:
        kwargs["exchange"] = exchange
    if n is not None:
        kwargs["n"] = n
    return safe_call(resolve_panda_fn("get_prev_trade_date", "get_previous_trading_date"), **kwargs)


def get_last_trade_date(
    exchange: Optional[str] = None,
) -> str:
    """获取最新交易日，返回日期字符串。"""
    kwargs: Dict[str, Any] = {}
    if exchange is not None:
        kwargs["exchange"] = exchange
    return safe_call(resolve_panda_fn("get_last_trade_date", "get_latest_trading_date"), **kwargs)


def get_stock_status_change(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取合约特殊处理数据（ST等）。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_stock_status_change", "get_stock_special_treatment"), **kwargs)


def get_trade_list(
    date: Union[str, List[str]] = "",
) -> str:
    """获取指定日期的在售股票列表。"""
    return safe_call(resolve_panda_fn("get_trade_list", "get_trading_stock_list"), date=date)


# ------------------------------------------------------------------
# Tool 定义列表
# ------------------------------------------------------------------

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_trade_cal",
        "description": (
            "获取交易日历，支持上交所(SH)、港交所(HK)、美股(US)。"
            "返回 DataFrame 包含日期、交易所、是否交易日、前一交易日、下一交易日等字段。"
            "可按交易日/非交易日筛选。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250131\"",
                },
                "exchange": {
                    "type": "string",
                    "description": "交易所代码，默认 \"SH\"。可选值：\"SH\"（上交所）、\"HK\"（港交所）、\"US\"（美股）",
                    "enum": ["SH", "HK", "US"],
                    "default": "SH",
                },
                "is_trading_day": {
                    "type": "integer",
                    "description": "是否为交易日筛选，1=仅交易日，0=仅非交易日，不传则返回全部",
                    "enum": [0, 1],
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": [],
        },
        "function": get_trade_cal,
    },
    {
        "name": "get_prev_trade_date",
        "description": (
            "获取某一日期前第n个交易日，返回日期字符串（格式 YYYYMMDD），而非 DataFrame。"
            "支持上交所(SH)、港交所(HK)、美股(US)。"
            "例如查询 20250102 前第5个交易日，返回 \"20241225\"。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "基准日期，格式 YYYYMMDD，例如 \"20250102\"",
                },
                "exchange": {
                    "type": "string",
                    "description": "交易所代码，默认 \"SH\"。可选值：\"SH\"（上交所）、\"HK\"（港交所）、\"US\"（美股）",
                    "enum": ["SH", "HK", "US"],
                    "default": "SH",
                },
                "n": {
                    "type": "integer",
                    "description": "前第n个交易日，默认为 1",
                    "default": 1,
                },
            },
            "required": ["date"],
        },
        "function": get_prev_trade_date,
    },
    {
        "name": "get_last_trade_date",
        "description": (
            "获取最新交易日，返回日期字符串（格式 YYYYMMDD），而非 DataFrame。"
            "支持上交所(SH)、港交所(HK)、美股(US)。"
            "如果没有交易日则返回 None。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "exchange": {
                    "type": "string",
                    "description": "交易所代码，默认 \"SH\"。可选值：\"SH\"（上交所）、\"HK\"（港交所）、\"US\"（美股）",
                    "enum": ["SH", "HK", "US"],
                    "default": "SH",
                },
            },
            "required": [],
        },
        "function": get_last_trade_date,
    },
    {
        "name": "get_stock_status_change",
        "description": (
            "获取合约特殊处理数据，包括 ST、*ST、退市整理期等状态变更信息。"
            "返回 DataFrame 包含股票代码、日期、变更日期、描述、名称、类别等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。例如 \"002217.SZ\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250131\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": [],
        },
        "function": get_stock_status_change,
    },
    {
        "name": "get_trade_list",
        "description": (
            "获取指定日期的在售股票列表。"
            "返回 DataFrame 包含股票代码和日期字段。"
            "支持传入单个日期或多个日期。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "日期，格式 YYYYMMDD，例如 \"20251211\"。支持单个字符串或字符串数组",
                },
            },
            "required": ["date"],
        },
        "function": get_trade_list,
    },
]
