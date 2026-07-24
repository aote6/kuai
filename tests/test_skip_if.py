import unittest
from core.state import State
from core.engine import Engine, SkipRemainingSteps
from flow.registry import BLOCK_REGISTRY


class TestSkipIf(unittest.TestCase):
    def test_skip_when_condition_met(self):
        blocks = [BLOCK_REGISTRY["条件跳过"], BLOCK_REGISTRY["列表"]]
        state = State({"筛选数量": 0})
        state = state.with_updates(_检查字段="筛选数量", _期望值="0")
        engine = Engine(verbose=False)
        result = engine.run_sequence(blocks, state)
        self.assertNotIn("文件列表", result)

    def test_no_skip_when_condition_not_met(self):
        blocks = [BLOCK_REGISTRY["条件跳过"]]
        state = State({"筛选数量": 5})
        state = state.with_updates(_检查字段="筛选数量", _期望值="0")
        engine = Engine(verbose=False)
        result = engine.run_sequence(blocks, state)
        self.assertNotIn("_检查字段", result)
        self.assertEqual(result["筛选数量"], 5)

    def test_skip_falsy_without_expected(self):
        state = State({"筛选数量": 0})
        state = state.with_updates(_检查字段="筛选数量")
        with self.assertRaises(SkipRemainingSteps):
            BLOCK_REGISTRY["条件跳过"].execute(state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
