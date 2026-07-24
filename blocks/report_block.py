import os
from core.state import State


def _do_report(state: State) -> State:
    base_dir = state["当前路径"]
    lines = []
    lines.append(f"目录: {base_dir}")
    lines.append(f"筛选数量: {state.get('筛选数量', 0)}")
    lines.append(f"分类数量: {state.get('分类数量', 0)}")
    lines.append("")

    for root, dirs, files in os.walk(base_dir):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, base_dir)
            lines.append(f"  {rel}")

    report = "\n".join(lines)
    report_path = os.path.join(base_dir, "整理报告.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return state.with_updates(报告路径=report_path, 报告内容=report)
