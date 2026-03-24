#!/usr/bin/env python3
"""全量接口批量测试脚本。

对 PandaAI 全部 38 个 API 方法进行真实调用测试，验证返回值类型和基本正确性。
每个 API 仅调用一次，使用最小化参数范围。

用法：
    python tests/test_all_apis.py                          # 测试全部 38 个 API
    python tests/test_all_apis.py --category market_data   # 仅测试行情数据类别
    python tests/test_all_apis.py --method get_market_data # 仅测试指定方法

    # 通过 pytest 运行（凭证：环境变量 或 tests/local_credentials.py，见下方 _configure_panda_credentials）
    pytest tests/test_all_apis.py -v
    pytest tests/ -m "not integration"                   # 跳过集成测试
"""

import argparse
import importlib.util
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import panda_data
import pytest

# ---------------------------------------------------------------------------
# 导入 tool 函数
# ---------------------------------------------------------------------------
from panda_tools.tools.market_data import (
    get_market_data,
    get_market_min_data,
)
from panda_tools.tools.market_ref import (
    get_stock_detail,
    get_index_detail,
    get_concept_list,
    get_concept_constituents,
    get_industry_detail,
    get_industry_constituents,
    get_stock_industry,
    get_index_indicator,
    get_index_weights,
    get_lhb_list,
    get_lhb_detail,
    get_repurchase,
    get_margin,
    get_hsgt_hold,
    get_investor_activity,
    get_restricted_list,
    get_holder_count,
    get_top_holders,
    get_block_trade,
    get_share_float,
)
from panda_tools.tools.financial import (
    get_fina_forecast,
    get_fina_performance,
    get_fina_reports,
    get_factor,
    get_adj_factor,
)
from panda_tools.tools.trade_tools import (
    get_trade_cal,
    get_prev_trade_date,
    get_last_trade_date,
    get_stock_status_change,
    get_trade_list,
)
from panda_tools.tools.futures import (
    get_future_detail,
    get_future_market_post,
    get_future_dominant,
)


def _configure_panda_credentials() -> bool:
    """初始化 PandaAI token。优先级：环境变量 > tests/local_credentials.py。

    环境变量：PANDA_DATA_USERNAME、PANDA_DATA_PASSWORD。

    本地文件（勿提交仓库）：复制 tests/local_credentials.example.py 为
    tests/local_credentials.py 并填写账号密码。
    """

    try:
        panda_data.init_token(username="", password="")
        return True
    except Exception:
        return False

    local = Path(__file__).resolve().parent / "local_credentials.py"
    if not local.is_file():
        return False
    spec = importlib.util.spec_from_file_location("_panda_local_credentials", local)
    if spec is None or spec.loader is None:
        return False
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    u = getattr(mod, "PANDA_USERNAME", None)
    p = getattr(mod, "PANDA_PASSWORD", None)
    if not u or not p:
        return False
    try:
        panda_data.init_token(username=str(u).strip(), password=str(p).strip())
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


@dataclass
class ApiCallCase:
    """单个 API 测试用例（勿命名为 Test*，避免 pytest 误识别为测试类）。"""

    category: str
    method: str
    func: Callable[..., str]
    kwargs: Dict[str, Any]
    expect_type: str = "dataframe"  # "dataframe" 或 "string"


@dataclass
class ApiCallResult:
    """单个 API 测试结果。"""

    category: str
    method: str
    success: bool
    elapsed: float = 0.0
    error: str = ""
    preview: str = ""


