"""删除块测试套件"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State, StateMismatchError
from flow.registry import BLOCK_REGISTRY


class TestDelete(unittest.TestCase):
    """删除块：契约 / 单文件 / 文件集合 / 幂等 / 文件系统一致"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
        self.block = BLOCK_REGISTRY["删除"]

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
        """缺少「当前对象」应报错"""
        state = State({})
        with self.assertRaises(StateMismatchError):
            self.block.execute(state)

    # ② 删除单文件
    def test_delete_single_file(self):
        """删除单个文件：文件不存在，已删除=True，删除数量=1"""
        f = self._make_file("a.txt", "hello")
        state = State({"当前对象": f, "对象类型": "文件"})
        result = self.block.execute(state)

        self.assertTrue(result["已删除"])
        self.assertEqual(result["删除数量"], 1)
        self.assertFalse(os.path.exists(f))

    # ③ 删除文件集合
    def test_delete_file_collection(self):
        """删除文件集合：所有文件不存在，删除数量=集合大小"""
        f1 = self._make_file("x.txt", "x")
        f2 = self._make_file("y.txt", "y")
        self._make_file("z.log", "z")  # 不在集合中，不应被删

        state = State({
            "当前对象": [f1, f2],
            "对象类型": "文件集合",
        })
        result = self.block.execute(state)

        self.assertTrue(result["已删除"])
        self.assertEqual(result["删除数量"], 2)
        self.assertFalse(os.path.exists(f1))
        self.assertFalse(os.path.exists(f2))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "z.log")))

    # ④ 幂等：重复删除
    def test_idempotent_double_delete(self):
        """重复删除：第二次删除数量=0，不报错"""
        f = self._make_file("b.txt", "bbb")
        state = State({"当前对象": f, "对象类型": "文件"})

        r1 = self.block.execute(state)
        self.assertEqual(r1["删除数量"], 1)

        r2 = self.block.execute(state)
        self.assertEqual(r2["删除数量"], 0, "文件已不存在，应跳过")
        self.assertTrue(r2["已删除"])

    # ⑤ 文件系统一致性
    def test_filesystem_consistency(self):
        """删除后文件确实不存在"""
        f = self._make_file("c.txt", "ccc")
        state = State({"当前对象": f, "对象类型": "文件"})
        self.block.execute(state)
        self.assertFalse(os.path.isfile(f),
                         f"删除后文件应不存在: {f}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
