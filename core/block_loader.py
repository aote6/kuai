import re
import importlib
from core.block import Block


class BlockDefParseError(Exception):
    pass


class BlockDefLoadError(Exception):
    pass


def _parse_block_def_text(text: str, source_path: str) -> dict:
    lines = [line.rstrip() for line in text.splitlines()]
    lines = [line for line in lines if line.strip()]

    if not lines:
        raise BlockDefParseError(f"{source_path}: 空的块定义文件")

    m = re.match(r"^块\s+(\S.*)$", lines[0].strip())
    if not m:
        raise BlockDefParseError(f"{source_path}: 第1行必须是 '块 <名称>'")
    name = m.group(1).strip()

    section = None
    input_fields = []
    output_fields = []
    output_constants = {}
    param_inject_keys = []  # 改为列表: [(外部名, 内部State字段), ...]
    exec_line = None

    for i, raw in enumerate(lines[1:], start=2):
        stripped = raw.strip()
        if stripped in ("输入:", "输出:", "参数:", "执行:"):
            section = stripped[:-1]
            continue
        if section is None:
            raise BlockDefParseError(
                f"{source_path}:{i}: 内容出现在任何 输入:/输出:/参数:/执行: 段落之前"
            )

        if section == "输入":
            input_fields.append(stripped)
        elif section == "输出":
            if "=" in stripped:
                key, val = stripped.split("=", 1)
                output_constants[key.strip()] = val.strip()
            else:
                output_fields.append(stripped)
        elif section == "参数":
            # 格式: <外部名> -> <内部State字段名>
            m3 = re.match(r"^(\S+)\s*->\s*(\S+)$", stripped)
            if not m3:
                raise BlockDefParseError(
                    f"{source_path}:{i}: 参数行格式错误，应为 '<外部名> -> <内部State字段>'，实际: '{stripped}'"
                )
            param_inject_keys.append((m3.group(1), m3.group(2)))
        elif section == "执行":
            exec_line = stripped

    if exec_line is None:
        raise BlockDefParseError(f"{source_path}: 缺少 '执行:' 段落")

    m2 = re.match(r"^python://([\w\.]+):(\w+)$", exec_line)
    if not m2:
        raise BlockDefParseError(
            f"{source_path}: 执行体格式错误，应为 'python://模块路径:函数名'，实际: '{exec_line}'"
        )
    exec_module, exec_func = m2.group(1), m2.group(2)

    return {
        "name": name,
        "input_fields": input_fields,
        "output_fields": output_fields,
        "output_constants": output_constants,
        "param_inject_keys": param_inject_keys,
        "exec_module": exec_module,
        "exec_func": exec_func,
    }


def load_block_from_file(filepath: str) -> Block:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    spec = _parse_block_def_text(text, filepath)

    try:
        module = importlib.import_module(spec["exec_module"])
    except ImportError as e:
        raise BlockDefLoadError(
            f"{filepath}: 无法加载模块 '{spec['exec_module']}': {e}"
        )

    if not hasattr(module, spec["exec_func"]):
        raise BlockDefLoadError(
            f"{filepath}: 模块 '{spec['exec_module']}' 中找不到函数 '{spec['exec_func']}'"
        )

    execute_func = getattr(module, spec["exec_func"])
    output_schema = spec["output_fields"] + list(spec["output_constants"].keys())

    block = Block(
        name=spec["name"],
        input_schema=spec["input_fields"],
        output_schema=output_schema,
        execute_func=execute_func,
    )
    block.output_constants = spec["output_constants"]
    block.param_inject_keys = spec["param_inject_keys"]  # 改为列表
    return block


def load_all_blocks(block_defs_dir: str) -> dict:
    import os

    registry = {}
    for fname in os.listdir(block_defs_dir):
        if not fname.endswith(".block"):
            continue
        filepath = os.path.join(block_defs_dir, fname)
        block = load_block_from_file(filepath)
        if block.name in registry:
            raise BlockDefLoadError(
                f"{filepath}: 块名 '{block.name}' 与已加载的块重复"
            )
        registry[block.name] = block
    return registry
