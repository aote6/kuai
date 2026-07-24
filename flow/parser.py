import re


class FlowParseError(Exception):
    pass


def parse_flow(text: str) -> dict:
    lines = [line.strip() for line in text.strip().splitlines()]
    lines = [line for line in lines if line]

    if not lines:
        raise FlowParseError("空的flow文件")

    first = lines[0]
    m = re.match(r"^任务\s+(\S.*)$", first)
    if not m:
        raise FlowParseError(f"第一行必须是 '任务 <名称>'，实际: '{first}'")
    task_name = m.group(1).strip()

    last = lines[-1]
    if last != "结束":
        raise FlowParseError(f"最后一行必须是 '结束'，实际: '{last}'")

    body_lines = lines[1:-1]
    if not body_lines:
        raise FlowParseError(f"任务 '{task_name}' 没有任何块")

    variables = {}
    block_lines = []
    for line in body_lines:
        m = re.match(r"^变量\s+(\S+)=(\S.*)$", line)
        if m:
            var_name = m.group(1)
            var_value = m.group(2)
            if var_name in variables:
                raise FlowParseError(f"变量 '{var_name}' 重复声明")
            variables[var_name] = var_value
        else:
            block_lines.append(line)

    blocks = []
    for line_num_offset, line in enumerate(block_lines):
        line_num = line_num_offset + 2  # 保持原始行号
        parts = line.split(None, 1)
        name = parts[0]
        args_raw = parts[1].strip() if len(parts) > 1 else ""

        # 解析 key=value 对
        named_args = {}
        positional_arg = None
        if args_raw:
            for token in args_raw.split():
                if "=" in token:
                    k, v = token.split("=", 1)
                    named_args[k.strip()] = v.strip()
                else:
                    positional_arg = token

        # 变量替换：位置参数和具名参数的值如果在变量表中，替换为变量值
        if positional_arg and positional_arg in variables:
            positional_arg = variables[positional_arg]
        for k, v in named_args.items():
            if v in variables:
                named_args[k] = variables[v]

        blocks.append({
            "name": name,
            "arg": positional_arg,
            "named_args": named_args,
            "line": line_num,
        })

    return {"task": task_name, "variables": variables, "blocks": blocks}
