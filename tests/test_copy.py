"""复制块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestCopy(unittest.TestCase):
    """复制块：契约 / 文件 / 目录 / 目标不存在 / 源不存在 / 文件系统一致"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        os.makedirs(self.dest_dir)
        self.block = BLOCK_REGISTRY["复制"]

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
        """缺少「当前对象」或「目标目录」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    # ② 复制文件
    def test_copy_file(self):
        """复制单个文件：原文件保留，新文件存在"""
        src = self._make_file("a.txt", "hello")
        state = State({
            "当前对象": src,
            "对象类型": "文件",
            "目标目录": self.dest_dir,
        })
        result = self.block.execute(state)

        expected = os.path.join(self.dest_dir, "a.txt")
        self.assertEqual(result["当前对象"], expected)
        self.assertTrue(os.path.isfile(src), "原文件应保留")
        self.assertTrue(os.path.isfile(expected), "副本应存在")

    # ③ 复制目录
    def test_copy_directory(self):
        """复制整个目录：原目录保留，新目录存在"""
        subdir = os.path.join(self.temp_dir, "sub")
        os.makedirs(subdir)
        self._make_file("sub/x.txt", "x")

        state = State({
            "当前对象": subdir,
            "对象类型": "目录",
            "目标目录": self.dest_dir,
        })
        result = self.block.execute(state)

        expected = os.path.join(self.dest_dir, "sub")
        self.assertEqual(result["当前对象"], expected)
        self.assertTrue(os.path.isdir(subdir), "原目录应保留")
        self.assertTrue(os.path.isdir(expected), "副本应存在")
        self.assertTrue(os.path.isfile(os.path.join(expected, "x.txt")))

    # ④ 目标目录不存在
    def test_dest_not_exist(self):
        """目标目录不存在时应报错"""
        src = self._make_file("b.txt", "bbb")
        state = State({
            "当前对象": src,
            "对象类型": "文件",
            "目标目录": os.path.join(self.temp_dir, "nonexistent"),
        })
        with self.assertRaises((FileNotFoundError, OSError, ValueError)):
            self.block.execute(state)

    # ⑤ 源文件不存在
    def test_source_not_exist(self):
        """当前对象指向的文件不存在时应报错"""
        state = State({
            "当前对象": os.path.join(self.temp_dir, "ghost.txt"),
            "对象类型": "文件",
            "目标目录": self.dest_dir,
        })
        with self.assertRaises((FileNotFoundError, OSError)):
            self.block.execute(state)

    # ⑥ 文件系统一致性
    def test_filesystem_consistency(self):
        """复制后 State 指向新路径，原文件与新文件同时存在"""
        src = self._make_file("c.txt", "ccc")
        state = State({
            "当前对象": src,
            "对象类型": "文件",
            "目标目录": self.dest_dir,
        })
        result = self.block.execute(state)

        new_path = result["当前对象"]
        self.assertTrue(os.path.isfile(src),
                        f"原文件应保留: {src}")
        self.assertTrue(os.path.isfile(new_path),
                        f"副本应存在: {new_path}")
        self.assertNotEqual(src, new_path, "原文件和副本路径不应相同")


if __name__ == "__main__":
    unittest.main(verbosity=2)
