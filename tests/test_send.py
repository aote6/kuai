import os
import tempfile
import unittest
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestSendBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["发送"]
        self.tmp = tempfile.TemporaryDirectory()
        self.dst = os.path.join(self.tmp.name, "out")
        self.file = os.path.join(self.tmp.name, "data.txt")
        with open(self.file, "w") as f:
            f.write("sending data")

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertIn("当前对象", self.block.input_schema)
        self.assertIn("当前对象", self.block.output_schema)

    def test_send_file(self):
        state = State({
            "当前对象": self.file,
            "对象类型": "文件",
            "目标目录": self.dst,
        })
        result = self.block.execute(state)
        self.assertTrue(result["完成"])
        dest_path = os.path.join(self.dst, "data.txt")
        self.assertEqual(result["当前对象"], dest_path)
        self.assertTrue(os.path.isfile(dest_path))

    def test_type_preserved(self):
        """发送不应改变对象类型"""
        state = State({
            "当前对象": self.file,
            "对象类型": "压缩包",
            "目标目录": self.dst,
        })
        result = self.block.execute(state)
        self.assertEqual(result["对象类型"], "压缩包",
                         "发送不应改变对象类型")


if __name__ == "__main__":
    unittest.main(verbosity=2)
