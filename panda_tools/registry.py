"""Tool 注册中心模块。

汇总 tools/ 下 6 个分类模块的所有 tool 定义，提供统一的查询和调用入口。
支持懒加载：tool 模块尚未实现时自动跳过，不影响已有模块的注册。
"""

import importlib
import logging
from typing import Any, Dict, List, Optional

from panda_tools.tools import TOOL_MODULES

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Tool 注册中心，汇总所有 tool 的定义和调用入口。

    从 panda_tools.tools 下的 6 个分类模块自动收集 tool 定义，
    构建名称→函数映射和类别→tool 列表映射，提供统一的查询与调用接口。
    """

    def __init__(self) -> None:
        # 名称 → tool 定义（含 function）
        self._tools: Dict[str, Dict[str, Any]] = {}
        # 类别 → tool 定义列表（不含 function，用于对外暴露 schema）
        self._categories: Dict[str, List[Dict[str, Any]]] = {}
        # 名称 → 可调用函数
        self._functions: Dict[str, Any] = {}

        self._load_all_modules()

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """返回所有已注册 tool 的 JSON Schema 定义列表。

        每个元素包含 name、description、parameters 三个字段，
        不包含内部使用的 function 引用。

        Returns:
            tool 定义列表。
        """
        return [self._schema_only(t) for t in self._tools.values()]

    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别返回 tool 的 JSON Schema 定义列表。

        Args:
            category: 类别标识符，可选值：
                market_data / market_ref / financial / trade / futures

        Returns:
            该类别下的 tool 定义列表；类别不存在时返回空列表。
        """
        tools = self._categories.get(category, [])
        return [self._schema_only(t) for t in tools]

    def call_tool(self, name: str, **kwargs: Any) -> str:
        """根据 tool 名称调用对应函数，返回格式化结果。

        Args:
            name: tool 名称（与 panda_data API 方法名一致）。
            **kwargs: 传递给 tool 函数的关键字参数。

        Returns:
            格式化后的结果字符串，或错误描述。

        Raises:
            KeyError: 当 tool 名称未注册时抛出。
        """
        if name not in self._functions:
            raise KeyError(f"未注册的 tool：{name}")
        func = self._functions[name]
        return func(**kwargs)

    def get_tool_names(self) -> List[str]:
        """返回所有已注册 tool 的名称列表。

        Returns:
            tool 名称列表。
        """
        return list(self._tools.keys())

    def get_categories(self) -> List[str]:
        """返回所有已注册的类别标识符列表。

        Returns:
            类别标识符列表。
        """
        return list(self._categories.keys())

    @property
    def tool_count(self) -> int:
        """已注册 tool 总数。"""
        return len(self._tools)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _load_all_modules(self) -> None:
        """从 TOOL_MODULES 列表中逐个导入分类模块并注册 tool。

        模块尚未实现时捕获 ImportError / ModuleNotFoundError 并跳过，
        确保已实现的模块可以正常注册。
        """
        for module_path in TOOL_MODULES:
            try:
                module = importlib.import_module(module_path)
            except (ImportError, ModuleNotFoundError) as exc:
                logger.debug("跳过尚未实现的模块 %s: %s", module_path, exc)
                continue

            category: Optional[str] = getattr(module, "CATEGORY", None)
            tools: Optional[List[Dict]] = getattr(module, "TOOLS", None)

            if category is None or tools is None:
                logger.warning(
                    "模块 %s 缺少 CATEGORY 或 TOOLS 导出，已跳过", module_path
                )
                continue

            if category not in self._categories:
                self._categories[category] = []

            for tool_def in tools:
                name = tool_def.get("name")
                if not name:
                    logger.warning("模块 %s 中存在缺少 name 的 tool 定义，已跳过", module_path)
                    continue

                self._tools[name] = tool_def
                self._categories[category].append(tool_def)

                func = tool_def.get("function")
                if func is not None:
                    self._functions[name] = func

    @staticmethod
    def _schema_only(tool_def: Dict[str, Any]) -> Dict[str, Any]:
        """返回 tool 定义的纯 schema 部分（去除 function 引用）。

        Args:
            tool_def: 完整的 tool 定义字典。

        Returns:
            仅包含 name、description、parameters 的字典。
        """
        return {
            "name": tool_def["name"],
            "description": tool_def["description"],
            "parameters": tool_def["parameters"],
        }
