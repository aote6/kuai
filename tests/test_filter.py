"""筛选块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestFilter(unittest.TestCase):
    """筛选块：契约 / 空集合 / 正常筛选 / State不污染 / 文件系统一致"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["筛选"]

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

    # ② 空集合
    def test_empty_directory(self):
        """空目录 → 筛选结果=[], 筛选数量=0"""
        state = State({
            "当前路径": self.temp_dir,
            "_扩展名": "txt",
        })
        result = self.block.execute(state)
        self.assertEqual(result["筛选结果"], [])
        self.assertEqual(result["筛选数量"], 0)

    def test_no_match(self):
        """有文件但无匹配扩展名"""
        self._make_file("a.log")
        self._make_file("b.csv")
        state = State({
            "当前路径": self.temp_dir,
            "_扩展名": "txt",
        })
        result = self.block.execute(state)
        self.assertEqual(result["筛选数量"], 0)

    # ③ 正常筛选
    def test_filter_txt(self):
        """筛选 .txt 文件"""
        self._make_file("a.txt")
        self._make_file("b.txt")
        self._make_file("c.log")

        state = State({
            "当前路径": self.temp_dir,
            "_扩展名": "txt",
        })
        result = self.block.execute(state)
        self.assertEqual(result["筛选数量"], 2)
        self.assertEqual(len(result["筛选结果"]), 2)
        for p in result["筛选结果"]:
            self.assertTrue(p.endswith(".txt"))
            self.assertTrue(os.path.isabs(p))

    # ④ 外部字段不受污染
    def test_existing_fields_preserved(self):
        """传入的额外字段应原样保留"""
        self._make_file("a.txt")
        state = State({
            "当前路径": self.temp_dir,
            "_扩展名": "txt",
            "文件列表": ["some", "existing", "data"],
            "其他字段": 42,
        })
        result = self.block.execute(state)
        self.assertEqual(result["文件列表"], ["some", "existing", "data"])
        self.assertEqual(result["其他字段"], 42)

    # ⑤ 文件系统一致性
    def test_filesystem_unchanged(self):
        """筛选是只读操作，不应修改文件系统"""
        self._make_file("a.txt", "hello")
        self._make_file("b.log", "world")

        before = set(os.listdir(self.temp_dir))

        state = State({
            "当前路径": self.temp_dir,
            "_扩展名": "txt",
        })
        self.block.execute(state)

        after = set(os.listdir(self.temp_dir))
        self.assertEqual(before, after, "筛选操作不应修改文件系统")


if __name__ == "__main__":
    unittest.main(verbosity=2)
