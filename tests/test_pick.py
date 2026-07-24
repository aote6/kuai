"""选取块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestPick(unittest.TestCase):
    """选取块：契约 / 选取文件 / 选取目录 / 不存在 / 对象类型"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["选取"]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _make_file(self, name, content=""):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    # ① 契约测试
    def test_contract_missing_fields(self):
        """缺少「当前路径」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    # ② 选取文件
    def test_pick_file(self):
        """选取一个文件：当前对象=文件路径，对象类型=文件"""
        f = self._make_file("doc.txt", "content")

        state = State({
            "当前路径": self.temp_dir,
            "_待选文件": "doc.txt",
        })
        result = self.block.execute(state)

        self.assertEqual(result["当前对象"], f)
        self.assertEqual(result["对象类型"], "文件")

    # ③ 选取目录
    def test_pick_directory(self):
        """选取一个子目录：当前对象=目录路径，对象类型=目录"""
        subdir = os.path.join(self.temp_dir, "sub")
        os.makedirs(subdir)

        state = State({
            "当前路径": self.temp_dir,
            "_待选文件": "sub",
        })
        result = self.block.execute(state)

        self.assertEqual(result["当前对象"], subdir)
        self.assertEqual(result["对象类型"], "目录")

    # ④ 目标不存在
    def test_pick_nonexistent(self):
        """选取不存在的文件应报错"""
        state = State({
            "当前路径": self.temp_dir,
            "_待选文件": "ghost.txt",
        })
        with self.assertRaises((FileNotFoundError, OSError, ValueError)):
            self.block.execute(state)

    # ⑤ 不污染外部字段
    def test_preserve_existing_fields(self):
        """选取不应修改已有字段"""
        f = self._make_file("x.txt", "x")
        state = State({
            "当前路径": self.temp_dir,
            "_待选文件": "x.txt",
            "文件列表": ["old", "data"],
            "筛选结果": ["some", "paths"],
        })
        result = self.block.execute(state)
        self.assertEqual(result["文件列表"], ["old", "data"])
        self.assertEqual(result["筛选结果"], ["some", "paths"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
