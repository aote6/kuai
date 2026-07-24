from core.state import State


def _do_replace(state: State) -> State:
    filepath = state["当前对象"]
    old_text = state["_查找"]
    new_text = state["_替换"]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content.replace(old_text, new_text)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return state.with_updates(文件内容=new_content)
