"""解析 panda_data 顶层 API，兼容不同 SDK / wheel 中的新旧函数名。

若本地 panda_data 与官方 __init__ 导出不一致，会按候选名依次尝试。
"""

from __future__ import annotations

from typing import Any, Callable

import panda_data


def resolve_panda_fn(*names: str) -> Callable[..., Any]:
    """返回 ``panda_data`` 上第一个存在的可调用对象。

    Args:
        names: 按优先级排列的函数名（新名在前、旧名在后）。

    Raises:
        AttributeError: 所有候选名均不存在或不可调用。
    """
    for n in names:
        fn = getattr(panda_data, n, None)
        if callable(fn):
            return fn
    raise AttributeError(
        "当前环境的 panda_data 未导出以下任一函数: "
        + ", ".join(names)
        + "。请安装与 PandaAI 文档一致的 panda_data 包并检查版本。"
    )
