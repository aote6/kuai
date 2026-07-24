import subprocess
from core.state import State

def _do_shell(state: State) -> State:
    cmd = state["命令"]
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout or result.stderr
        code = result.returncode
    except Exception as e:
        output = str(e)
        code = -1
    return state.with_updates(命令输出=output, 退出码=code)
