import importlib
import os
from core.block import Block


def _parse_block_def(text: str) -> dict:
    """解析 .block 文件，返回块定义字典"""
    lines = text.strip().split("\n")
    result = {
        "name": None,
        "input_schema": [],
        "output_schema": [],
        "output_constants": {},
        "params": [],
        "properties": {},
        "execute": None,
    }

    section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("块 "):
            result["name"] = line[2:].strip()
            section = None
        elif line == "输入:":
            section = "input"
        elif line == "输出:":
            section = "output"
        elif line == "参数:":
            section = "params"
        elif line == "属性:":
            section = "properties"
        elif line == "执行:":
            section = "execute"
        elif section == "input":
            result["input_schema"].append(line)
        elif section == "output":
            if "=" in line:
                key, val = line.split("=", 1)
                result["output_constants"][key.strip()] = val.strip()
            else:
                result["output_schema"].append(line)
        elif section == "params":
            if "->" in line:
                ext, _int = line.split("->", 1)
                result["params"].append((ext.strip(), _int.strip()))
        elif section == "properties":
            if ":" in line:
                key, val = line.split(":", 1)
                result["properties"][key.strip()] = val.strip()
        elif section == "execute":
            result["execute"] = line.strip()

    return result


def _load_execute_func(execute_str: str):
    """从 python://module:func 字符串加载执行函数"""
    if not execute_str.startswith("python://"):
        raise ValueError(f"不支持的执行协议: {execute_str}")
    path = execute_str[len("python://"):]
    module_name, func_name = path.rsplit(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def load_all_blocks(block_defs_dir: str) -> dict:
    """加载所有 .block 定义文件，返回 {块名: Block} 字典"""
    registry = {}
    for fname in os.listdir(block_defs_dir):
        if not fname.endswith(".block"):
            continue
        filepath = os.path.join(block_defs_dir, fname)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        parsed = _parse_block_def(text)
        execute_func = _load_execute_func(parsed["execute"])

        # 合并输出字段与输出常量字段作为完整 output_schema
        full_output_schema = parsed["output_schema"] + list(parsed["output_constants"].keys())

        block = Block(
            name=parsed["name"],
            input_schema=parsed["input_schema"],
            output_schema=full_output_schema,
            execute_func=execute_func,
            param_inject_keys=parsed["params"],
            properties=parsed["properties"],
        )
        block.output_constants = parsed["output_constants"]
        registry[parsed["name"]] = block

    return registry
