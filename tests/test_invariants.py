"""系统不变量测试 — 验证跨 Block 的设计约束"""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestInvariants(unittest.TestCase):
    """这些测试守护 Kuai 的系统级设计规则，而非单个 Block 的实现细节"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_inv_")
        self.archive_dir = os.path.join(self.temp_dir, "archive")
        os.makedirs(self.archive_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _make_file(self, name, content="test"):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _make_zip_state(self):
        """构造一个「当前对象为压缩包」的 State"""
        self._make_file("a.txt", "aaa")

        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_待选文件="a.txt")
        state = BLOCK_REGISTRY["选取"].execute(state)
        state = BLOCK_REGISTRY["压缩"].execute(state)

        self.assertEqual(state["对象类型"], "压缩包",
                         "前置条件：压缩后对象类型应为压缩包")
        return state

    # ═══════════════════════════════════════
    # 不变量 1-3: 移动/复制/重命名不改变对象类型
    # ═══════════════════════════════════════

    def test_move_preserves_object_type(self):
        """移动压缩包后，对象类型仍为压缩包"""
        state = self._make_zip_state()
        state = state.with_updates(目标目录=self.archive_dir)
        state = BLOCK_REGISTRY["移动"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")

    def test_copy_preserves_object_type(self):
        """复制压缩包后，对象类型仍为压缩包"""
        state = self._make_zip_state()
        state = state.with_updates(目标目录=self.archive_dir)
        state = BLOCK_REGISTRY["复制"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")

    def test_rename_preserves_object_type(self):
        """重命名压缩包后，对象类型仍为压缩包"""
        state = self._make_zip_state()
        state = state.with_updates(新名称="renamed.zip")
        state = BLOCK_REGISTRY["重命名"].execute(state)
        self.assertEqual(state["对象类型"], "压缩包")

    # ═══════════════════════════════════════
    # 不变量 4: 当前对象必须存在
    # ═══════════════════════════════════════

    def test_current_object_exists(self):
        """任何块执行后，当前对象指向的路径必须真实存在"""
        state = self._make_zip_state()
        self.assertTrue(os.path.exists(state["当前对象"]),
                        f"当前对象应存在: {state['当前对象']}")

    # ═══════════════════════════════════════
    # 不变量 5: 当前对象必须是绝对路径
    # ═══════════════════════════════════════

    def test_current_object_is_absolute(self):
        """当前对象必须是绝对路径"""
        state = self._make_zip_state()
        self.assertTrue(os.path.isabs(state["当前对象"]),
                        f"当前对象应为绝对路径: {state['当前对象']}")

    # ═══════════════════════════════════════
    # 不变量 6: 只读块不修改文件系统
    # ═══════════════════════════════════════

    def test_filter_is_read_only(self):
        """筛选块不应修改文件系统"""
        self._make_file("x.txt", "x")
        self._make_file("y.log", "y")

        before = set(os.listdir(self.temp_dir))

        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_扩展名="txt")
        state = BLOCK_REGISTRY["筛选"].execute(state)

        after = set(os.listdir(self.temp_dir))
        self.assertEqual(before, after, "筛选是只读操作")

    def test_list_is_read_only(self):
        """列表块不应修改文件系统"""
        self._make_file("a.txt", "a")

        before = set(os.listdir(self.temp_dir))

        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = BLOCK_REGISTRY["列表"].execute(state)

        after = set(os.listdir(self.temp_dir))
        self.assertEqual(before, after, "列表是只读操作")

    # ═══════════════════════════════════════
    # 不变量 7: 进入只改变当前路径
    # ═══════════════════════════════════════

    def test_enter_only_changes_current_path(self):
        """进入块只应添加当前路径，不应修改其他字段"""
        self._make_file("keep.txt", "keep")

        state = State({"原有字段": "保持不变", "计数": 99})
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)

        self.assertEqual(state["原有字段"], "保持不变")
        self.assertEqual(state["计数"], 99)
        self.assertEqual(state["当前路径"], self.temp_dir)
        self.assertNotIn("_待进入路径", state)

    # ═══════════════════════════════════════
    # 不变量 8: 文件集合中的路径都是绝对路径
    # ═══════════════════════════════════════

    def test_file_collection_paths_are_absolute(self):
        """批量重命名产生的文件集合中，所有路径应为绝对路径"""
        self._make_file("a.txt", "a")
        self._make_file("b.txt", "b")

        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_前缀="pre_", _扩展名="txt")
        state = BLOCK_REGISTRY["批量重命名"].execute(state)

        for path in state["当前对象"]:
            self.assertTrue(os.path.isabs(path),
                            f"文件集合中的路径应为绝对路径: {path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

    # ═══════════════════════════════════════
    # 不变量 9: move 只允许修改当前对象
    # ═══════════════════════════════════════

    def test_move_only_changes_current_object(self):
        """移动块只应修改当前对象，不碰对象类型和筛选结果"""
        self._make_file("src.txt", "src")

        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_待选文件="src.txt")
        state = BLOCK_REGISTRY["选取"].execute(state)

        # 记录移动前的关键字段
        before_type = state["对象类型"]
        before_path = state["当前对象"]

        state = state.with_updates(目标目录=self.archive_dir)
        state = BLOCK_REGISTRY["移动"].execute(state)

        # 对象类型不变
        self.assertEqual(state["对象类型"], before_type)
        # 当前对象已改变（位置变了）
        self.assertNotEqual(state["当前对象"], before_path)
        # 当前对象仍存在
        self.assertTrue(os.path.exists(state["当前对象"]))

    # ═══════════════════════════════════════
    # 不变量 10: copy 只允许修改当前对象
    # ═══════════════════════════════════════

    def test_copy_only_changes_current_object(self):
        """复制块只应修改当前对象，不碰对象类型"""
        self._make_file("orig.txt", "orig")

        state = State()
        state = state.with_updates(_待进入路径=self.temp_dir)
        state = BLOCK_REGISTRY["进入"].execute(state)
        state = state.with_updates(_待选文件="orig.txt")
        state = BLOCK_REGISTRY["选取"].execute(state)

        before_type = state["对象类型"]
        before_path = state["当前对象"]

        state = state.with_updates(目标目录=self.archive_dir)
        state = BLOCK_REGISTRY["复制"].execute(state)

        self.assertEqual(state["对象类型"], before_type)
        self.assertNotEqual(state["当前对象"], before_path)
        self.assertTrue(os.path.exists(state["当前对象"]))
        # 原文件仍存在（复制不同于移动）
        self.assertTrue(os.path.exists(before_path))
