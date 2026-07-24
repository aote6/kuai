"""测试配置和共享 fixtures"""
import os
import sys
import tempfile
import shutil

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import State
from flow.registry import BLOCK_REGISTRY


class BlockTestCase:
    """每个 Block 测试的基类，提供通用验证方法"""
    
    def setup_method(self):
        """每个测试方法前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp(prefix="kuai_test_")
    
    def teardown_method(self):
        """每个测试方法后清理临时目录"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def make_file(self, name: str, content: str = ""):
        """在临时目录中创建文件"""
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path
    
    def make_files(self, *names):
        """批量创建空文件"""
        paths = []
        for name in names:
            paths.append(self.make_file(name))
        return paths
    
    def assert_file_exists(self, name: str):
        """断言文件存在"""
        path = os.path.join(self.temp_dir, name)
        assert os.path.isfile(path), f"文件不存在: {path}"
    
    def assert_file_not_exists(self, name: str):
        """断言文件不存在"""
        path = os.path.join(self.temp_dir, name)
        assert not os.path.isfile(path), f"文件不应存在: {path}"
    
    def assert_state_has(self, state: State, **kwargs):
        """断言 State 包含指定字段和值"""
        for key, expected in kwargs.items():
            actual = state.get(key)
            assert actual == expected, f"State[{key}] = {actual!r}, 期望 {expected!r}"
    
    def assert_state_not_has(self, state: State, *keys):
        """断言 State 不包含指定字段"""
        for key in keys:
            assert key not in state, f"State 不应包含字段: {key}"
