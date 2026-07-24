"""压缩块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestZip(unittest.TestCase):
    """压缩块：契约 / 单文件 / 文件集合 / 对象类型转换"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["压缩"]

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
        """缺少「当前对象」或「对象类型」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

        state2 = State({"当前对象": "/some/path"})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state2)

    # ② 单文件压缩
    def test_single_file_zip(self):
        """压缩单个文件"""
        f = self._make_file("doc.txt", "hello world")

        state = State({
            "当前对象": f,
            "对象类型": "文件",
        })
        result = self.block.execute(state)

        expected_zip = f + ".zip"
        self.assertEqual(result["当前对象"], expected_zip)
        self.assertEqual(result["对象类型"], "压缩包")
        self.assertTrue(os.path.isfile(expected_zip))

        # 验证 zip 内容
        with zipfile.ZipFile(expected_zip, "r") as zf:
            names = zf.namelist()
            self.assertIn("doc.txt", names)

    # ③ 文件集合压缩
    def test_file_collection_zip(self):
        """压缩文件集合"""
        f1 = self._make_file("a.txt", "aaa")
        f2 = self._make_file("b.txt", "bbb")
        self._make_file("c.log", "ccc")  # 不在集合中

        state = State({
            "当前对象": [f1, f2],
            "对象类型": "文件集合",
        })
        result = self.block.execute(state)

        self.assertEqual(result["对象类型"], "压缩包")
        self.assertTrue(result["当前对象"].endswith(".zip"))
        self.assertTrue(os.path.isfile(result["当前对象"]))

        # 验证 zip 内容
        with zipfile.ZipFile(result["当前对象"], "r") as zf:
            names = zf.namelist()
            self.assertIn("a.txt", names)
            self.assertIn("b.txt", names)
            self.assertNotIn("c.log", names)

    # ④ 空集合报错
    def test_empty_collection_error(self):
        """空文件集合应报错"""
        state = State({
            "当前对象": [],
            "对象类型": "文件集合",
        })
        with self.assertRaises(ValueError):
            self.block.execute(state)

    # ⑤ 对象类型转换验证
    def test_type_transition(self):
        """压缩后对象类型从 文件→压缩包"""
        f = self._make_file("x.txt", "x")
        state = State({
            "当前对象": f,
            "对象类型": "文件",
        })
        result = self.block.execute(state)
        self.assertEqual(result["对象类型"], "压缩包")
        self.assertNotEqual(result["当前对象"], f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
