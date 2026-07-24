"""进入块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestEnter(unittest.TestCase):
    """进入块：契约 / 正常进入 / 清理_待进入路径 / 路径不存在"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["进入"]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ① 契约测试
    def test_contract_missing_path(self):
        """缺少「_待进入路径」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    # ② 正常进入
    def test_enter_valid_directory(self):
        """正常进入：当前路径更新，_待进入路径被清理"""
        state = State({"_待进入路径": self.temp_dir})
        result = self.block.execute(state)

        self.assertEqual(result["当前路径"], self.temp_dir)
        self.assertNotIn("_待进入路径", result,
                         "_待进入路径应在执行后被移除")

    # ③ 路径不存在
    def test_enter_nonexistent(self):
        """进入不存在的路径应报错"""
        state = State({"_待进入路径": "/nonexistent/path/xyz"})
        with self.assertRaises((FileNotFoundError, OSError, NotADirectoryError)):
            self.block.execute(state)

    # ④ 路径是文件而非目录
    def test_enter_file_not_dir(self):
        """进入一个文件路径应报错"""
        f = os.path.join(self.temp_dir, "test.txt")
        with open(f, "w") as fh:
            fh.write("hello")

        state = State({"_待进入路径": f})
        with self.assertRaises((NotADirectoryError, OSError)):
            self.block.execute(state)

    # ⑤ 不污染其他字段
    def test_preserve_existing_fields(self):
        """进入操作不应影响 State 中的其他字段"""
        state = State({
            "_待进入路径": self.temp_dir,
            "现有字段": "保持原样",
            "计数": 99,
        })
        result = self.block.execute(state)
        self.assertEqual(result["现有字段"], "保持原样")
        self.assertEqual(result["计数"], 99)


if __name__ == "__main__":
    unittest.main(verbosity=2)
