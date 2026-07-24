import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestSetVarBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["设置变量"]

    def test_contract(self):
        self.assertIn("_设置键", self.block.input_schema)
        self.assertIn("_设置值", self.block.input_schema)

    def test_set_variable(self):
        state = State({
            "_设置键": "项目路径",
            "_设置值": "/tmp/test_project",
        })
        result = self.block.execute(state)
        self.assertEqual(result["项目路径"], "/tmp/test_project")


if __name__ == "__main__":
    unittest.main(verbosity=2)
