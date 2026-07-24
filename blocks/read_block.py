from core.state import State


def _do_read(state: State) -> State:
    filepath = state["当前对象"]
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return state.with_updates(文件内容=content)
