Kuai

State-as-Single-Source-of-Truth DSL execution engine.

109 tests, 0 failures.

====================================================================

What Kuai Is NOT

Kuai is not a file manager. The 20+ blocks currently in this repo
are test fixtures used to verify the core systems: Flow parsing,
State propagation, Block scheduling, and contract enforcement.
They exist to prove the engine works, not to define its limits.

====================================================================

What Kuai IS

Kuai is a DSL execution engine. ANY capability can be registered
as a Block. A Block is a contract (.block file) + a Python function.
The engine handles the rest: parsing, scheduling, State passing,
error handling, contract enforcement.

====================================================================

What Can Be A Block

Anything with an input and an output. Examples of domains that can
be registered as Blocks:

  AI          AI对话 AI总结 AI翻译 AI决策
  System      Shell Cron 环境变量 包管理
  Network     HTTP FTP WebSocket 邮件
  Database    SQLite MySQL 查询 写入
  Media       图片处理 视频转码 音频提取 OCR
  Cloud       S3 OSS 上传 下载
  Git         Clone Commit Push
  Docker      Build Run Stop
  Mobile      GPS 短信 相机 剪贴板 传感器
  Control     循环 重试 超时 条件分支 并行

None of these are implemented yet. They are listed to show what
the framework CAN support, not what it currently DOES.

====================================================================

How It Works

  1. Define a contract: block_defs/my_block.block
  2. Write the logic: blocks/my_block.py
  3. Use it in a flow:

     任务 示例
     进入 /path
     我的块 参数=值
     结束

  4. Run: python main_flow.py my_flow.flow

The engine enforces that every Block declares its inputs and outputs,
never modifies fields it doesn't own, and leaves State clean after
execution.

====================================================================

Current State

  109 tests, 0 failures
  24 test blocks (file operations, text, control flow)
  3-layer test system: unit + integration + invariants

  The test blocks are real and working. They prove that:
  - Contracts are enforced
  - State flows correctly between blocks
  - Idempotency works where declared
  - Filesystem and State stay in sync
  - Type preservation is maintained across transform blocks

====================================================================

Quick Start

  git clone https://github.com/aote6/kuai.git
  cd kuai
  python -m unittest discover tests -v

====================================================================

License

  GPL-3.0
