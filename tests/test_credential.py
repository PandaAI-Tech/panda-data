"""credential.py 属性基测试（hypothesis）。

使用 hypothesis 对 CredentialManager 进行属性基测试，验证凭证传递正确性、
空凭证拒绝和认证异常传播三个核心属性。
"""

import os
from unittest.mock import patch, MagicMock

from hypothesis import given, settings, assume
from hypothesis import strategies as st

import panda_tools.credential as credential_module
from panda_tools.credential import CredentialManager


# ---------------------------------------------------------------------------
# 辅助策略：生成有效（非空、非纯空白）的用户名/密码字符串
# ---------------------------------------------------------------------------
valid_credential_str = st.text(min_size=1).filter(lambda s: s.strip() != "" and "\x00" not in s)


# ---------------------------------------------------------------------------
# Property 1: 凭证传递正确性
# Feature: panda-data-openclaw-skills, Property 1: 凭证传递正确性
# **Validates: Requirements 2.1, 2.2**
# ---------------------------------------------------------------------------
@given(username=valid_credential_str, password=valid_credential_str)
@settings(max_examples=100)
def test_credential_passthrough(username: str, password: str) -> None:
    """对于任意有效用户名密码字符串对，环境变量设置后 CredentialManager
    读取值与设置值一致，且传递给 panda_data.init_token() 的参数匹配。"""

    # 重置模块级标志位
    credential_module._initialized = False

    env = {
        "PANDA_DATA_USERNAME": username,
        "PANDA_DATA_PASSWORD": password,
    }

    with patch.dict(os.environ, env, clear=False), \
         patch("panda_tools.credential.panda_data") as mock_pd:
        result = CredentialManager.init_from_env()

        # init_token 应被调用一次，且参数与环境变量值一致
        mock_pd.init_token.assert_called_once_with(
            username=username, password=password
        )
        assert "成功" in result


# ---------------------------------------------------------------------------
# Property 2: 空凭证拒绝
# Feature: panda-data-openclaw-skills, Property 2: 空凭证拒绝
# **Validates: Requirements 2.3, 14.4**
# ---------------------------------------------------------------------------

# 策略：生成空/None/纯空白的凭证值
empty_credential_str = st.one_of(
    st.just(""),
    st.just(None),
    st.text(alphabet=" \t\n\r", min_size=1),  # 纯空白字符串
)


@given(
    username=st.one_of(empty_credential_str, valid_credential_str),
    password=st.one_of(empty_credential_str, valid_credential_str),
)
@settings(max_examples=100)
def test_empty_credential_rejection(username, password) -> None:
    """对于任意空字符串/None/纯空白的用户名或密码，应拒绝初始化并返回错误提示，
    且不应调用 panda_data.init_token()。"""

    # 至少有一个凭证为空/None/纯空白
    username_invalid = username is None or str(username).strip() == ""
    password_invalid = password is None or str(password).strip() == ""
    assume(username_invalid or password_invalid)

    # 重置模块级标志位
    credential_module._initialized = False

    with patch("panda_tools.credential.panda_data") as mock_pd:
        # 测试 init_with_credentials（直接传入方式）
        result = CredentialManager.init_with_credentials(username, password)

        # 应返回错误提示
        assert "失败" in result or "错误" in result or "为空" in result
        # 不应调用 init_token
        mock_pd.init_token.assert_not_called()

    # 同时测试 init_from_env（环境变量方式）
    credential_module._initialized = False

    env = {}
    if username is not None:
        env["PANDA_DATA_USERNAME"] = str(username)
    if password is not None:
        env["PANDA_DATA_PASSWORD"] = str(password)

    # 清除可能存在的环境变量
    env_to_clear = {}
    if username is None:
        env_to_clear["PANDA_DATA_USERNAME"] = ""
    if password is None:
        env_to_clear["PANDA_DATA_PASSWORD"] = ""

    with patch.dict(os.environ, env, clear=False), \
         patch("panda_tools.credential.panda_data") as mock_pd:
        # 如果 username 是 None，需要确保环境变量不存在
        if username is None and "PANDA_DATA_USERNAME" in os.environ:
            del os.environ["PANDA_DATA_USERNAME"]
        if password is None and "PANDA_DATA_PASSWORD" in os.environ:
            del os.environ["PANDA_DATA_PASSWORD"]

        result = CredentialManager.init_from_env()

        assert "失败" in result or "错误" in result or "未设置" in result or "为空" in result
        mock_pd.init_token.assert_not_called()


# ---------------------------------------------------------------------------
# Property 3: 认证异常传播
# Feature: panda-data-openclaw-skills, Property 3: 认证异常传播
# **Validates: Requirements 2.4**
# ---------------------------------------------------------------------------

# 常见异常类型列表
exception_types = st.sampled_from([
    ValueError, TypeError, ConnectionError, RuntimeError,
    OSError, IOError, PermissionError, TimeoutError,
])


@given(
    exc_type=exception_types,
    exc_msg=st.text(min_size=1).filter(lambda s: s.strip() != ""),
    username=valid_credential_str,
    password=valid_credential_str,
)
@settings(max_examples=100)
def test_auth_exception_propagation(exc_type, exc_msg, username, password) -> None:
    """对于任意异常类型和消息，当 panda_data.init_token() 抛出该异常时，
    CredentialManager 返回的错误信息应同时包含异常类型名称和异常消息内容。"""

    # 重置模块级标志位
    credential_module._initialized = False

    with patch("panda_tools.credential.panda_data") as mock_pd:
        mock_pd.init_token.side_effect = exc_type(exc_msg)

        result = CredentialManager.init_with_credentials(username, password)

        # 返回的错误信息应包含异常类型名称
        assert exc_type.__name__ in result
        # 返回的错误信息应包含异常消息内容
        assert exc_msg in result
