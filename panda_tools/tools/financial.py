"""财务与因子数据 Tool 模块。

包含 5 个 tool：
- get_fina_forecast：获取业绩预告数据
- get_fina_performance：获取财务快报数据
- get_fina_reports：获取财务季度报告
- get_factor：获取回测因子
- get_adj_factor：获取复权因子
"""

from typing import Any, Dict, List, Optional, Union

from panda_tools.formatter import safe_call
from panda_tools.sdk import resolve_panda_fn

CATEGORY: str = "financial"


# ------------------------------------------------------------------
# 联合类型 schema 复用
# ------------------------------------------------------------------

_STR_OR_LIST_SCHEMA: Dict[str, Any] = {
    "oneOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string"}},
    ]
}


def _ymd_to_quarter(ymd: str) -> str:
    """YYYYMMDD -> yyyyqN，供 get_fina_reports 季度区间。"""
    s = (ymd or "").strip()
    if len(s) < 8:
        return ""
    y = int(s[:4])
    m = int(s[4:6])
    q = (m - 1) // 3 + 1
    return f"{y}q{q}"


# ------------------------------------------------------------------
# Tool 函数
# ------------------------------------------------------------------


def get_fina_forecast(
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    info_date: Optional[str] = None,
    end_quarter: Optional[str] = None,
) -> str:
    """获取业绩预告数据。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if info_date is not None:
        kwargs["info_date"] = info_date
    if end_quarter is not None:
        kwargs["end_quarter"] = end_quarter
    return safe_call(resolve_panda_fn("get_fina_forecast", "get_financial_forecast"), **kwargs)


def get_fina_performance(
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    info_date: Optional[str] = None,
    end_quarter: Optional[str] = None,
) -> str:
    """获取财务快报数据。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if info_date is not None:
        kwargs["info_date"] = info_date
    if end_quarter is not None:
        kwargs["end_quarter"] = end_quarter
    return safe_call(resolve_panda_fn("get_fina_performance", "get_financial_performance"), **kwargs)


def get_fina_reports(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_quarter: Optional[str] = None,
    end_quarter: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
    is_latest: Optional[bool] = None,
) -> str:
    """获取财务季度报告，对应 SDK ``get_fina_reports``（parquet 季度维度）。

    若提供 ``start_date`` / ``end_date``（YYYYMMDD）而未显式给 ``start_quarter`` / ``end_quarter``，
    会按日期换算为 ``yyyyqN`` 季度区间。``end_date`` 同时作为 ``date`` 过滤（与 SDK 一致）。
    """
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields

    sq = (start_quarter or "").strip()
    eq = (end_quarter or "").strip()
    if sq:
        kwargs["start_quarter"] = sq
    elif start_date:
        converted = _ymd_to_quarter(start_date)
        if converted:
            kwargs["start_quarter"] = converted
    if eq:
        kwargs["end_quarter"] = eq
    elif end_date:
        converted = _ymd_to_quarter(end_date)
        if converted:
            kwargs["end_quarter"] = converted

    if end_date is not None:
        kwargs["date"] = end_date
    if is_latest is not None:
        kwargs["is_latest"] = is_latest

    return safe_call(resolve_panda_fn("get_fina_reports"), **kwargs)


def get_factor(
    start_date: str = "",
    end_date: str = "",
    factors: Union[str, List[str]] = "",
    symbol: Optional[Union[str, List[str]]] = None,
    index_component: Optional[str] = None,
    type: Optional[str] = None,
) -> str:
    """获取回测因子数据，支持股票和期货。"""
    kwargs: Dict[str, Any] = {
        "start_date": start_date,
        "end_date": end_date,
        "factors": factors,
    }
    if symbol is not None:
        kwargs["symbol"] = symbol
    if index_component is not None:
        kwargs["index_component"] = index_component
    if type is not None:
        kwargs["type"] = type
    return safe_call(resolve_panda_fn("get_factor"), **kwargs)


