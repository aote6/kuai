import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestReplaceBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["替换"]
        self.tmp = tempfile.TemporaryDirectory()
        self.file = os.path.join(self.tmp.name, "doc.txt")
        with open(self.file, "w", encoding="utf-8") as f:
            f.write("hello world")

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertEqual(self.block.input_schema, ["当前对象"])
        self.assertIn("文件内容", self.block.output_schema)

    def test_replace_text(self):
        state = State({
            "当前对象": self.file,
            "_查找": "world",
            "_替换": "kuai",
        })
        result = self.block.execute(state)
        self.assertEqual(result["文件内容"], "hello kuai")
        with open(self.file, "r") as f:
            self.assertEqual(f.read(), "hello kuai")

    def test_no_match(self):
        state = State({
            "当前对象": self.file,
            "_查找": "xyz",
            "_替换": "abc",
        })
        result = self.block.execute(state)
        self.assertEqual(result["文件内容"], "hello world")

    def test_filesystem_consistency(self):
        state = State({
            "当前对象": self.file,
            "_查找": "hello",
            "_替换": "hi",
        })
        result = self.block.execute(state)
        with open(self.file, "r") as f:
            self.assertEqual(f.read(), result["文件内容"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
