from core.state import State
from core.engine import Engine


def run_flow_file(filepath: str, verbose=True):
    from flow.parser import parse_flow
    from flow.registry import build_executable_blocks

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    parsed = parse_flow(text)
    executable = build_executable_blocks(parsed)

    if verbose:
        print(f"=== 任务: {parsed['task']} ===")

    engine = Engine(verbose=verbose)
    current_state = State()

    for block, injections in executable:
        # 注入参数
        if injections:
            current_state = current_state.with_updates(**injections)
        
        # 执行
        current_state = engine.run_sequence([block], current_state)
        
        # 清理注入的参数（下划线开头的字段）
        if injections:
            clean = {k: v for k, v in current_state.items() if k not in injections}
            current_state = State(clean)

    return current_state
