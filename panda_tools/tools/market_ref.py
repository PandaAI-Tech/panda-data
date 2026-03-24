"""市场参考数据 Tool 模块。

包含 20 个 tool：
- get_stock_detail：获取股票基本信息
- get_index_detail：获取指数基本信息
- get_concept_list：获取概念列表
- get_concept_constituents：获取概念成分股
- get_industry_detail：获取行业基本信息
- get_industry_constituents：获取行业成分股
- get_stock_industry：获取指定股票所属行业
- get_index_indicator：获取指数估值指标
- get_index_weights：获取指数权重信息
- get_lhb_list：获取股票龙虎榜数据
- get_lhb_detail：获取股票龙虎榜明细数据
- get_repurchase：获取回购数据
- get_margin：获取融资融券信息
- get_hsgt_hold：获取沪深股通持股信息
- get_investor_activity：获取A股合约投资者关系活动
- get_restricted_list：获取股票限售解禁明细数据
- get_holder_count：获取股东数量
- get_top_holders：获取A股股东信息
- get_block_trade：获取A股大宗交易信息
- get_share_float：获取股票股本数据
"""

from typing import Any, Dict, List, Optional, Union

from panda_tools.formatter import safe_call
from panda_tools.sdk import resolve_panda_fn

CATEGORY: str = "market_ref"


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


def get_stock_detail(
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    market: Optional[str] = None,
    status: Optional[int] = None,
) -> str:
    """获取股票基本信息。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if market is not None:
        kwargs["market"] = market
    if status is not None:
        kwargs["status"] = status
    return safe_call(resolve_panda_fn("get_stock_detail"), **kwargs)


def get_index_detail(
    symbol: Optional[Union[str, List[str]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
    status: Optional[int] = None,
) -> str:
    """获取指数基本信息。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if status is not None:
        kwargs["status"] = status
    return safe_call(resolve_panda_fn("get_index_detail", "get_index_symbol"), **kwargs)


