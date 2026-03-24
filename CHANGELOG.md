# Changelog

本文件记录 PandaAI 金融数据 Tool 层 (`panda-data-tools`) 的所有版本变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.0.0] - 2025-07-18

### Added

- 新增 DuckDB 本地数据缓存模块 (`panda_tools/cache.py`)
  - `CacheManager` 类：支持 `save`、`read`（带过滤条件）、`clear`、`list_tables`、`close`
  - 可配置数据库路径，默认 `./panda_data_cache.duckdb`
  - DuckDB 未安装时优雅降级，记录警告日志
- 新增数据导出模块 (`panda_tools/exporter.py`)
  - `export_data` 函数：支持 CSV、Excel、DuckDB 三种格式导出
  - CSV 导出使用 UTF-8 with BOM 编码（`utf-8-sig`）
  - Excel 导出基于 openpyxl 引擎
  - DuckDB 导出为指定数据库文件的表
  - 自动创建输出目录
  - 统一错误消息格式：`"导出失败：{ErrorType}: {message}"`
- 新增属性基测试（Hypothesis）
  - 缓存存取往返一致性测试 (Property 2)
  - 缓存过滤查询正确性测试 (Property 3)
  - 缓存清除有效性测试 (Property 4)
  - 导出往返一致性测试 (Property 5)
  - 导出成功消息验证测试 (Property 6)
  - 导出失败消息格式测试 (Property 7)
  - 导出自动创建目录测试 (Property 8)
- 新增 `CHANGELOG.md` 版本变更记录
- 新增 `duckdb` 为项目依赖

### Changed

- `pyproject.toml` 添加 `duckdb` 到 dependencies
- `pyproject.toml` 添加 `[project.optional-dependencies]` test 组（pytest, hypothesis, duckdb, openpyxl）
- `README.md` 更新，补充 cache.py 和 exporter.py 模块文档

## [1.0.0] - 2025-07-01

### Added

- 初始发布，将 panda_data 包的 38 个金融数据查询 API 封装为 LLM function calling tools
- 凭证管理模块 (`panda_tools/credential.py`)
  - `CredentialManager` 类：支持环境变量配置用户名和密码
- API 返回值格式化器 (`panda_tools/formatter.py`)
  - `safe_call` 函数：统一 API 调用和错误处理
  - 错误消息格式：`"API 调用失败：{ErrorType}: {message}"`
- Tool 注册中心 (`panda_tools/registry.py`)
  - `ToolRegistry` 类：管理所有 tool 的注册和发现
- 6 个分类 Tool 模块，覆盖 38 个 API：
  - `tools/market_data.py` — 行情数据
  - `tools/market_ref.py` — 基础信息
  - `tools/financial.py` — 财务数据
  - `tools/futures.py` — 期货数据
  - `tools/trade_tools.py` — 交易工具
- 测试套件：
  - `tests/test_credential.py` — 凭证管理测试
  - `tests/test_formatter.py` — 格式化器测试
  - `tests/test_registry.py` — 注册中心测试
  - `tests/test_schema.py` — Tool schema 验证测试
  - `tests/test_all_apis.py` — 全量 API 测试