@dataclass
class ApiBatchSummary:
    """测试汇总统计。"""

    total: int = 0
    success: int = 0
    failure: int = 0
    results: List[ApiCallResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 测试用例定义 — 38 个 API
# ---------------------------------------------------------------------------


def build_test_cases() -> List[ApiCallCase]:
    """构建全部 38 个 API 的测试用例列表。"""
    cases: List[ApiCallCase] = []

    # ---- market_data（2 个）----
    cases.append(ApiCallCase(
        category="market_data",
        method="get_market_data",
        func=get_market_data,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_data",
        method="get_market_min_data",
        func=get_market_min_data,
        kwargs={
            "symbol": "000001.SZ",
            "start_date": "20250101",
            "end_date": "20250115",
            "frequency": "60m",
        },
    ))

    # ---- market_ref（20 个）----
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_stock_detail",
        func=get_stock_detail,
        kwargs={"symbol": "000001.SZ"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_index_detail",
        func=get_index_detail,
        kwargs={"symbol": "000001.SH"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_concept_list",
        func=get_concept_list,
        kwargs={},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_concept_constituents",
        func=get_concept_constituents,
        kwargs={"concept": "英伟达概念"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_industry_detail",
        func=get_industry_detail,
        kwargs={"level": "L1"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_industry_constituents",
        func=get_industry_constituents,
        kwargs={"industry_code": "801780"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_stock_industry",
        func=get_stock_industry,
        kwargs={"stock_symbol": "000001.SZ"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_index_indicator",
        func=get_index_indicator,
        kwargs={"symbol": "000001.SH", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_index_weights",
        func=get_index_weights,
        kwargs={
            "index_symbol": "000006.SH",
            "start_date": "20250101",
            "end_date": "20250115",
        },
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_lhb_list",
        func=get_lhb_list,
        kwargs={"start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_lhb_detail",
        func=get_lhb_detail,
        kwargs={"start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_repurchase",
        func=get_repurchase,
        kwargs={"symbol": "002011.SZ", "start_date": "20250101", "end_date": "20250630"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_margin",
        func=get_margin,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_hsgt_hold",
        func=get_hsgt_hold,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_investor_activity",
        func=get_investor_activity,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_restricted_list",
        func=get_restricted_list,
        kwargs={"start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_holder_count",
        func=get_holder_count,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_top_holders",
        func=get_top_holders,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_block_trade",
        func=get_block_trade,
        kwargs={"start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="market_ref",
        method="get_share_float",
        func=get_share_float,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))

    # ---- financial（5 个）----
    cases.append(ApiCallCase(
        category="financial",
        method="get_fina_forecast",
        func=get_fina_forecast,
        kwargs={"symbol": "688795.SH"},
    ))
    cases.append(ApiCallCase(
        category="financial",
        method="get_fina_performance",
        func=get_fina_performance,
        kwargs={"symbol": "688235.SH"},
    ))
    cases.append(ApiCallCase(
        category="financial",
        method="get_fina_reports",
        func=get_fina_reports,
        kwargs={"symbol": "688795.SH", "start_date": "20240101", "end_date": "20241231"},
    ))
    cases.append(ApiCallCase(
        category="financial",
        method="get_factor",
        func=get_factor,
        kwargs={
            "symbol": "000001.SZ",
            "start_date": "20250101",
            "end_date": "20250115",
            "factors": ["open", "close", "volume"],
        },
    ))
    cases.append(ApiCallCase(
        category="financial",
        method="get_adj_factor",
        func=get_adj_factor,
        kwargs={"symbol": "000001.SZ", "start_date": "20250101", "end_date": "20250115"},
    ))

    # ---- trade（5 个）----
    cases.append(ApiCallCase(
        category="trade",
        method="get_trade_cal",
        func=get_trade_cal,
        kwargs={"start_date": "20250101", "end_date": "20250115", "exchange": "SH"},
    ))
    cases.append(ApiCallCase(
        category="trade",
        method="get_prev_trade_date",
        func=get_prev_trade_date,
        kwargs={"date": "20250115"},
        expect_type="string",
    ))
    cases.append(ApiCallCase(
        category="trade",
        method="get_last_trade_date",
        func=get_last_trade_date,
        kwargs={},
        expect_type="string",
    ))
    cases.append(ApiCallCase(
        category="trade",
        method="get_stock_status_change",
        func=get_stock_status_change,
        kwargs={"symbol": "002217.SZ"},
    ))
    cases.append(ApiCallCase(
        category="trade",
        method="get_trade_list",
        func=get_trade_list,
        kwargs={"date": "20250115"},
    ))

    # ---- futures（3 个）----
    cases.append(ApiCallCase(
        category="futures",
        method="get_future_detail",
        func=get_future_detail,
        kwargs={"symbol": "A2501.DCE"},
    ))
    cases.append(ApiCallCase(
        category="futures",
        method="get_future_market_post",
        func=get_future_market_post,
        kwargs={"symbol": "A2501.DCE", "start_date": "20250101", "end_date": "20250115"},
    ))
    cases.append(ApiCallCase(
        category="futures",
        method="get_future_dominant",
        func=get_future_dominant,
        kwargs={"underlying_symbol": "A", "start_date": "20250101", "end_date": "20250115"},
    ))

    return cases


# ---------------------------------------------------------------------------
# 测试执行
# ---------------------------------------------------------------------------

ERROR_PREFIX: str = "API 调用失败"


def run_single_test(case: ApiCallCase) -> ApiCallResult:
    """执行单个 API 测试用例。

    Args:
        case: 测试用例。

    Returns:
        测试结果。
    """
    start: float = time.time()
    try:
        result: str = case.func(**case.kwargs)
        elapsed: float = time.time() - start

        # 检查是否为 API 调用失败
        if result.startswith(ERROR_PREFIX):
            return ApiCallResult(
                category=case.category,
                method=case.method,
                success=False,
                elapsed=elapsed,
                error=result,
            )

        # 验证返回值为非空字符串
        if not isinstance(result, str) or len(result.strip()) == 0:
            return ApiCallResult(
                category=case.category,
                method=case.method,
                success=False,
                elapsed=elapsed,
                error=f"返回值类型异常：期望非空字符串，实际为 {type(result).__name__}",
            )

        # 截取预览（前 200 字符）
        preview: str = result[:200] + ("..." if len(result) > 200 else "")

        return ApiCallResult(
            category=case.category,
            method=case.method,
            success=True,
            elapsed=elapsed,
            preview=preview,
        )

    except Exception as e:
        elapsed = time.time() - start
        return ApiCallResult(
            category=case.category,
            method=case.method,
            success=False,
            elapsed=elapsed,
            error=f"{type(e).__name__}: {e}",
        )


def run_tests(
    cases: List[ApiCallCase],
    category_filter: Optional[str] = None,
    method_filter: Optional[str] = None,
) -> ApiBatchSummary:
    """执行批量测试。

    Args:
        cases: 全部测试用例列表。
        category_filter: 按类别过滤，为 None 时不过滤。
        method_filter: 按方法名过滤，为 None 时不过滤。

    Returns:
        测试汇总统计。
    """
    # 过滤测试用例
    filtered: List[ApiCallCase] = cases
    if category_filter:
        filtered = [c for c in filtered if c.category == category_filter]
    if method_filter:
        filtered = [c for c in filtered if c.method == method_filter]

    summary = ApiBatchSummary()
    summary.total = len(filtered)

    print(f"\n{'=' * 70}")
    print(f"PandaAI 全量接口批量测试 — 共 {summary.total} 个 API")
    print(f"{'=' * 70}\n")

    for i, case in enumerate(filtered, 1):
        print(f"[{i}/{summary.total}] 测试 {case.category}/{case.method} ...", end=" ", flush=True)

        result: ApiCallResult = run_single_test(case)
        summary.results.append(result)

        if result.success:
            summary.success += 1
            print(f"✓ 成功 ({result.elapsed:.2f}s)")
        else:
            summary.failure += 1
            print(f"✗ 失败 ({result.elapsed:.2f}s)")
            print(f"    错误: {result.error}")

    return summary


def print_summary(summary: ApiBatchSummary) -> None:
    """打印测试汇总统计。

    Args:
        summary: 测试汇总统计。
    """
    print(f"\n{'=' * 70}")
    print("测试汇总")
    print(f"{'=' * 70}")
    print(f"  总数:   {summary.total}")
    print(f"  成功:   {summary.success}")
    print(f"  失败:   {summary.failure}")

    if summary.failure > 0:
        print(f"\n{'─' * 70}")
        print("失败详情:")
        print(f"{'─' * 70}")
        for r in summary.results:
            if not r.success:
                print(f"  [{r.category}] {r.method}")
                print(f"    {r.error}")

    pass_rate: float = (summary.success / summary.total * 100) if summary.total > 0 else 0
    print(f"\n通过率: {pass_rate:.1f}%")
    print(f"{'=' * 70}\n")


# ---------------------------------------------------------------------------
# Pytest 集成测试（与上方脚本共用同一套用例）
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session", autouse=True)
def _session_init_panda_credentials() -> None:
    """pytest 不会执行 ``if __name__ == '__main__'``，须在此初始化 token。"""
    if not _configure_panda_credentials():
        pytest.skip(
            "未配置凭证：请设置 PANDA_DATA_USERNAME / PANDA_DATA_PASSWORD，"
            "或添加 tests/local_credentials.py（参见 local_credentials.example.py）",
        )


@pytest.mark.parametrize(
    "case",
    build_test_cases(),
    ids=lambda c: f"{c.category}__{c.method}",
)
def test_panda_tool_api_real_call(case: ApiCallCase) -> None:
    """通过 tool 封装调用真实 API；凭证由 _session_init_panda_credentials 初始化。"""
    result = run_single_test(case)
    assert result.success, f"{case.category}/{case.method}: {result.error}"


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="PandaAI 全量接口批量测试（真实 API 调用）",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        choices=["market_data", "market_ref", "financial", "trade", "futures"],
        help="按类别过滤测试范围",
    )
    parser.add_argument(
        "--method",
        type=str,
        default=None,
        help="按方法名过滤测试范围（如 get_market_data）",
    )
    return parser.parse_args()


def main() -> None:
    """批量测试入口。"""
    if not _configure_panda_credentials():
        print(
            "错误：未配置凭证。请设置环境变量 PANDA_DATA_USERNAME / PANDA_DATA_PASSWORD，"
            "或创建 tests/local_credentials.py（参见 local_credentials.example.py）。",
            file=sys.stderr,
        )
        sys.exit(2)
    args: argparse.Namespace = parse_args()
    cases: List[ApiCallCase] = build_test_cases()

    summary: ApiBatchSummary = run_tests(
        cases,
        category_filter=args.category,
        method_filter=args.method,
    )
    print_summary(summary)

    # 有失败时以非零退出码退出
    if summary.failure > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()