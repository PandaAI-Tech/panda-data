"""PandaAI 返回值格式化器模块。

提供 format_result 和 safe_call 两个核心函数：
- format_result：将 API 返回结果（DataFrame / str / None）格式化为 LLM 可读文本
- safe_call：统一的 API 调用包装器，自动认证、异常捕获、结果格式化
"""

from typing import Any, Callable

import pandas as pd

from panda_tools.credential import CredentialManager


def format_result(result: Any, max_rows: int = 20) -> str:
    """将 API 返回结果格式化为 LLM 可读的文本。

    格式化规则：
    - DataFrame：转为表格文本（to_string），超过 max_rows 行截断并提示总行数
    - str：直接返回
    - None / 空 DataFrame：返回"未查询到数据"

    Args:
        result: API 返回的原始结果，可能是 DataFrame、str 或 None。
        max_rows: 最大显示行数，默认 20。

    Returns:
        格式化后的字符串。
    """
    if result is None:
        return "未查询到数据"

    if isinstance(result, pd.DataFrame):
        if result.empty:
            return "未查询到数据"
        total_rows = len(result)
        if total_rows <= max_rows:
            return result.to_string(index=False)
        truncated = result.head(max_rows).to_string(index=False)
        return f"{truncated}\n\n... 共 {total_rows} 行，仅显示前 {max_rows} 行"

    if isinstance(result, str):
        return result

    return "未查询到数据"


def safe_call(func: Callable, **kwargs: Any) -> str:
    """统一的 API 调用包装器。

    执行流程：
    1. 自动调用 CredentialManager.ensure_initialized() 确保认证已完成
    2. 调用目标函数并传入参数
    3. 使用 format_result 格式化返回值
    4. 捕获所有异常，返回包含错误类型和错误信息的结构化描述

    Args:
        func: 要调用的 API 函数。
        **kwargs: 传递给 API 函数的关键字参数。

    Returns:
        格式化后的结果字符串，或结构化的错误描述。
    """
    try:
        if not CredentialManager.ensure_initialized():
            return f"API 调用失败：{CredentialManager.last_init_message()}"
        result = func(**kwargs)
        return format_result(result)
    except Exception as e:
        return f"API 调用失败：{type(e).__name__}: {e}"
