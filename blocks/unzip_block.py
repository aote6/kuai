import os
import zipfile
import shutil
from core.state import State


def _do_unzip(state: State) -> State:
    zip_path = state["当前对象"]
    extract_dir = zip_path
    if extract_dir.endswith(".zip"):
        extract_dir = extract_dir[:-4]
    extract_dir = extract_dir + "_解压"

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    return state.with_updates(当前对象=extract_dir, 对象类型="文件副本")
