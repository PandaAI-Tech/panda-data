"""PandaAI 凭证管理器模块。

提供 CredentialManager 类，支持通过环境变量或直接传入用户名密码两种方式
完成 PandaAI 认证初始化。使用模块级标志位避免重复初始化。
"""

import os
from typing import Optional

import panda_data


def _load_dotenv_if_available() -> None:
    """从当前工作目录向上查找 `.env` 并加载到 `os.environ`。

    默认不覆盖已存在的环境变量，与 shell 中 `export` 的优先级一致。
    解决「在项目根目录用 pip install -e . 时能读到凭证，打成 whl 后从别处运行读不到」
    的常见情况：开发时 IDE / 工具注入了 `.env`，而仅安装 whl 时进程里没有这些变量。
    """
    try:
        from dotenv import find_dotenv, load_dotenv
    except ImportError:
        return
    path = find_dotenv(usecwd=True)
    if path:
        load_dotenv(path, override=False)


# 模块级标志位，避免重复初始化
_initialized: bool = False
# 最近一次 init_from_env / init_with_credentials 的说明（成功或失败），供 safe_call 展示
_last_init_message: str = ""


class CredentialManager:
    """PandaAI 凭证管理器，支持环境变量和直接传入两种方式。"""

    @staticmethod
    def init_from_env() -> str:
        """从环境变量 PANDA_DATA_USERNAME 和 PANDA_DATA_PASSWORD 读取凭证并初始化。

        Returns:
            成功信息或错误描述。
        """
        global _initialized, _last_init_message

        if _initialized:
            msg = "PandaAI 认证已完成，无需重复初始化。"
            _last_init_message = msg
            return msg

        _load_dotenv_if_available()

        username: Optional[str] = os.environ.get("PANDA_DATA_USERNAME")
        password: Optional[str] = os.environ.get("PANDA_DATA_PASSWORD")

        if not username or not username.strip():
            msg = "认证失败：环境变量 PANDA_DATA_USERNAME 未设置或为空，请配置有效的用户名。"
            _last_init_message = msg
            return msg

        if not password or not password.strip():
            msg = "认证失败：环境变量 PANDA_DATA_PASSWORD 未设置或为空，请配置有效的密码。"
            _last_init_message = msg
            return msg

        try:
            panda_data.init_token(username=username, password=password)
            _initialized = True
            msg = "PandaAI 认证初始化成功。"
            _last_init_message = msg
            return msg
        except Exception as e:
            msg = f"认证失败：{type(e).__name__}: {e}"
            _last_init_message = msg
            return msg

    @staticmethod
    def init_with_credentials(username: str, password: str) -> str:
        """直接传入用户名密码初始化。

        Args:
            username: PandaAI 用户名。
            password: PandaAI 密码。

        Returns:
            成功信息或错误描述。
        """
        global _initialized, _last_init_message

        if _initialized:
            msg = "PandaAI 认证已完成，无需重复初始化。"
            _last_init_message = msg
            return msg

        if username is None or not str(username).strip():
            msg = "认证失败：用户名为空，请提供有效的用户名。"
            _last_init_message = msg
            return msg

        if password is None or not str(password).strip():
            msg = "认证失败：密码为空，请提供有效的密码。"
            _last_init_message = msg
            return msg

        try:
            panda_data.init_token(username=username, password=password)
            _initialized = True
            msg = "PandaAI 认证初始化成功。"
            _last_init_message = msg
            return msg
        except Exception as e:
            msg = f"认证失败：{type(e).__name__}: {e}"
            _last_init_message = msg
            return msg

    @staticmethod
    def ensure_initialized() -> bool:
        """检查是否已完成认证初始化。如果未初始化，尝试从环境变量初始化。

        Returns:
            True 表示已初始化，False 表示初始化失败。
        """
        global _initialized

        if _initialized:
            return True

        CredentialManager.init_from_env()
        return _initialized

    @staticmethod
    def last_init_message() -> str:
        """最近一次认证尝试的说明（成功或失败），供调用方展示。"""
        return _last_init_message
