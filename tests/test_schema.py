# Feature: panda-data-openclaw-skills, Property 4: Tool Schema 完整性
"""Tool Schema 完整性测试。

**Validates: Requirements 4.2, 9.1, 9.2, 9.5**

验证所有 38 个 tool 均满足：
(a) 包含非空 name 字段且与 panda_data 方法名一致
(b) 包含非空中文 description
(c) parameters 符合 JSON Schema 规范（type、properties、required）
(d) 接口文档中标记为"必填"的参数出现在 required 列表中
(e) Union 类型（Optional[Union[str, List[str]]]）正确声明为 oneOf
"""

import re

import pytest

from panda_tools.registry import ToolRegistry


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture(scope="module")
def registry() -> ToolRegistry:
    """创建全局 ToolRegistry 实例。"""
    return ToolRegistry()


@pytest.fixture(scope="module")
def all_tools(registry: ToolRegistry):
    """获取所有已注册 tool 的 schema 列表。"""
    return registry.get_all_tools()


# ------------------------------------------------------------------
# 全部 38 个 panda_data 方法名
# ------------------------------------------------------------------

ALL_METHOD_NAMES = [
    # market_data (2)
    "get_market_data",
    "get_market_min_data",
    # market_ref (20)
    "get_stock_detail",
    "get_index_detail",
    "get_concept_list",
    "get_concept_constituents",
    "get_industry_detail",
    "get_industry_constituents",
    "get_stock_industry",
    "get_index_indicator",
    "get_index_weights",
    "get_lhb_list",
    "get_lhb_detail",
    "get_repurchase",
    "get_margin",
    "get_hsgt_hold",
    "get_investor_activity",
    "get_restricted_list",
    "get_holder_count",
    "get_top_holders",
    "get_block_trade",
    "get_share_float",
    # financial (5)
    "get_fina_forecast",
    "get_fina_performance",
    "get_fina_reports",
    "get_factor",
    "get_adj_factor",
    # trade (5)
    "get_trade_cal",
    "get_prev_trade_date",
    "get_last_trade_date",
    "get_stock_status_change",
    "get_trade_list",
    # futures (3)
    "get_future_detail",
    "get_future_market_post",
    "get_future_dominant",
]

# 期望的类别及其 tool 数量
EXPECTED_CATEGORY_COUNTS = {
    "market_data": 2,
    "market_ref": 20,
    "financial": 5,
    "trade": 5,
    "futures": 3,
}

# 关键 tool 的必填参数映射（接口文档中标记为"必填"的参数）
REQUIRED_PARAMS_MAP = {
    "get_market_data": ["start_date", "end_date"],
    "get_market_min_data": ["start_date", "end_date"],
    "get_stock_industry": ["stock_symbol"],
    "get_index_weights": ["start_date", "end_date"],
    "get_lhb_detail": ["start_date", "end_date"],
    "get_margin": ["start_date", "end_date"],
    "get_hsgt_hold": ["start_date", "end_date"],
    "get_investor_activity": ["start_date", "end_date"],
    "get_restricted_list": ["start_date", "end_date"],
    "get_top_holders": ["start_date", "end_date"],
    "get_share_float": ["start_date", "end_date"],
    "get_factor": ["start_date", "end_date", "factors"],
    "get_prev_trade_date": ["date"],
    "get_trade_list": ["date"],
    "get_future_market_post": ["start_date", "end_date"],
    "get_future_dominant": ["start_date", "end_date"],
}

