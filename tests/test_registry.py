"""ToolRegistry 单元测试。

验证注册中心的核心功能：模块加载、tool 查询、tool 调用、容错处理。
"""

import pytest

from panda_tools.registry import ToolRegistry


class TestToolRegistryEmpty:
    """当 tool 模块尚未实现时，注册中心应正常工作（空注册）。"""

    def test_empty_registry_returns_empty_list(self) -> None:
        """未实现任何 tool 模块时，get_all_tools 返回空列表。"""
        registry = ToolRegistry()
        # 当前 tool 模块尚未实现，应返回空列表或已实现模块的 tool
        tools = registry.get_all_tools()
        assert isinstance(tools, list)

    def test_empty_registry_category_returns_empty(self) -> None:
        """查询不存在的类别时返回空列表。"""
        registry = ToolRegistry()
        tools = registry.get_tools_by_category("nonexistent_category")
        assert tools == []

    def test_call_unknown_tool_raises_key_error(self) -> None:
        """调用未注册的 tool 名称时抛出 KeyError。"""
        registry = ToolRegistry()
        with pytest.raises(KeyError, match="未注册的 tool"):
            registry.call_tool("nonexistent_tool")

    def test_tool_count_is_non_negative(self) -> None:
        """tool_count 属性返回非负整数。"""
        registry = ToolRegistry()
        assert registry.tool_count >= 0

    def test_get_categories_returns_list(self) -> None:
        """get_categories 返回列表类型。"""
        registry = ToolRegistry()
        categories = registry.get_categories()
        assert isinstance(categories, list)

    def test_get_tool_names_returns_list(self) -> None:
        """get_tool_names 返回列表类型。"""
        registry = ToolRegistry()
        names = registry.get_tool_names()
        assert isinstance(names, list)


class TestToolRegistryWithMockModule:
    """使用模拟 tool 定义验证注册中心的核心逻辑。"""

    @staticmethod
    def _make_registry_with_tools(tools_list, category="test_cat"):
        """创建一个注入了模拟 tool 的 ToolRegistry 实例。"""
        registry = ToolRegistry()
        # 手动注入 tool 定义
        if category not in registry._categories:
            registry._categories[category] = []
        for tool_def in tools_list:
            name = tool_def["name"]
            registry._tools[name] = tool_def
            registry._categories[category].append(tool_def)
            if "function" in tool_def:
                registry._functions[name] = tool_def["function"]
        return registry

    def test_get_all_tools_returns_schema_without_function(self) -> None:
        """get_all_tools 返回的 tool 定义不包含 function 字段。"""
        tool_def = {
            "name": "test_tool",
            "description": "测试工具",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": lambda: "ok",
        }
        registry = self._make_registry_with_tools([tool_def])
        tools = registry.get_all_tools()
        # 查找我们注入的 test_tool（可能还有自动加载的真实模块 tool）
        test_tools = [t for t in tools if t["name"] == "test_tool"]
        assert len(test_tools) == 1
        assert "function" not in test_tools[0]
        assert test_tools[0]["name"] == "test_tool"
        assert test_tools[0]["description"] == "测试工具"

    def test_get_tools_by_category(self) -> None:
        """get_tools_by_category 按类别正确返回 tool 列表。"""
        tool_a = {
            "name": "tool_a",
            "description": "工具A",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
        tool_b = {
            "name": "tool_b",
            "description": "工具B",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
        registry = ToolRegistry()
        # 注入两个不同类别
        registry._categories["cat1"] = [tool_a]
        registry._categories["cat2"] = [tool_b]
        registry._tools["tool_a"] = tool_a
        registry._tools["tool_b"] = tool_b

        cat1_tools = registry.get_tools_by_category("cat1")
        assert len(cat1_tools) == 1
        assert cat1_tools[0]["name"] == "tool_a"

        cat2_tools = registry.get_tools_by_category("cat2")
        assert len(cat2_tools) == 1
        assert cat2_tools[0]["name"] == "tool_b"

    def test_call_tool_invokes_function(self) -> None:
        """call_tool 正确调用注册的函数并返回结果。"""
        def mock_func(symbol="", start_date=""):
            return f"result: {symbol}, {start_date}"

        tool_def = {
            "name": "mock_api",
            "description": "模拟API",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": mock_func,
        }
        registry = self._make_registry_with_tools([tool_def])
        result = registry.call_tool("mock_api", symbol="000001.SZ", start_date="20250101")
        assert result == "result: 000001.SZ, 20250101"

    def test_call_tool_passes_kwargs(self) -> None:
        """call_tool 正确传递所有关键字参数。"""
        received = {}

        def capture_func(**kwargs):
            received.update(kwargs)
            return "done"

        tool_def = {
            "name": "capture_tool",
            "description": "捕获参数",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": capture_func,
        }
        registry = self._make_registry_with_tools([tool_def])
        registry.call_tool("capture_tool", a=1, b="two", c=[3])
        assert received == {"a": 1, "b": "two", "c": [3]}

    def test_tool_count_reflects_registered_tools(self) -> None:
        """tool_count 正确反映已注册 tool 数量（含自动加载的真实模块）。"""
        tools = [
            {
                "name": f"tool_{i}",
                "description": f"工具{i}",
                "parameters": {"type": "object", "properties": {}, "required": []},
            }
            for i in range(5)
        ]
        registry = self._make_registry_with_tools(tools)
        # 注入的 5 个 + 自动加载的真实模块 tool
        assert registry.tool_count >= 5
        for i in range(5):
            assert f"tool_{i}" in registry.get_tool_names()

    def test_get_tool_names_matches_registered(self) -> None:
        """get_tool_names 包含所有手动注入的 tool 名称。"""
        tools = [
            {
                "name": f"api_{i}",
                "description": f"接口{i}",
                "parameters": {"type": "object", "properties": {}, "required": []},
            }
            for i in range(3)
        ]
        registry = self._make_registry_with_tools(tools)
        names = registry.get_tool_names()
        # 注入的 tool 名称应全部存在（可能还有自动加载的真实模块 tool）
        assert {"api_0", "api_1", "api_2"}.issubset(set(names))

    def test_schema_only_extracts_correct_fields(self) -> None:
        """_schema_only 仅保留 name、description、parameters 三个字段。"""
        tool_def = {
            "name": "test",
            "description": "描述",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": lambda: None,
            "extra_field": "should_be_removed",
        }
        schema = ToolRegistry._schema_only(tool_def)
        assert set(schema.keys()) == {"name", "description", "parameters"}
