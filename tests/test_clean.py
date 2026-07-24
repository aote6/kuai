import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestCleanBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["清理"]
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertEqual(self.block.input_schema, ["当前路径"])
        self.assertIn("清理数量", self.block.output_schema)

    def test_clean_tmp_files(self):
        with open(os.path.join(self.dir, "a.tmp"), "w") as f:
            f.write("tmp")
        with open(os.path.join(self.dir, "b.txt"), "w") as f:
            f.write("keep")
        with open(os.path.join(self.dir, "c.tmp"), "w") as f:
            f.write("tmp2")

        state = State({"当前路径": self.dir})
        result = self.block.execute(state)
        self.assertEqual(result["清理数量"], 2)
        self.assertFalse(os.path.isfile(os.path.join(self.dir, "a.tmp")))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "b.txt")))

    def test_clean_nothing(self):
        with open(os.path.join(self.dir, "keep.txt"), "w") as f:
            f.write("keep")

        state = State({"当前路径": self.dir})
        result = self.block.execute(state)
        self.assertEqual(result["清理数量"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
