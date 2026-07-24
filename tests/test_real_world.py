# -*- coding: utf-8 -*-
import os as _os
import sys
import unittest
import tempfile
import shutil
import zipfile

sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from core.state import State
from flow.registry import BLOCK_REGISTRY


class TestRealWorldScenario(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='kuai_real_')
        self.project_a = _os.path.join(self.root, 'project_a')
        self.project_b = _os.path.join(self.root, 'project_b')
        self.backup_dir = _os.path.join(self.root, 'backup')
        self.archive_dir = _os.path.join(self.root, 'archive')
        _os.makedirs(self.project_a)
        _os.makedirs(self.project_b)
        _os.makedirs(self.backup_dir)
        _os.makedirs(self.archive_dir)

    def tearDown(self):
        if _os.path.exists(self.root):
            shutil.rmtree(self.root)

    def _make_file(self, path, content=''):
        with open(path, 'w') as f:
            f.write(content)
        return path

    def _run_flow(self, steps, initial_state=None):
        state = initial_state or State()
        for block_name, injections in steps:
            if injections:
                state = state.with_updates(**injections)
            state = BLOCK_REGISTRY[block_name].execute(state)
        return state

    def test_organize_and_archive(self):
        self._make_file(_os.path.join(self.project_a, 'notes.txt'), 'meeting')
        self._make_file(_os.path.join(self.project_a, 'data.csv'), '1,2')
        self._make_file(_os.path.join(self.project_a, 'readme.txt'), 'readme')
        self._make_file(_os.path.join(self.project_a, 'script.py'), 'print(1)')

        state = self._run_flow([
            ('进入', {'_待进入路径': self.project_a}),
            ('列表', {}),
            ('筛选', {'_扩展名': 'txt'}),
            ('批量重命名', {'_前缀': 'bk_', '_扩展名': 'txt'}),
            ('压缩', {}),
            ('移动', {'目标目录': self.archive_dir}),
            ('解压', {}),
        ])
        self.assertEqual(state['对象类型'], '文件集合')
        self.assertEqual(state['解压文件数'], 2)

    def test_backup_and_delete(self):
        self._make_file(_os.path.join(self.project_b, 'temp.log'), 'debug')
        self._make_file(_os.path.join(self.project_b, 'debug.log'), 'more')

        state = self._run_flow([
            ('进入', {'_待进入路径': self.project_b}),
            ('列表', {}),
            ('筛选', {'_扩展名': 'log'}),
            ('合并为对象', {}),
            ('复制', {'目标目录': self.backup_dir}),
            ('删除', {}),
        ])
        self.assertTrue(state['已删除'])

    def test_pick_rename_zip(self):
        self._make_file(_os.path.join(self.project_a, 'draft.txt'), 'draft')

        state = self._run_flow([
            ('进入', {'_待进入路径': self.project_a}),
            ('选取', {'_待选文件': 'draft.txt'}),
            ('重命名', {'新名称': 'final.txt'}),
            ('压缩', {}),
            ('移动', {'目标目录': self.archive_dir}),
        ])
        self.assertEqual(state['对象类型'], '压缩包')
        self.assertTrue(state['当前对象'].startswith(self.archive_dir))


if __name__ == '__main__':
    unittest.main(verbosity=2)
