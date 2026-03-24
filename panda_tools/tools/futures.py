"""期货数据 Tool 模块。

包含 3 个 tool：
- get_future_detail：获取期货基本信息
- get_future_market_post：获取期货后复权数据
- get_future_dominant：获取期货主力合约数据
"""

from typing import Any, Dict, List, Optional, Union

from panda_tools.formatter import safe_call
from panda_tools.sdk import resolve_panda_fn

CATEGORY: str = "futures"


# ------------------------------------------------------------------
# Tool 函数
# ------------------------------------------------------------------


def get_future_detail(
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    is_trading: Optional[int] = None,
) -> str:
    """获取期货基本信息。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if is_trading is not None:
        kwargs["is_trading"] = is_trading
    return safe_call(resolve_panda_fn("get_future_detail", "get_future_list"), **kwargs)


def get_future_market_post(
    start_date: str = "",
    end_date: str = "",
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取期货后复权数据。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_future_market_post"), **kwargs)


def get_future_dominant(
    start_date: str = "",
    end_date: str = "",
    underlying_symbol: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取期货主力合约数据。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if underlying_symbol is not None:
        kwargs["underlying_symbol"] = underlying_symbol
    return safe_call(resolve_panda_fn("get_future_dominant"), **kwargs)


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
# Tool 定义列表
# ------------------------------------------------------------------

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_future_detail",
        "description": (
            "获取期货基本信息，包括合约代码、上市/退市日期、合约乘数、交易所、保证金率、交易时间等。"
            "期货代码格式：\"A2501.DCE\"、\"ZN_DOMINANT.SHF\"。"
            "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "期货代码，支持单个字符串或字符串数组。"
                        "示例：\"A2501.DCE\"、\"ZN_DOMINANT.SHF\"。"
                        "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE"
                    ),
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "is_trading": {
                    "type": "integer",
                    "description": "是否可交易，1 表示交易中，0 表示已退市。不传则返回全部",
                    "enum": [0, 1],
                },
            },
            "required": [],
        },
        "function": get_future_detail,
    },
    {
        "name": "get_future_market_post",
        "description": (
            "获取期货后复权数据，返回包含日期、代码、开高低收、成交量、结算价等字段的 DataFrame。"
            "期货代码格式：\"A2501.DCE\"、\"ZN_DOMINANT.SHF\"。"
            "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "期货代码，支持单个字符串或字符串数组。"
                        "示例：\"A2511.DCE\"、\"A_DOMINANT.DCE\"。"
                        "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE"
                    ),
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250702\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250702\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_future_market_post,
    },
    {
        "name": "get_future_dominant",
        "description": (
            "获取期货主力合约数据，返回每日主力合约代码及交易代码。"
            "期货品种示例：\"A\"（豆一）、\"AG\"（白银）。"
            "期货交易所代码映射：CFFEX→CFE, CZCE→CZC, DCE→DCE, SHFE→SHF, INE→INE, GFEX→GFE。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "underlying_symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "期货品种代码，支持单个字符串或字符串数组。"
                        "示例：\"A\"（豆一）、\"AG\"（白银）、\"ZN\"（沪锌）。"
                        "注意：此参数为品种代码而非合约代码"
                    ),
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250701\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250710\"",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_future_dominant,
    },
]
