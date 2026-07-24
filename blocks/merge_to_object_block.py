from core.state import State


def _do_merge(state: State) -> State:
    files = state["筛选结果"]
    if not files:
        raise ValueError("合并为对象: 筛选结果为空，没有可操作的文件")
    return state.with_updates(当前对象=files, 对象类型="文件集合")