# 应使用 oneOf 联合类型的参数（Optional[Union[str, List[str]]] 类型）
UNION_TYPE_PARAMS = {
    "get_market_data": ["symbol", "fields"],
    "get_market_min_data": ["symbol", "fields"],
    "get_stock_detail": ["symbol", "fields"],
    "get_index_detail": ["symbol", "fields"],
    "get_concept_list": ["concept"],
    "get_concept_constituents": ["concept", "concept_stock", "fields"],
    "get_industry_detail": ["fields", "level"],
    "get_industry_constituents": ["industry_code", "stock_symbol", "fields"],
    "get_trade_cal": ["fields"],
    "get_stock_status_change": ["symbol", "fields"],
    "get_trade_list": ["date"],
    "get_future_detail": ["symbol", "fields"],
    "get_future_market_post": ["symbol", "fields"],
    "get_future_dominant": ["underlying_symbol"],
    "get_factor": ["factors", "symbol"],
    "get_fina_forecast": ["symbol", "fields"],
    "get_fina_performance": ["symbol", "fields"],
    "get_fina_reports": ["symbol", "fields"],
    "get_adj_factor": ["symbol", "fields"],
    "get_lhb_list": ["symbol", "type", "fields"],
    "get_lhb_detail": ["symbol", "type", "fields"],
    "get_repurchase": ["symbol", "fields"],
    "get_margin": ["symbol", "fields"],
    "get_hsgt_hold": ["symbol", "fields"],
    "get_investor_activity": ["symbol", "fields"],
    "get_restricted_list": ["symbol", "fields"],
    "get_holder_count": ["symbol", "fields"],
    "get_top_holders": ["symbol", "fields"],
    "get_block_trade": ["symbol", "fields"],
    "get_share_float": ["symbol", "fields"],
    "get_index_indicator": ["symbol", "fields"],
    "get_index_weights": ["index_symbol", "stock_symbol", "fields"],
}


# ------------------------------------------------------------------
# 辅助函数
# ------------------------------------------------------------------


def _has_chinese(text: str) -> bool:
    """检查字符串是否包含中文字符。"""
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _is_one_of_str_or_array(schema: dict) -> bool:
    """检查 schema 是否为 oneOf [string, array<string>] 模式。"""
    one_of = schema.get("oneOf")
    if not one_of or not isinstance(one_of, list):
        return False
    types_found = set()
    for item in one_of:
        if item.get("type") == "string":
            types_found.add("string")
        elif item.get("type") == "array":
            items = item.get("items", {})
            if items.get("type") == "string":
                types_found.add("array")
    return types_found == {"string", "array"}


# ------------------------------------------------------------------
# 测试：总数验证
# ------------------------------------------------------------------


class TestToolCount:
    """验证 tool 总数为 38。"""

    def test_total_tool_count_is_38(self, registry: ToolRegistry) -> None:
        """注册中心应包含 38 个 tool。"""
        assert registry.tool_count == 38, (
            f"期望 38 个 tool，实际 {registry.tool_count} 个。"
            f"已注册名称：{registry.get_tool_names()}"
        )


# ------------------------------------------------------------------
# 测试：类别计数验证
# ------------------------------------------------------------------


class TestCategoryCounts:
    """验证各类别的 tool 数量。"""

    @pytest.mark.parametrize(
        "category,expected_count",
        list(EXPECTED_CATEGORY_COUNTS.items()),
        ids=list(EXPECTED_CATEGORY_COUNTS.keys()),
    )
    def test_category_count(
        self, registry: ToolRegistry, category: str, expected_count: int
    ) -> None:
        """每个类别的 tool 数量应与预期一致。"""
        tools = registry.get_tools_by_category(category)
        assert len(tools) == expected_count, (
            f"类别 {category} 期望 {expected_count} 个 tool，"
            f"实际 {len(tools)} 个：{[t['name'] for t in tools]}"
        )


# ------------------------------------------------------------------
# 测试：每个 tool 的 schema 完整性
# ------------------------------------------------------------------


