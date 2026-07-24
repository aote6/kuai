import random
import string
from core.state import State

def _do_random(state: State) -> State:
    return state.with_updates(
        随机整数=str(random.randint(1, 100)),
        随机密码=''.join(random.choices(string.ascii_letters + string.digits, k=12)),
    )
