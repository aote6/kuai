import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestReadBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["读取"]
        self.tmp = tempfile.TemporaryDirectory()
        self.file = os.path.join(self.tmp.name, "a.txt")
        with open(self.file, "w", encoding="utf-8") as f:
            f.write("hello world")

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertEqual(self.block.input_schema, ["当前对象"])
        self.assertEqual(self.block.output_schema, ["文件内容"])

    def test_read_file(self):
        state = State({"当前对象": self.file})
        result = self.block.execute(state)
        self.assertEqual(result["文件内容"], "hello world")
        self.assertEqual(result["当前对象"], self.file)

    def test_read_only(self):
        before = "hello world"
        state = State({"当前对象": self.file})
        self.block.execute(state)
        with open(self.file, "r") as f:
            after = f.read()
        self.assertEqual(before, after, "读取不应修改文件")


if __name__ == "__main__":
    unittest.main(verbosity=2)
