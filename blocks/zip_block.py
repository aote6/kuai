import os
import shutil
from core.block import Block
from core.state import State


def _do_zip(state: State) -> State:
    target = state["当前对象"]
    archive_base = target.rstrip("/").rstrip("\\")

    if os.path.isdir(target):
        archive_path = shutil.make_archive(archive_base, "zip", target)
    else:
        import zipfile
        archive_path = archive_base + ".zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.write(target, arcname=os.path.basename(target))

    return state.with_updates(当前对象=archive_path, 对象类型="压缩包")


ZipBlock = Block(
    name="压缩",
    input_schema=["当前对象", "对象类型"],
    output_schema=["当前对象", "对象类型"],
    execute_func=_do_zip,
)
