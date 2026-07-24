from core.state import State

def _a(state):
    return state.with_updates(文件数量=10)

def _b(state):
    return state.with_updates(文件数量=20)
