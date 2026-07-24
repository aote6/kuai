import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestReportBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["生成报告"]
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertEqual(self.block.input_schema, ["当前路径"])
        self.assertIn("报告路径", self.block.output_schema)
        self.assertIn("报告内容", self.block.output_schema)

    def test_generate_report(self):
        with open(os.path.join(self.dir, "a.txt"), "w") as f:
            f.write("aaa")
        with open(os.path.join(self.dir, "b.txt"), "w") as f:
            f.write("bbb")

        state = State({"当前路径": self.dir})
        result = self.block.execute(state)
        self.assertTrue(len(result["报告内容"]) > 0)
        self.assertTrue(os.path.isfile(result["报告路径"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
