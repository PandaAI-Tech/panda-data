# panda-data-tools

PandaAI 金融数据 API 的 LLM Tool 封装层，将 `panda_data` 包的 38 个数据查询方法封装为符合 LLM function calling 规范的 tools。

## 安装

```bash
# 本地安装（推荐使用 uv）
uv pip install .

# 或使用 pip
pip install .
```

### 依赖说明

核心依赖：

- `pandas` — 数据处理
- `duckdb` — 本地数据缓存和 DuckDB 格式导出

可选依赖：

- `openpyxl` — Excel 格式导出（未安装时 Excel 导出返回错误提示）

## 构建分发包

```bash
uv build
```

## 使用方式

### 基本用法

```python
from panda_tools.credential import CredentialManager
from panda_tools.registry import ToolRegistry

# 1. 认证初始化（从环境变量读取凭证）
CredentialManager.init_from_env()

# 2. 获取所有 tool 定义
registry = ToolRegistry()
tools = registry.get_all_tools()

# 3. 调用指定 tool
result = registry.call_tool("get_market_data", start_date="20250101", end_date="20250110", symbol="000001.SZ")
print(result)
```

### 数据缓存

使用 `CacheManager` 将查询结果缓存到本地 DuckDB 数据库，避免重复调用远程 API：

```python
from panda_tools.cache import CacheManager

# 初始化缓存管理器（可自定义数据库路径）
cache = CacheManager(db_path="./my_cache.duckdb")

# 缓存查询结果
cache.save("get_market_data", df)

# 读取缓存数据（支持过滤条件）
cached_df = cache.read("get_market_data", symbol="000001.SZ")

# 查看所有缓存表
tables = cache.list_tables()

# 清除指定表缓存
cache.clear("get_market_data")

# 清除所有缓存
cache.clear()

# 关闭连接
cache.close()
```

### 数据导出

使用 `export_data` 将 DataFrame 导出为 CSV、Excel 或 DuckDB 格式：

```python
from panda_tools.exporter import export_data

# 导出为 CSV（UTF-8 with BOM 编码，Excel 打开中文不乱码）
result = export_data(df, "output/data.csv", format="csv")

# 导出为 Excel
result = export_data(df, "output/data.xlsx", format="excel")

# 导出为 DuckDB 表
result = export_data(df, "output/data.duckdb", format="duckdb", table_name="market_data")
```

输出目录不存在时会自动创建。

## 测试

```bash
# 运行属性基测试和单元测试（不需要 API 凭证）
uv run pytest tests/ -v

# 运行 Hypothesis 属性基测试
uv run pytest tests/ -v -k "hypothesis or property"

# 运行全量接口批量测试（需要 API 凭证）
uv run --with ./panda_data-0.1.0-py3-none-any.whl pytest tests/test_all_apis.py -v

# 按类别测试
uv run --with ./panda_data-0.1.0-py3-none-any.whl pytest tests/test_all_apis.py -v --category market_data

# 测试单个方法
uv run --with ./panda_data-0.1.0-py3-none-any.whl pytest tests/test_all_apis.py -v --method get_market_data
```

测试依赖：`pytest`、`hypothesis`、`duckdb`、`openpyxl`

## 项目结构

```
panda-data/
├── panda_tools/
│   ├── __init__.py          # 包入口
│   ├── credential.py        # 凭证管理
│   ├── registry.py          # Tool 注册中心
│   ├── formatter.py         # 返回值格式化
│   ├── cache.py             # DuckDB 本地数据缓存（v2.0.0 新增）
│   ├── exporter.py          # 数据导出 CSV/Excel/DuckDB（v2.0.0 新增）
│   └── tools/               # 按类别组织的 tool 定义
│       ├── __init__.py
│       ├── market_data.py   # 行情数据（2个方法）
│       ├── market_ref.py    # 市场参考数据（20个方法）
│       ├── financial.py     # 财务与因子（5个方法）
│       ├── trade_tools.py   # 交易工具（5个方法）
│       └── futures.py       # 期货（3个方法）
├── tests/
│   ├── __init__.py
│   ├── test_all_apis.py     # 全量接口批量测试
│   ├── test_cache.py        # 缓存模块测试（属性基 + 单元）
│   ├── test_exporter.py     # 导出模块测试（属性基 + 单元）
│   ├── test_credential.py   # 凭证管理测试
│   ├── test_formatter.py    # 格式化器测试
│   ├── test_registry.py     # 注册中心测试
│   ├── test_schema.py       # Tool schema 验证测试
│   ├── test_changelog.py    # CHANGELOG 格式测试
│   └── test_skill_content.py # SKILL.md 内容测试
├── panda-data-skill/       # ClawHub 技能包（发布用）
│   ├── SKILL.md
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── api_reference.md
│   └── scripts/
│       └── call_tool.py
├── pyproject.toml
├── CHANGELOG.md
└── README.md
```

## v2.0.0 新特性

### DuckDB 本地数据缓存

- 基于 DuckDB 的查询结果本地持久化存储
- 支持按表名存取、过滤查询、单表/全量清除
- DuckDB 未安装时自动降级，不影响现有功能

### 数据导出

- 支持 CSV（UTF-8 with BOM）、Excel（openpyxl）、DuckDB 三种格式
- 自动创建输出目录
- 统一的错误消息格式

### 属性基测试

- 使用 Hypothesis 框架编写属性基测试
- 覆盖缓存存取往返、过滤查询、清除有效性
- 覆盖导出往返一致性、成功消息、失败消息、目录自动创建

## 变更记录

详见 [CHANGELOG.md](CHANGELOG.md)。
