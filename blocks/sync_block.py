import os
import shutil
from core.state import State


def _do_sync(state: State) -> State:
    src_dir = state["当前路径"]
    dest_dir = state["目标目录"]
    synced = 0
    skipped = 0

    os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        dest_root = os.path.join(dest_dir, rel_path)
        os.makedirs(dest_root, exist_ok=True)

        for fname in files:
            src_file = os.path.join(root, fname)
            dest_file = os.path.join(dest_root, fname)

            if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                shutil.copy2(src_file, dest_file)
                synced += 1
            else:
                skipped += 1

    return state.with_updates(同步数量=synced, 跳过数量=skipped)
