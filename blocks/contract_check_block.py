"""
契约检查块 —— 把定界的数值契约包装成kuai的Block
"""
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/dingjie')
from invariants.value_predicates.range_consistency import pairwise_le
import sympy as sp
from core.state import State, StateMismatchError


def check_min_le_max(state: State) -> State:
    dmin, dmax = state['damage_min'], state['damage_max']
    a, b = sp.symbols('a b', integer=True)
    violation = sp.And(sp.Eq(a, dmin), sp.Eq(b, dmax))
    invariant = pairwise_le(a, b)
    if sp.simplify(sp.And(violation, sp.Not(invariant))) != False:
        raise StateMismatchError(f"契约违反: damage_min({dmin}) > damage_max({dmax})")
    return state
