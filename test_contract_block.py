import importlib.util, sys, os

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

state_mod = load_module('state', 'core/state.py')
State = state_mod.State

sys.path.insert(0, '/data/data/com.termux/files/home/dingjie')
from invariants.value_predicates.range_consistency import pairwise_le
import sympy as sp

def check_min_le_max(state):
    dmin, dmax = state['damage_min'], state['damage_max']
    a, b = sp.symbols('a b', integer=True)
    invariant = pairwise_le(a, b)
    violation = sp.And(sp.Eq(a, dmin), sp.Eq(b, dmax))
    if sp.simplify(sp.And(violation, sp.Not(invariant))) != False:
        raise ValueError(f'契约违反: damage_min({dmin}) > damage_max({dmax})')
    return state

s1 = State()
s1['damage_min'] = 5
s1['damage_max'] = 10
check_min_le_max(s1)
print('合法值5/10: 通过')

s2 = State()
s2['damage_min'] = 10
s2['damage_max'] = 5
try:
    check_min_le_max(s2)
    print('错误：没拦住！')
except ValueError as e:
    print('非法值10/5: 正确拦截:', e)
