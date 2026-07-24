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
    blocks_only = []
    for block, injections in executable:
        if injections:
            current_state = current_state.with_updates(**injections)
        blocks_only.append(block)

    final_state = engine.run_sequence(blocks_only, current_state)
    return final_state
