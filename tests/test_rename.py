"""重命名块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestRename(unittest.TestCase):
    """重命名单个文件块：契约 / 正常 / 目标已存在 / 源不存在 / 文件系统一致"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["重命名"]

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
        """缺少「当前对象」或「新名称」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

        state2 = State({"当前对象": "/some/file.txt"})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state2)

    # ② 正常重命名
    def test_rename_file(self):
        """重命名文件：旧名不存在，新名存在"""
        src = self._make_file("old.txt", "content")
        state = State({
            "当前对象": src,
            "对象类型": "文件",
            "新名称": "new.txt",
        })
        result = self.block.execute(state)

        expected = os.path.join(self.temp_dir, "new.txt")
        self.assertEqual(result["当前对象"], expected)
        self.assertFalse(os.path.isfile(src), "旧文件应不存在")
        self.assertTrue(os.path.isfile(expected), "新文件应存在")

    # ③ 源文件不存在
    def test_source_not_exist(self):
        """重命名不存在的文件应报错"""
        state = State({
            "当前对象": os.path.join(self.temp_dir, "ghost.txt"),
            "对象类型": "文件",
            "新名称": "new.txt",
        })
        with self.assertRaises((FileNotFoundError, OSError)):
            self.block.execute(state)

    # ④ 文件系统一致性
    def test_filesystem_consistency(self):
        """State 指向新路径，旧路径确实不存在"""
        src = self._make_file("before.txt", "test")
        state = State({
            "当前对象": src,
            "对象类型": "文件",
            "新名称": "after.txt",
        })
        result = self.block.execute(state)

        new_path = result["当前对象"]
        self.assertTrue(os.path.isfile(new_path),
                        f"重命名后文件应存在于: {new_path}")
        self.assertFalse(os.path.isfile(src),
                         f"重命名后旧路径应不存在: {src}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
