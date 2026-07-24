import urllib.request
import json
from core.state import State

def _do_http_get(state: State) -> State:
    url = state["URL"]
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except Exception as e:
        body = str(e)
        status = 0
    return state.with_updates(响应内容=body, 状态码=status)
