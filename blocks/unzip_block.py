import os
import zipfile
from core.state import State


def _do_unzip(state: State) -> State:
    target = state["当前对象"]
    obj_type = state["对象类型"]

    if obj_type != "压缩包":
        raise ValueError(f"解压: 对象类型必须为「压缩包」，当前为「{obj_type}」")

    if not os.path.exists(target):
        raise FileNotFoundError(f"解压: 压缩包不存在: {target}")

    dest_dir = os.path.dirname(target)
    extract_dir = os.path.join(dest_dir, os.path.splitext(os.path.basename(target))[0])

    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(target, "r") as zf:
        zf.extractall(extract_dir)

    extracted_files = [
        os.path.join(extract_dir, name)
        for name in sorted(os.listdir(extract_dir))
    ]

    return state.with_updates(
        当前对象=extracted_files,
        对象类型="文件集合",
        解压目录=extract_dir,
        解压文件数=len(extracted_files),
    )
