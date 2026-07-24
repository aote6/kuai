from datetime import datetime
from core.state import State

def _do_now(state: State) -> State:
    now = datetime.now()
    return state.with_updates(
        当前时间=now.strftime("%H:%M:%S"),
        当前日期=now.strftime("%Y-%m-%d"),
        时间戳=int(now.timestamp()),
    )
