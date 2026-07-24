"""解压块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestUnzip(unittest.TestCase):
    """解压块：契约 / 正常解压 / 类型检查 / 对象类型转换 / 文件系统一致"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["解压"]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _make_zip(self, zip_name, files):
        """创建一个测试用 zip 文件，返回路径"""
        zip_path = os.path.join(self.temp_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for fname, content in files.items():
                fpath = os.path.join(self.temp_dir, fname)
                with open(fpath, "w") as f:
                    f.write(content)
                zf.write(fpath, fname)
                os.remove(fpath)
        return zip_path

    # ① 契约测试
    def test_contract_missing_fields(self):
        """缺少「当前对象」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    def test_contract_wrong_type(self):
        """对象类型不是压缩包应报错"""
        state = State({
            "当前对象": "/some/file.txt",
            "对象类型": "文件",
        })
        with self.assertRaises(ValueError):
            self.block.execute(state)

    # ② 正常解压
    def test_unzip_single_file(self):
        """解压含单个文件的压缩包"""
        zip_path = self._make_zip("test.zip", {"a.txt": "hello"})

        state = State({
            "当前对象": zip_path,
            "对象类型": "压缩包",
        })
        result = self.block.execute(state)

        self.assertEqual(result["对象类型"], "文件集合")
        self.assertEqual(result["解压文件数"], 1)
        self.assertTrue(os.path.isdir(result["解压目录"]))
        self.assertTrue(os.path.isfile(os.path.join(result["解压目录"], "a.txt")))

    def test_unzip_multiple_files(self):
        """解压含多个文件的压缩包"""
        zip_path = self._make_zip("multi.zip", {
            "x.txt": "x",
            "y.txt": "y",
            "z.log": "z",
        })

        state = State({
            "当前对象": zip_path,
            "对象类型": "压缩包",
        })
        result = self.block.execute(state)

        self.assertEqual(result["对象类型"], "文件集合")
        self.assertEqual(result["解压文件数"], 3)
        self.assertEqual(len(result["当前对象"]), 3)
        extract_dir = result["解压目录"]
        self.assertTrue(os.path.isfile(os.path.join(extract_dir, "x.txt")))
        self.assertTrue(os.path.isfile(os.path.join(extract_dir, "y.txt")))
        self.assertTrue(os.path.isfile(os.path.join(extract_dir, "z.log")))

    # ③ 对象类型转换
    def test_type_transition(self):
        """解压后对象类型从 压缩包→文件集合"""
        zip_path = self._make_zip("type_test.zip", {"a.txt": "a"})

        state = State({
            "当前对象": zip_path,
            "对象类型": "压缩包",
        })
        result = self.block.execute(state)

        self.assertEqual(result["对象类型"], "文件集合")
        self.assertIsInstance(result["当前对象"], list)

    # ④ 文件系统一致性
    def test_filesystem_consistency(self):
        """解压后文件确实存在，当前对象路径有效"""
        zip_path = self._make_zip("fs_test.zip", {"b.txt": "bbb"})

        state = State({
            "当前对象": zip_path,
            "对象类型": "压缩包",
        })
        result = self.block.execute(state)

        for path in result["当前对象"]:
            self.assertTrue(os.path.exists(path),
                            f"解压出的文件应存在: {path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
