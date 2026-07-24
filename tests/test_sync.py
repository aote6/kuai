import os
import tempfile
import unittest
import time
from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestSyncBlock(unittest.TestCase):
    def setUp(self):
        self.block = BLOCK_REGISTRY["同步"]
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src")
        self.dst = os.path.join(self.tmp.name, "dst")
        os.makedirs(self.src)

    def tearDown(self):
        self.tmp.cleanup()

    def test_contract(self):
        self.assertEqual(self.block.input_schema, ["当前路径"])
        self.assertIn("同步数量", self.block.output_schema)
        self.assertIn("跳过数量", self.block.output_schema)

    def test_sync_new_files(self):
        with open(os.path.join(self.src, "a.txt"), "w") as f:
            f.write("aaa")
        with open(os.path.join(self.src, "b.txt"), "w") as f:
            f.write("bbb")

        state = State({
            "当前路径": self.src,
            "目标目录": self.dst,
        })
        result = self.block.execute(state)
        self.assertEqual(result["同步数量"], 2)
        self.assertEqual(result["跳过数量"], 0)
        self.assertTrue(os.path.isfile(os.path.join(self.dst, "a.txt")))
        self.assertTrue(os.path.isfile(os.path.join(self.dst, "b.txt")))

    def test_sync_skip_unchanged(self):
        with open(os.path.join(self.src, "x.txt"), "w") as f:
            f.write("xxx")
        os.makedirs(self.dst)
        with open(os.path.join(self.dst, "x.txt"), "w") as f:
            f.write("xxx")
        time.sleep(0.1)
        # touch src to make it newer
        os.utime(os.path.join(self.src, "x.txt"), None)

        state = State({
            "当前路径": self.src,
            "目标目录": self.dst,
        })
        result = self.block.execute(state)
        self.assertEqual(result["同步数量"], 1)
        self.assertEqual(result["跳过数量"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
