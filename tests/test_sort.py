import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestSortBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["分类"]
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertEqual(self.block.input_schema, ["当前路径"])
        self.assertIn("分类数量", self.block.output_schema)

    def test_sort_by_extension(self):
        with open(os.path.join(self.dir, "a.txt"), "w") as f:
            f.write("a")
        with open(os.path.join(self.dir, "b.txt"), "w") as f:
            f.write("b")
        with open(os.path.join(self.dir, "c.png"), "w") as f:
            f.write("c")

        state = State({"当前路径": self.dir})
        result = self.block.execute(state)
        self.assertGreaterEqual(result["分类数量"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