class TestToolSchemaCompleteness:
    """验证每个 tool 的 name、description、parameters 完整性。"""

    def test_all_method_names_registered(self, registry: ToolRegistry) -> None:
        """所有 38 个 panda_data 方法名均已注册。"""
        registered_names = set(registry.get_tool_names())
        expected_names = set(ALL_METHOD_NAMES)
        missing = expected_names - registered_names
        extra = registered_names - expected_names
        assert not missing, f"缺少以下 tool：{missing}"
        assert not extra, f"多出以下 tool：{extra}"

    @pytest.mark.parametrize("tool_name", ALL_METHOD_NAMES)
    def test_tool_has_non_empty_name(
        self, all_tools: list, tool_name: str
    ) -> None:
        """每个 tool 的 name 字段非空。"""
        tool = next((t for t in all_tools if t["name"] == tool_name), None)
        assert tool is not None, f"tool {tool_name} 未找到"
        assert tool["name"], f"tool {tool_name} 的 name 为空"
        assert isinstance(tool["name"], str)

    @pytest.mark.parametrize("tool_name", ALL_METHOD_NAMES)
    def test_tool_has_chinese_description(
        self, all_tools: list, tool_name: str
    ) -> None:
        """每个 tool 的 description 非空且包含中文。"""
        tool = next((t for t in all_tools if t["name"] == tool_name), None)
        assert tool is not None, f"tool {tool_name} 未找到"
        desc = tool["description"]
        assert desc, f"tool {tool_name} 的 description 为空"
        assert _has_chinese(desc), (
            f"tool {tool_name} 的 description 不包含中文：{desc[:80]}"
        )

    @pytest.mark.parametrize("tool_name", ALL_METHOD_NAMES)
    def test_tool_parameters_has_json_schema_structure(
        self, all_tools: list, tool_name: str
    ) -> None:
        """每个 tool 的 parameters 包含 type、properties、required 字段。"""
        tool = next((t for t in all_tools if t["name"] == tool_name), None)
        assert tool is not None, f"tool {tool_name} 未找到"
        params = tool["parameters"]
        assert isinstance(params, dict), f"tool {tool_name} 的 parameters 不是字典"
        assert params.get("type") == "object", (
            f"tool {tool_name} 的 parameters.type 应为 'object'，"
            f"实际为 {params.get('type')}"
        )
        assert "properties" in params, (
            f"tool {tool_name} 的 parameters 缺少 properties 字段"
        )
        assert isinstance(params["properties"], dict), (
            f"tool {tool_name} 的 parameters.properties 不是字典"
        )
        assert "required" in params, (
            f"tool {tool_name} 的 parameters 缺少 required 字段"
        )
        assert isinstance(params["required"], list), (
            f"tool {tool_name} 的 parameters.required 不是列表"
        )


# ------------------------------------------------------------------
# 测试：必填参数验证
# ------------------------------------------------------------------


class TestRequiredParams:
    """验证关键 tool 的必填参数在 required 列表中。"""

    @pytest.mark.parametrize(
        "tool_name,expected_required",
        list(REQUIRED_PARAMS_MAP.items()),
        ids=list(REQUIRED_PARAMS_MAP.keys()),
    )
    def test_required_params_present(
        self,
        all_tools: list,
        tool_name: str,
        expected_required: list,
    ) -> None:
        """接口文档中标记为必填的参数应出现在 required 列表中。"""
        tool = next((t for t in all_tools if t["name"] == tool_name), None)
        assert tool is not None, f"tool {tool_name} 未找到"
        actual_required = set(tool["parameters"]["required"])
        for param in expected_required:
            assert param in actual_required, (
                f"tool {tool_name} 的必填参数 '{param}' 未出现在 required 中。"
                f"当前 required：{tool['parameters']['required']}"
            )


# ------------------------------------------------------------------
# 测试：Union 类型 oneOf 验证
# ------------------------------------------------------------------


class TestUnionTypeSchemas:
    """验证 Union 类型参数使用 oneOf 模式声明。"""

    @pytest.mark.parametrize(
        "tool_name,union_params",
        list(UNION_TYPE_PARAMS.items()),
        ids=list(UNION_TYPE_PARAMS.keys()),
    )
    def test_union_params_use_one_of(
        self,
        all_tools: list,
        tool_name: str,
        union_params: list,
    ) -> None:
        """Union[str, List[str]] 类型参数应使用 oneOf 模式。"""
        tool = next((t for t in all_tools if t["name"] == tool_name), None)
        assert tool is not None, f"tool {tool_name} 未找到"
        properties = tool["parameters"]["properties"]
        for param_name in union_params:
            assert param_name in properties, (
                f"tool {tool_name} 缺少参数 '{param_name}'。"
                f"已有参数：{list(properties.keys())}"
            )
            param_schema = properties[param_name]
            assert _is_one_of_str_or_array(param_schema), (
                f"tool {tool_name} 的参数 '{param_name}' 应使用 "
                f"oneOf [string, array<string>] 模式，"
                f"实际 schema：{param_schema}"
            )
