import os
from core.state import State


def _do_delete(state: State) -> State:
    target = state["当前对象"]

    if isinstance(target, list):
        deleted = 0
        for f in target:
            if os.path.exists(f):
                os.remove(f)
                deleted += 1
        return state.with_updates(已删除=True, 删除数量=deleted)
    else:
        if os.path.exists(target):
            os.remove(target)
            return state.with_updates(已删除=True, 删除数量=1)
        else:
            # 幂等：目标已不存在，视为已完成
            return state.with_updates(已删除=True, 删除数量=0)
