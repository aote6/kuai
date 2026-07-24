import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestVariableRoundtrip(unittest.TestCase):
    def test_set_then_get(self):
        state = State({"文件数量": 5})
        state = state.with_updates(_设置键="图片数量", _设置值=state["文件数量"])
        state = BLOCK_REGISTRY["设置变量"].execute(state)
        self.assertEqual(state["图片数量"], 5)
        self.assertNotIn("_设置键", state)
        self.assertNotIn("_设置值", state)

        state = state.with_updates(_取键="图片数量", _取目标键="备份数量")
        state = BLOCK_REGISTRY["取变量"].execute(state)
        self.assertEqual(state["备份数量"], 5)
        self.assertNotIn("_取键", state)
        self.assertNotIn("_取目标键", state)

    def test_get_missing_key_errors(self):
        state = State({"_取键": "不存在的字段", "_取目标键": "x"})
        with self.assertRaises(Exception):
            BLOCK_REGISTRY["取变量"].execute(state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
