"""按类别组织的 Tool 定义模块。

每个子模块导出：
- CATEGORY: str — 类别标识符
- TOOLS: List[Dict] — tool 定义列表，每个 dict 包含 name、description、parameters、function
"""

# 所有 tool 分类模块名称
TOOL_MODULES = [
    "panda_tools.tools.market_data",
    "panda_tools.tools.market_ref",
    "panda_tools.tools.financial",
    "panda_tools.tools.trade_tools",
    "panda_tools.tools.futures",
]

# 类别标识符列表
CATEGORIES = [
    "market_data",
    "market_ref",
    "financial",
    "trade",
    "futures"
]
