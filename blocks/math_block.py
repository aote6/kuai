from core.state import State

def _do_calc(state: State) -> State:
    expr = state["表达式"]
    try:
        result = eval(expr, {"__builtins__": {}}, {"abs": abs, "round": round, "max": max, "min": min, "sum": sum, "len": len, "int": int, "float": float})
    except Exception as e:
        result = f"错误: {e}"
    return state.with_updates(计算结果=str(result))
