Kuai

State-as-Single-Source-of-Truth DSL engine for AI-native file management.

109 tests, 0 failures. 24 blocks.

====================================================================

What is Kuai

Kuai is a file management DSL engine designed for AI agent collaboration.
It does not try to be a general-purpose programming language. Instead it
reduces complex control logic into composable atomic blocks:

1. State is the single source of truth. No second storage layer.
   All data and context flows through the State dictionary.

2. Block contracts and invariants. Each .block file declares input,
   output, and constraints. Blocks are forbidden from modifying fields
   they do not own.

3. Self-describing capabilities. BLOCK_REGISTRY exports structured
   manifests so AI agents can discover available blocks instead of
   guessing interfaces from documentation.

4. Lightweight control flow. Branching and skipping are implemented as
   standard blocks, not new syntax. Works for both numeric comparisons
   and AI semantic decisions.

====================================================================

Quick Start

  git clone https://github.com/aote6/kuai.git
  cd kuai
  python -m unittest discover tests -v

List all registered blocks:

  python tools/list_blocks.py

Query blocks by input/output:

  python tools/query_blocks.py --input 当前路径 --output 当前对象
  python tools/query_blocks.py --name 压缩

====================================================================

DSL Example

A .flow file is a plain sequence of blocks. No nested syntax.

  任务 自动打包示例

  进入 /home/project/downloads
  列表
  筛选 扩展名=jpg
  条件跳过 字段=筛选数量 期望值=0
  设置变量 键=图片数量 值=筛选数量
  压缩
  取变量 键=图片数量 存入=已处理数量

  结束

====================================================================

Architecture

  block_defs/     Block contract definitions (.block files)
  blocks/         Python implementations
  core/           State, Engine, Registry, Block
  flow/           DSL parser and runner
  tests/          109 automated tests (unit + integration + invariants)
  tools/          list_blocks.py, query_blocks.py
  docs/           Design principles, block audit table
  STATUS.md       Current project phase and priorities

====================================================================

Block Inventory (24 blocks)

  Navigation:  进入, 选取
  Read-only:   列表, 筛选, 读取
  Modify:      复制, 移动, 重命名, 批量重命名, 删除, 清理
  Transform:   压缩, 解压, 合并为对象
  Text:        替换
  Sync:        同步, 发送
  Organize:    分类, 按日期分类, 生成报告
  Control:     条件跳过
  State:       设置变量, 取变量

====================================================================

Test System

  Level 1 - Block unit tests: contract, empty input, normal execution,
           idempotency, state pollution, filesystem consistency.
  Level 2 - Flow integration tests: object chain, roundtrip,
           double execution, variable set/get.
  Level 3 - System invariants: type preservation, absolute paths,
           read-only constraints, field ownership.

====================================================================

Design Principles

  See docs/DESIGN_PRINCIPLES.md for the full list.

  Key rules:
  - Blocks only modify fields they explicitly declare.
  - move/copy/rename must not change object type.
  - Read-only blocks must not modify the filesystem.
  - All paths in State must be absolute.
  - Repeated execution of idempotent blocks produces stable results.

====================================================================

License

  GPL-3.0
