"""列表块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestList(unittest.TestCase):
    """列表块：契约 / 空目录 / 正常列表 / 只读 / 字段保留"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["列表"]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _make_file(self, name, content=""):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    # ① 契约测试
    def test_contract_missing_path(self):
        """缺少「当前路径」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    # ② 空目录
    def test_empty_directory(self):
        """空目录 → 文件列表=[], 文件数量=0"""
        state = State({"当前路径": self.temp_dir})
        result = self.block.execute(state)
        self.assertEqual(result["文件列表"], [])
        self.assertEqual(result["文件数量"], 0)

    # ③ 正常列表
    def test_list_files(self):
        """列出目录中的文件"""
        self._make_file("a.txt", "aaa")
        self._make_file("b.log", "bbb")

        state = State({"当前路径": self.temp_dir})
        result = self.block.execute(state)

        self.assertEqual(result["文件数量"], 2)
        file_list = result["文件列表"]
        self.assertIn("a.txt (文件, 3字节)", file_list)
        self.assertIn("b.log (文件, 3字节)", file_list)

    # ④ 只读操作
    def test_filesystem_unchanged(self):
        """列表是只读操作，不应修改文件系统"""
        self._make_file("x.txt", "hello")
        before = set(os.listdir(self.temp_dir))

        state = State({"当前路径": self.temp_dir})
        self.block.execute(state)

        after = set(os.listdir(self.temp_dir))
        self.assertEqual(before, after, "列表操作不应修改文件系统")

    # ⑤ 外部字段保留
    def test_preserve_existing_fields(self):
        """列表不应修改已有字段"""
        self._make_file("a.txt", "a")
        state = State({
            "当前路径": self.temp_dir,
            "筛选结果": ["important", "data"],
            "计数": 42,
        })
        result = self.block.execute(state)
        self.assertEqual(result["筛选结果"], ["important", "data"])
        self.assertEqual(result["计数"], 42)


if __name__ == "__main__":
    unittest.main(verbosity=2)
