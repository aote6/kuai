import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestDateSortBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["按日期分类"]
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertIn("筛选结果", self.block.input_schema)
        self.assertIn("当前路径", self.block.input_schema)
        self.assertIn("分类数量", self.block.output_schema)

    def test_date_sort(self):
        with open(os.path.join(self.dir, "a.txt"), "w") as f:
            f.write("a")
        with open(os.path.join(self.dir, "b.txt"), "w") as f:
            f.write("b")

        state = State({
            "当前路径": self.dir,
            "筛选结果": [
                os.path.join(self.dir, "a.txt"),
                os.path.join(self.dir, "b.txt"),
            ],
        })
        result = self.block.execute(state)
        self.assertGreaterEqual(result["分类数量"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