def get_adj_factor(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取复权因子数据。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_adj_factor", "get_factor_restored"), **kwargs)



# ------------------------------------------------------------------
# Tool 定义列表
# ------------------------------------------------------------------

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_fina_forecast",
        "description": (
            "获取业绩预告数据。"
            "返回 DataFrame 包含股票代码、信息发布日期、报告日期、业绩预期类型、预期增长幅度、预期净利润等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"688795.SH\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "info_date": {
                    "type": "string",
                    "description": "信息发布日期，格式 YYYYMMDD，例如 \"20251128\"",
                },
                "end_quarter": {
                    "type": "string",
                    "description": "报告季度，格式 YYYYqN，例如 \"2025q4\"",
                },
            },
            "required": [],
        },
        "function": get_fina_forecast,
    },
    {
        "name": "get_fina_performance",
        "description": (
            "获取财务快报数据。"
            "返回 DataFrame 包含股票代码、信息发布日期、报告日期、营业收入、净利润、每股收益、净资产收益率等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"688235.SH\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "info_date": {
                    "type": "string",
                    "description": "信息发布日期，格式 YYYYMMDD，例如 \"20251107\"",
                },
                "end_quarter": {
                    "type": "string",
                    "description": "报告季度，格式 YYYYqN，例如 \"2025q4\"",
                },
            },
            "required": [],
        },
        "function": get_fina_performance,
    },
    {
        "name": "get_fina_reports",
        "description": (
            "获取财务季度报告数据（SDK：get_fina_reports）。"
            "响应字段覆盖四大报表：现金流量表(cfs_*)、资产负债表(bs_*)、利润表(is_*)、估值(ratio_*)。"
            "支持 start_quarter/end_quarter（如 2024q1）或 start_date/end_date（YYYYMMDD，将换算为季度区间）。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"688795.SH\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期 YYYYMMDD；未传 start_quarter 时用于换算季度下界",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期 YYYYMMDD；未传 end_quarter 时用于换算季度上界，并作为 date 过滤",
                },
                "start_quarter": {
                    "type": "string",
                    "description": "起始季度，格式 yyyyqN，例如 \"2024q1\"；优先级高于由 start_date 换算",
                },
                "end_quarter": {
                    "type": "string",
                    "description": "结束季度，格式 yyyyqN，例如 \"2024q4\"；优先级高于由 end_date 换算",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "返回字段，支持单个字符串或字符串数组。不传则返回全部字段。"
                        "字段前缀：cfs_(现金流量表)、bs_(资产负债表)、is_(利润表)、ratio_(估值)"
                    ),
                },
                "is_latest": {
                    "type": "boolean",
                    "description": "是否每个 symbol+quarter 组合只保留最新一条（默认 true，与 SDK 一致）",
                },
            },
            "required": [],
        },
        "function": get_fina_reports,
    },
    {
        "name": "get_factor",
        "description": (
            "获取回测因子数据，支持股票和期货。"
            "返回 DataFrame 包含日期、代码、以及所选因子字段。"
            "因子包括基础因子（开高低收、成交量等）和财务因子（现金流量表 cfs_*、资产负债表 bs_*、利润表 is_*、估值 ratio_*，仅股票可选）。"
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
                "factors": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "因子列表，支持单个字符串或字符串数组。"
                        "基础因子如 \"open\"、\"close\"、\"volume\"、\"market_cap\"、\"turnover\" 等；"
                        "财务因子如 \"cfs_net_cash_operating\"、\"bs_total_assets\"、\"is_revenue\"、\"ratio_pe_ttm\" 等（仅 stock 可选）"
                    ),
                },
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "股票/期货代码，支持单个字符串或字符串数组。"
                        "股票示例：\"000001.SZ\"；期货示例：\"A_DOMINANT.DCE\"、\"ZN2501.SHF\""
                    ),
                },
                "index_component": {
                    "type": "string",
                    "description": (
                        "指数成分股过滤条件。"
                        "可选值：\"100\"（沪深300）、\"010\"（中证500）、\"001\"（中证1000）、\"000\"（非上述指数成分股）"
                    ),
                },
                "type": {
                    "type": "string",
                    "description": "产品类型，可选值：\"stock\"（股票，默认）、\"future\"（期货）",
                    "enum": ["stock", "future"],
                    "default": "stock",
                },
            },
            "required": ["start_date", "end_date", "factors"],
        },
        "function": get_factor,
    },
    {
        "name": "get_adj_factor",
        "description": (
            "获取复权因子数据。"
            "返回 DataFrame 包含股票代码、除权除息日期、前复权因子、后复权因子、除权结束日期、公告日期等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"000001.SZ\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250831\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": [],
        },
        "function": get_adj_factor,
    },
]
