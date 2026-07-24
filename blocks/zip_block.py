import os
import shutil
import zipfile
from core.state import State


def _do_zip(state: State) -> State:
    target = state["当前对象"]
    obj_type = state["对象类型"]

    if obj_type == "文件集合":
        if not isinstance(target, list):
            raise TypeError(f"压缩: 对象类型为'文件集合'时，当前对象应为列表，实际: {type(target)}")
        if not target:
            raise ValueError("压缩: 文件集合为空，没有可压缩的内容")

        first_dir = os.path.dirname(target[0])
        archive_path = os.path.join(first_dir, "筛选结果打包.zip")
        with zipfile.ZipFile(archive_path, "w") as zf:
            for f in target:
                zf.write(f, arcname=os.path.basename(f))

        return state.with_updates(当前对象=archive_path, 对象类型="压缩包")

    archive_base = target.rstrip("/").rstrip("\\")

    if os.path.isdir(target):
        archive_path = shutil.make_archive(archive_base, "zip", target)
    else:
        archive_path = archive_base + ".zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.write(target, arcname=os.path.basename(target))

    return state.with_updates(当前对象=archive_path, 对象类型="压缩包")