def get_concept_list(
    concept: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """获取概念列表。"""
    kwargs: Dict[str, Any] = {}
    if concept is not None:
        kwargs["concept"] = concept
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    return safe_call(resolve_panda_fn("get_concept_list"), **kwargs)


def get_concept_constituents(
    concept: Optional[Union[str, List[str]]] = None,
    concept_stock: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取概念成分股。"""
    kwargs: Dict[str, Any] = {}
    if concept is not None:
        kwargs["concept"] = concept
    if concept_stock is not None:
        kwargs["concept_stock"] = concept_stock
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_concept_constituents", "get_concept_stock"), **kwargs)


def get_industry_detail(
    fields: Optional[Union[str, List[str]]] = None,
    level: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取行业基本信息数据。"""
    kwargs: Dict[str, Any] = {}
    if fields is not None:
        kwargs["fields"] = fields
    if level is not None:
        kwargs["level"] = level
    return safe_call(resolve_panda_fn("get_industry_detail", "get_industry_list"), **kwargs)


def get_industry_constituents(
    industry_code: Optional[Union[str, List[str]]] = None,
    stock_symbol: Optional[Union[str, List[str]]] = None,
    level: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取行业成分股数据。"""
    kwargs: Dict[str, Any] = {}
    if industry_code is not None:
        kwargs["industry_code"] = industry_code
    if stock_symbol is not None:
        kwargs["stock_symbol"] = stock_symbol
    if level is not None:
        kwargs["level"] = level
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_industry_constituents", "get_industry_stock"), **kwargs)


def get_stock_industry(
    stock_symbol: str = "",
    level: Optional[str] = None,
) -> str:
    """获取指定股票所属的行业信息。"""
    kwargs: Dict[str, Any] = {"stock_symbol": stock_symbol}
    if level is not None:
        kwargs["level"] = level
    return safe_call(resolve_panda_fn("get_stock_industry"), **kwargs)


def get_index_indicator(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取指数估值指标。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_index_indicator"), **kwargs)


def get_index_weights(
    index_symbol: Optional[Union[str, List[str]]] = None,
    stock_symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取指数权重信息。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if index_symbol is not None:
        kwargs["index_symbol"] = index_symbol
    if stock_symbol is not None:
        kwargs["stock_symbol"] = stock_symbol
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_index_weights"), **kwargs)


def get_lhb_list(
    symbol: Optional[Union[str, List[str]]] = None,
    type: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取股票龙虎榜数据。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if type is not None:
        kwargs["type"] = type
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_lhb_list", "get_abnormal"), **kwargs)


def get_lhb_detail(
    symbol: Optional[Union[str, List[str]]] = None,
    type: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    side: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取股票龙虎榜明细数据。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if type is not None:
        kwargs["type"] = type
    if side is not None:
        kwargs["side"] = side
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_lhb_detail", "get_abnormal_detail"), **kwargs)


def get_repurchase(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取回购数据。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_repurchase", "get_buy_back"), **kwargs)


def get_margin(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
    margin_type: Optional[str] = None,
) -> str:
    """获取融资融券信息。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if margin_type is not None:
        kwargs["margin_type"] = margin_type
    return safe_call(resolve_panda_fn("get_margin", "get_securities_margin"), **kwargs)


def get_hsgt_hold(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取沪深股通持股信息。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_hsgt_hold", "get_stock_connect"), **kwargs)


def get_investor_activity(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取A股合约投资者关系活动。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_investor_activity", "get_investor_activities"), **kwargs)


def get_restricted_list(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
    market: Optional[str] = None,
) -> str:
    """获取股票限售解禁明细数据。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if market is not None:
        kwargs["market"] = market
    return safe_call(resolve_panda_fn("get_restricted_list", "get_restricted_details"), **kwargs)


def get_holder_count(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取股东数量。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_holder_count", "get_holder_number"), **kwargs)


def get_top_holders(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
    market: Optional[str] = None,
    start_rank: Optional[int] = None,
    end_rank: Optional[int] = None,
    stock_type: Optional[str] = None,
) -> str:
    """获取A股股东信息。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    if market is not None:
        kwargs["market"] = market
    if start_rank is not None:
        kwargs["start_rank"] = start_rank
    if end_rank is not None:
        kwargs["end_rank"] = end_rank
    if stock_type is not None:
        kwargs["stock_type"] = stock_type
    return safe_call(resolve_panda_fn("get_top_holders", "get_main_shareholder"), **kwargs)


def get_block_trade(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取A股大宗交易信息。"""
    kwargs: Dict[str, Any] = {}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if start_date is not None:
        kwargs["start_date"] = start_date
    if end_date is not None:
        kwargs["end_date"] = end_date
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_block_trade"), **kwargs)


def get_share_float(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = "",
    end_date: str = "",
    fields: Optional[Union[str, List[str]]] = None,
) -> str:
    """获取股票股本数据。"""
    kwargs: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if symbol is not None:
        kwargs["symbol"] = symbol
    if fields is not None:
        kwargs["fields"] = fields
    return safe_call(resolve_panda_fn("get_share_float", "get_stock_shares"), **kwargs)


# ------------------------------------------------------------------
# Tool 定义列表
# ------------------------------------------------------------------

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_stock_detail",
        "description": (
            "获取股票基本信息，支持A股、港股、美股。"
            "返回 DataFrame 包含股票代码、名称、行业、上市日期、交易状态等字段。"
            "A股代码格式：\"000001.SZ\"、\"600000.SH\"；"
            "港股代码格式：\"0001.HK\"、\"0700.HK\"；"
            "美股代码格式：\"AAPL.NB\"、\"TSLA.NB\"。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "股票代码，支持单个字符串或字符串数组。"
                        "A股示例：\"000001.SZ\"；港股示例：\"0001.HK\"；美股示例：\"AAPL.NB\"。"
                        "传空字符串可获取全部股票"
                    ),
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "market": {
                    "type": "string",
                    "description": "市场，可选值：\"cn\"（A股，默认）、\"hk\"（港股）、\"us\"（美股）",
                    "enum": ["cn", "hk", "us"],
                    "default": "cn",
                },
                "status": {
                    "type": "integer",
                    "description": "是否在市，可选值：1（在市）、0（退市）、-1（未知）",
                    "enum": [1, 0, -1],
                },
            },
            "required": [],
        },
        "function": get_stock_detail,
    },
    {
        "name": "get_index_detail",
        "description": (
            "获取指数基本信息。"
            "返回 DataFrame 包含指数代码、名称、上市日期、交易状态等字段。"
            "指数代码格式：\"000001.SH\"、\"000300.SH\"。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "指数代码，支持单个字符串或字符串数组。"
                        "示例：\"000001.SH\"、\"000300.SH\"。"
                        "传空字符串可获取全部指数"
                    ),
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "status": {
                    "type": "string",
                    "description": "指数状态，可选值：\"1\"（正常交易）、\"0\"（已退市）、\"-1\"（暂无信息）",
                    "enum": ["1", "0", "-1"],
                },
            },
            "required": [],
        },
        "function": get_index_detail,
    },
    {
        "name": "get_concept_list",
        "description": (
            "获取概念列表。"
            "返回 DataFrame 包含概念名称和概念纳入日期。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "concept": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "概念名称，支持单个字符串或字符串数组。示例：\"英伟达概念\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250131\"",
                },
            },
            "required": [],
        },
        "function": get_concept_list,
    },
    {
        "name": "get_concept_constituents",
        "description": (
            "获取概念成分股。"
            "返回 DataFrame 包含概念名称、成分股代码和纳入日期。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "concept": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "概念名称，支持单个字符串或字符串数组。示例：\"英伟达概念\"",
                },
                "concept_stock": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"001339.SZ\"",
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
        "function": get_concept_constituents,
    },
    {
        "name": "get_industry_detail",
        "description": (
            "获取行业基本信息数据（申万行业分类）。"
            "返回 DataFrame 包含行业代码、名称、级别、上级行业代码等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "level": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "行业级别，支持单个字符串或字符串数组。"
                        "可选值：\"L1\"（一级）、\"L2\"（二级）、\"L3\"（三级）"
                    ),
                },
            },
            "required": [],
        },
        "function": get_industry_detail,
    },
    {
        "name": "get_industry_constituents",
        "description": (
            "获取行业成分股数据。"
            "返回 DataFrame 包含股票代码、各级行业代码和名称、纳入时间等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "industry_code": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "行业代码，支持单个字符串或字符串数组。示例：\"801780\"",
                },
                "stock_symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"000001.SZ\"",
                },
                "level": {
                    "type": "string",
                    "description": "行业级别，可选值：\"L1\"（一级）、\"L2\"（二级）、\"L3\"（三级）",
                    "enum": ["L1", "L2", "L3"],
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": [],
        },
        "function": get_industry_constituents,
    },
    {
        "name": "get_stock_industry",
        "description": (
            "获取指定股票所属的行业信息。"
            "返回 DataFrame 包含股票代码、行业代码、行业名称及上级行业信息。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "股票代码（必填）。示例：\"000001.SZ\"",
                },
                "level": {
                    "type": "string",
                    "description": "行业级别，可选值：\"L1\"（一级）、\"L2\"（二级）、\"L3\"（三级）",
                    "enum": ["L1", "L2", "L3"],
                },
            },
            "required": ["stock_symbol"],
        },
        "function": get_stock_industry,
    },
    {
        "name": "get_index_indicator",
        "description": (
            "获取指数估值指标。"
            "返回 DataFrame 包含日期、指数代码、市净率(LF/LYR/TTM)、市盈率(LYR/TTM)等字段。"
            "指数代码格式：\"000001.SH\"、\"000300.SH\"。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "指数代码，支持单个字符串或字符串数组。"
                        "示例：\"000001.SH\"。传空字符串可获取全部指数"
                    ),
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
        "function": get_index_indicator,
    },
    {
        "name": "get_index_weights",
        "description": (
            "获取指数权重信息。"
            "返回 DataFrame 包含指数代码、日期、股票代码、权重等字段。"
            "指数代码格式：\"000006.SH\"；股票代码格式：\"600048.SH\"。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "index_symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "指数代码，支持单个字符串或字符串数组。示例：\"000006.SH\"",
                },
                "stock_symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "成分股代码，支持单个字符串或字符串数组。示例：\"600048.SH\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250131\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_index_weights,
    },
    {
        "name": "get_lhb_list",
        "description": (
            "获取股票龙虎榜数据。"
            "返回 DataFrame 包含股票代码、日期、龙虎榜类型、原因、金额、涨跌幅等字段。"
            "龙虎榜类型代码示例：G0007（日涨幅偏离值达7%）、T0020（日换手率达20%）、"
            "C0000（涨跌幅）、D0000（涨跌幅偏离值）等。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"000001.SZ\"",
                },
                "type": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "龙虎榜类型，支持单个字符串或字符串数组。"
                        "常见类型：\"G0007\"（日涨幅偏离值达7%）、\"L0007\"（日跌幅偏离值达7%）、"
                        "\"T0020\"（日换手率达20%）、\"C0000\"（涨跌幅）"
                    ),
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
        "function": get_lhb_list,
    },
    {
        "name": "get_lhb_detail",
        "description": (
            "获取股票龙虎榜明细数据。"
            "返回 DataFrame 包含股票代码、日期、龙虎榜类型、买卖方向、排名、营业部名称、买入/卖出金额等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"001314.SZ\"",
                },
                "type": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": (
                        "龙虎榜类型，支持单个字符串或字符串数组。"
                        "常见类型：\"G0007\"（日涨幅偏离值达7%）、\"L0007\"（日跌幅偏离值达7%）、"
                        "\"T0020\"（日换手率达20%）"
                    ),
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250131\"",
                },
                "side": {
                    "type": "string",
                    "description": (
                        "买卖方向。可选值：\"buy\"（买入）、\"sell\"（卖出）、"
                        "\"cum\"（累计数据，记录发生严重异常时的累计数据，与具体买卖方向无关）"
                    ),
                    "enum": ["buy", "sell", "cum"],
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_lhb_detail,
    },
    {
        "name": "get_repurchase",
        "description": (
            "获取回购数据。"
            "返回 DataFrame 包含股票代码、日期、回购方、事件进程、回购股数、回购金额、回购价格等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"002011.SZ\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20251231\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": [],
        },
        "function": get_repurchase,
    },
    {
        "name": "get_margin",
        "description": (
            "获取融资融券信息。"
            "返回 DataFrame 包含股票代码、日期、融资买入额、融资余额、融券卖出量、融券余额、总余额等字段。"
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
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250131\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "margin_type": {
                    "type": "string",
                    "description": "买卖方向，可选值：\"stock\"（融券卖出）、\"cash\"（融资买入）",
                    "enum": ["stock", "cash"],
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_margin,
    },
    {
        "name": "get_hsgt_hold",
        "description": (
            "获取沪深股通持股信息。"
            "返回 DataFrame 包含日期、股票代码、持股数量、持股比例、调整后持股比例等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"000001.SZ\"。传空字符串可获取全部股票",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250601\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250630\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_hsgt_hold,
    },
    {
        "name": "get_investor_activity",
        "description": (
            "获取A股合约投资者关系活动。"
            "返回 DataFrame 包含公告发布日、股票代码、参与人员、与会人员详情、参与机构等字段。"
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
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250131\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_investor_activity,
    },
    {
        "name": "get_restricted_list",
        "description": (
            "获取股票限售解禁明细数据。"
            "返回 DataFrame 包含合约代码、发布日期、解禁日期、股东名、股东类型、解除限售股份数量等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"001256.SZ\"",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20251201\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20251231\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "market": {
                    "type": "string",
                    "description": "市场，默认 \"cn\" 为中国内地市场",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_restricted_list,
    },
    {
        "name": "get_holder_count",
        "description": (
            "获取股东数量。"
            "返回 DataFrame 包含股票代码、公告日期、截止日期、A股股东户数、户均持股数等字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "股票代码，支持单个字符串或字符串数组。示例：\"000001.SZ\"。传空字符串可获取全部股票",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式 YYYYMMDD，例如 \"20250531\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": [],
        },
        "function": get_holder_count,
    },
    {
        "name": "get_top_holders",
        "description": (
            "获取A股股东信息。"
            "返回 DataFrame 包含信息发布日期、股票代码、排名、股东名称、股东性质、占股比例等字段。"
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
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250531\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
                "market": {
                    "type": "string",
                    "description": "市场，默认 \"cn\" 为中国内地市场",
                },
                "start_rank": {
                    "type": "integer",
                    "description": "排名开始值，例如 1",
                },
                "end_rank": {
                    "type": "integer",
                    "description": "排名结束值，例如 5",
                },
                "stock_type": {
                    "type": "string",
                    "description": "股票种类，可选值：\"flow\"（基于持有A股流通股）、\"total\"（基于所有发行出的A股）",
                    "enum": ["flow", "total"],
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_top_holders,
    },
    {
        "name": "get_block_trade",
        "description": (
            "获取A股大宗交易信息。"
            "返回 DataFrame 包含股票代码、交易日期、成交价、成交量、成交额、买方营业部、卖方营业部等字段。"
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
        "function": get_block_trade,
    },
    {
        "name": "get_share_float",
        "description": (
            "获取股票股本数据。"
            "返回 DataFrame 包含股票代码、信息发布日期、流通A股、自由流通股本、非流通A股、总股本等字段。"
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
                    "description": "开始日期（必填），格式 YYYYMMDD，例如 \"20250101\"",
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期（必填），格式 YYYYMMDD，例如 \"20250831\"",
                },
                "fields": {
                    **_STR_OR_LIST_SCHEMA,
                    "description": "返回字段，支持单个字符串或字符串数组。不传则返回全部字段",
                },
            },
            "required": ["start_date", "end_date"],
        },
        "function": get_share_float,
    },
]
