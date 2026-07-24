"""流程级集成测试 — 验证块链协作"""
import os
import sys
import unittest
import tempfile
import shutil
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestFlowIntegration(unittest.TestCase):
    """验证多条完整流程的端到端行为"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_flow_")
        self.archive_dir = os.path.join(self.temp_dir, "archive")
        os.makedirs(self.archive_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _make_file(self, name, content=""):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _enter(self, state):
        """进入目录"""
        s = state.with_updates(_待进入路径=self.temp_dir)
        return BLOCK_REGISTRY["进入"].execute(s)

    def _run_flow(self, blocks_with_injections):
        """执行一系列块，返回最终 State"""
        state = State()
        for block_name, injections in blocks_with_injections:
            if injections:
                state = state.with_updates(**injections)
            state = BLOCK_REGISTRY[block_name].execute(state)
        return state

    # ═══════════════════════════════════════
    # 流程 1: 筛选 → 批量重命名 → 压缩 → 移动
    # ═══════════════════════════════════════

    def test_flow_filter_rename_zip_move(self):
        """核心对象链：txt 筛选 → 加前缀 → 压缩 → 归档"""
        self._make_file("a.txt", "aaa")
        self._make_file("b.txt", "bbb")
        self._make_file("c.log", "ccc")

        final = self._run_flow([
            ("进入", {"_待进入路径": self.temp_dir}),
            ("列表", {}),
            ("筛选", {"_扩展名": "txt"}),
            ("批量重命名", {"_前缀": "backup_", "_扩展名": "txt"}),
            ("压缩", {}),
            ("移动", {"目标目录": self.archive_dir}),
        ])

        # 验证最终 State
        self.assertEqual(final["对象类型"], "压缩包")
        self.assertTrue(final["当前对象"].startswith(self.archive_dir))
        self.assertTrue(final["当前对象"].endswith(".zip"))

        # 验证文件系统
        # 原文件已被重命名
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, "backup_a.txt")))
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, "backup_b.txt")))
        # 未匹配的文件不变
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, "c.log")))
        # zip 在 archive 中
        self.assertTrue(os.path.isfile(final["当前对象"]))

        # 验证 zip 内容
        with zipfile.ZipFile(final["当前对象"], "r") as zf:
            names = zf.namelist()
            self.assertIn("backup_a.txt", names)
            self.assertIn("backup_b.txt", names)

    # ═══════════════════════════════════════
    # 流程 2: 选取 → 复制 → 重命名
    # ═══════════════════════════════════════

    def test_flow_pick_copy_rename(self):
        """选取单个文件 → 复制到子目录 → 重命名"""
        self._make_file("original.txt", "hello world")
        subdir = os.path.join(self.temp_dir, "sub")
        os.makedirs(subdir)

        final = self._run_flow([
            ("进入", {"_待进入路径": self.temp_dir}),
            ("选取", {"_待选文件": "original.txt"}),
            ("复制", {"目标目录": subdir}),
            ("重命名", {"新名称": "renamed.txt"}),
        ])

        # 验证最终 State
        expected = os.path.join(subdir, "renamed.txt")
        self.assertEqual(final["当前对象"], expected)
        self.assertEqual(final["对象类型"], "文件")

        # 验证文件系统
        # 原文件还在
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, "original.txt")))
        # 复制并重命名后的文件存在
        self.assertTrue(os.path.isfile(expected))
        # 中间文件名不存在
        self.assertFalse(os.path.isfile(os.path.join(subdir, "original.txt")))

    # ═══════════════════════════════════════
    # 流程 3: 筛选结果不被中间块污染
    # ═══════════════════════════════════════

    def test_flow_screen_result_not_polluted(self):
        """筛选结果在整个流程中应保持原始值"""
        self._make_file("x.txt", "x")
        self._make_file("y.txt", "y")
        self._make_file("z.log", "z")

        final = self._run_flow([
            ("进入", {"_待进入路径": self.temp_dir}),
            ("列表", {}),
            ("筛选", {"_扩展名": "txt"}),
            ("批量重命名", {"_前缀": "pre_", "_扩展名": "txt"}),
        ])

        # 筛选结果应仍指向原始文件名，而非重命名后的
        for path in final["筛选结果"]:
            basename = os.path.basename(path)
            self.assertFalse(basename.startswith("pre_"),
                             f"筛选结果被污染: {basename}")

    # ═══════════════════════════════════════
    # 流程 4: 流程幂等性 — 连续执行两次
    # ═══════════════════════════════════════

    def test_flow_idempotent_double_run(self):
        """同一流程执行两次：第二次应跳过已处理文件，文件系统状态稳定"""
        self._make_file("a.txt", "aaa")
        self._make_file("b.txt", "bbb")
        self._make_file("c.log", "ccc")

        flow = [
            ("进入", {"_待进入路径": self.temp_dir}),
            ("列表", {}),
            ("筛选", {"_扩展名": "txt"}),
            ("批量重命名", {"_前缀": "bk_", "_扩展名": "txt"}),
        ]

        # 第一次执行
        r1 = self._run_flow(flow)
        self.assertEqual(r1["重命名数量"], 2)

        # 第二次执行（重新进入，因为 State 可能已被清理）
        r2 = self._run_flow(flow)
        self.assertEqual(r2["重命名数量"], 0, "第二次应跳过已有前缀的文件")

        # 文件系统不应有双重前缀
        all_files = os.listdir(self.temp_dir)
        double = [f for f in all_files if "bk_bk_" in f]
        self.assertEqual(len(double), 0, f"出现双重前缀: {double}")

    # ═══════════════════════════════════════
    # 流程 5: 对象类型转换链
    # ═══════════════════════════════════════

    def test_flow_object_type_transitions(self):
        """验证对象类型在流程中的转换：文件集合 → 压缩包"""
        self._make_file("a.txt", "aaa")
        self._make_file("b.txt", "bbb")

        # 记录每个阶段的「当前对象」和「对象类型」
        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)

        state = BLOCK_REGISTRY["列表"].execute(state)

        state = state.with_updates(_扩展名="txt")
        state = BLOCK_REGISTRY["筛选"].execute(state)
        # 筛选后：无当前对象（筛选不产生当前对象）

        state = state.with_updates(_前缀="arc_", _扩展名="txt")
        state = BLOCK_REGISTRY["批量重命名"].execute(state)
        self.assertEqual(state["对象类型"], "文件集合")
        self.assertIsInstance(state["当前对象"], list)

        state = BLOCK_REGISTRY["压缩"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")
        self.assertTrue(state["当前对象"].endswith(".zip"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

    # ═══════════════════════════════════════
    # 流程 6: 移动不改变对象类型
    # ═══════════════════════════════════════

    def test_move_preserves_zip_type(self):
        """移动压缩包后，对象类型仍为压缩包"""
        self._make_file("a.txt", "aaa")
        
        # 先产生一个压缩包
        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_待选文件="a.txt")
        state = BLOCK_REGISTRY["选取"].execute(state)
        state = BLOCK_REGISTRY["压缩"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")

        # 移动
        state = state.with_updates(目标目录=self.archive_dir)
        state = BLOCK_REGISTRY["移动"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包",
                         "移动不应改变压缩包的对象类型")

    # ═══════════════════════════════════════
    # 流程 7: 复制不改变对象类型
    # ═══════════════════════════════════════

    def test_copy_preserves_zip_type(self):
        """复制压缩包后，对象类型仍为压缩包"""
        self._make_file("b.txt", "bbb")
        
        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_待选文件="b.txt")
        state = BLOCK_REGISTRY["选取"].execute(state)
        state = BLOCK_REGISTRY["压缩"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")

        state = state.with_updates(目标目录=self.archive_dir)
        state = BLOCK_REGISTRY["复制"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包",
                         "复制不应改变压缩包的对象类型")

    # ═══════════════════════════════════════
    # 流程 8: 重命名不改变对象类型
    # ═══════════════════════════════════════

    def test_rename_preserves_zip_type(self):
        """重命名压缩包后，对象类型仍为压缩包"""
        self._make_file("c.txt", "ccc")
        
        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_待选文件="c.txt")
        state = BLOCK_REGISTRY["选取"].execute(state)
        state = BLOCK_REGISTRY["压缩"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")

        state = state.with_updates(新名称="renamed.zip")
        state = BLOCK_REGISTRY["重命名"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包",
                         "重命名不应改变压缩包的对象类型")
