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

    blocks = []
    for line_num, line in enumerate(body_lines, start=2):
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

        blocks.append({
            "name": name,
            "arg": positional_arg,
            "named_args": named_args,
            "line": line_num,
        })

    return {"task": task_name, "blocks": blocks}
