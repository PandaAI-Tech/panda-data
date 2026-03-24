#!/usr/bin/env bash
# PyPI 发布脚本：构建 wheel/sdist 并上传到 Test PyPI 或正式 PyPI。
# 依赖：pip install build twine
#
# 令牌（勿提交到 git）：
#   - Test PyPI: 在 https://test.pypi.org/manage/account/token/ 创建，设置 TEST_PYPI_API_TOKEN
#   - 正式 PyPI: 在 https://pypi.org/manage/account/token/ 创建，设置 PYPI_API_TOKEN
#
# 用法：
#   ./build_and_push.sh build          # 仅清理并构建 + twine check（默认）
#   ./build_and_push.sh test           # 构建并上传到 Test PyPI
#   ./build_and_push.sh prod           # 构建并上传到正式 PyPI
#   ./build_and_push.sh clean          # 仅删除 dist/ build/ 等
#
# 发布后用户安装（与 pyproject.toml [project] name 一致）：
#   pip install panda-data-tools
#
# 安装后 Python 中 import 的是包目录名 panda_tools（非 PyPI 项目名）：
#   from panda_tools.credential import CredentialManager
#   from panda_tools.registry import ToolRegistry

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# PyPI / pip 使用的发行版名称（与 pyproject.toml [project] name 一致）
DISTRIBUTION_NAME="panda-data-tools"

clean() {
  rm -rf dist build *.egg-info
}

build_only() {
  clean
  python -m build
  twine check dist/*
  echo "构建完成: dist/"
}

upload_test() {
  export TWINE_USERNAME=__token__
  export TWINE_PASSWORD="${TEST_PYPI_API_TOKEN:?请设置环境变量 TEST_PYPI_API_TOKEN（Test PyPI API token）}"
  twine upload --repository-url https://test.pypi.org/legacy/ dist/*
  echo "已上传到 Test PyPI。本地验证安装示例："
  echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ${DISTRIBUTION_NAME}"
}

upload_prod() {
  export TWINE_USERNAME=__token__
  export TWINE_PASSWORD="${PYPI_API_TOKEN:?请设置环境变量 PYPI_API_TOKEN（PyPI API token）}"
  twine upload dist/*
  echo "已上传到 PyPI。用户安装："
  echo "  pip install ${DISTRIBUTION_NAME}"
  echo "验证导入示例："
  echo "  python -c \"from panda_tools.credential import CredentialManager; from panda_tools.registry import ToolRegistry; print('ok')\""
}

case "${1:-build}" in
  clean)
    clean
    echo "已清理 dist/、build/、*.egg-info"
    ;;
  build)
    build_only
    ;;
  test)
    build_only
    upload_test
    ;;
  prod|publish)
    build_only
    read -r -p "确认上传到正式 PyPI？(y/N) " ans
    case "$ans" in
      y|Y|yes|YES) upload_prod ;;
      *) echo "已取消"; exit 1 ;;
    esac
    ;;
  *)
    echo "用法: $0 {build|test|prod|clean}" >&2
    exit 1
    ;;
esac
