"""批量重命名块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestBatchRename(unittest.TestCase):
    """批量重命名块：契约 / 空集合 / 正常执行 / 幂等 / State污染 / 当前对象"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["批量重命名"]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ---------- 辅助方法 ----------
    def _make_file(self, name, content=""):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _make_files(self, *names):
        for name in names:
            self._make_file(name)

    def _assert_exists(self, name):
        path = os.path.join(self.temp_dir, name)
        self.assertTrue(os.path.isfile(path), f"文件应存在: {path}")

    def _assert_not_exists(self, name):
        path = os.path.join(self.temp_dir, name)
        self.assertFalse(os.path.isfile(path), f"文件不应存在: {path}")

    # ═══════════════════════════════════════════
    # ① 契约测试
    # ═══════════════════════════════════════════

    def test_contract_missing_path(self):
        """缺少「当前路径」字段时应抛出 StateMismatchError"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    def test_contract_empty_state(self):
        """空 State 应明确报错"""
        state = State()
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    # ═══════════════════════════════════════════
    # ② 空集合测试
    # ═══════════════════════════════════════════

    def test_empty_directory(self):
        """目录为空时，重命名数量=0，不抛异常"""
        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "backup_",
            "_扩展名": "txt",
        })
        result = self.block.execute(state)
        self.assertEqual(result["重命名数量"], 0)
        self.assertEqual(result["当前对象"], [])
        self.assertEqual(result["对象类型"], "文件集合")

    def test_no_matching_extension(self):
        """目录中有文件但扩展名不匹配，重命名数量=0"""
        self._make_files("a.log", "b.log", "c.csv")
        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "backup_",
            "_扩展名": "txt",
        })
        result = self.block.execute(state)
        self.assertEqual(result["重命名数量"], 0)

    # ═══════════════════════════════════════════
    # ③ 正常执行测试
    # ═══════════════════════════════════════════

    def test_normal_execute(self):
        """正常重命名：匹配文件被加前缀，未匹配文件不变"""
        self._make_files("a.txt", "b.txt")
        self._make_file("c.log")

        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "backup_",
            "_扩展名": "txt",
        })
        result = self.block.execute(state)

        # 重命名数量
        self.assertEqual(result["重命名数量"], 2)

        # 文件系统验证
        self._assert_exists("backup_a.txt")
        self._assert_exists("backup_b.txt")
        self._assert_not_exists("a.txt")
        self._assert_not_exists("b.txt")
        self._assert_exists("c.log")  # 未匹配的保持不变

        # 当前对象
        expected = sorted([
            os.path.join(self.temp_dir, "backup_a.txt"),
            os.path.join(self.temp_dir, "backup_b.txt"),
        ])
        self.assertEqual(sorted(result["当前对象"]), expected)
        self.assertEqual(result["对象类型"], "文件集合")

    # ═══════════════════════════════════════════
    # ④ 幂等性测试
    # ═══════════════════════════════════════════

    def test_idempotent_double_execute(self):
        """连续执行两次：第二次重命名数量=0，无双重前缀"""
        self._make_files("a.txt", "b.txt")

        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "backup_",
            "_扩展名": "txt",
        })

        # 第一次
        r1 = self.block.execute(state)
        self.assertEqual(r1["重命名数量"], 2)

        # 第二次（路径不变，但文件已被重命名）
        r2 = self.block.execute(state)
        self.assertEqual(r2["重命名数量"], 0, "第二次应跳过已有前缀的文件")

        # 文件系统验证
        self._assert_exists("backup_a.txt")
        self._assert_exists("backup_b.txt")

        # 不应出现 backup_backup_*
        all_files = os.listdir(self.temp_dir)
        double_prefixed = [f for f in all_files if "backup_backup" in f]
        self.assertEqual(len(double_prefixed), 0,
                         f"出现双重前缀文件: {double_prefixed}")

    def test_idempotent_property(self):
        """is_idempotent 属性应为 False"""
        self.assertFalse(self.block.is_idempotent)

    # ═══════════════════════════════════════════
    # ⑤ State 污染测试
    # ═══════════════════════════════════════════

    def test_no_state_pollution(self):
        """「筛选结果」等外部字段不应被修改"""
        self._make_files("a.txt", "b.txt")

        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "backup_",
            "_扩展名": "txt",
            "筛选结果": ["original_a.txt", "original_b.txt"],
            "筛选数量": 2,
        })

        result = self.block.execute(state)

        self.assertEqual(result["筛选结果"], ["original_a.txt", "original_b.txt"],
                         "筛选结果不应被批量重命名修改")
        self.assertEqual(result["筛选数量"], 2)

    # ═══════════════════════════════════════════
    # ⑥ 当前对象测试
    # ═══════════════════════════════════════════

    def test_current_object_type(self):
        """当前对象应为列表，对象类型=文件集合"""
        self._make_files("x.txt", "y.txt")

        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "pre_",
            "_扩展名": "txt",
        })

        result = self.block.execute(state)

        self.assertIsInstance(result["当前对象"], list)
        self.assertEqual(len(result["当前对象"]), 2)
        self.assertEqual(result["对象类型"], "文件集合")

    def test_current_object_paths_absolute(self):
        """当前对象中的路径应为绝对路径"""
        self._make_files("test.txt")

        state = State({
            "当前路径": self.temp_dir,
            "_前缀": "p_",
            "_扩展名": "txt",
        })

        result = self.block.execute(state)
        for path in result["当前对象"]:
            self.assertTrue(os.path.isabs(path), f"路径不是绝对路径: {path}")
            self.assertTrue(path.startswith(self.temp_dir))


if __name__ == "__main__":
    unittest.main(verbosity=2)
