from core.state import State
from core.block_loader import load_all_blocks

BLOCK_DEFS_DIR = "block_defs"


def _enter_dir(state: State) -> State:
    path = state["_待进入路径"]
    new_state = State({k: v for k, v in state.items() if k != "_待进入路径"})
    return new_state.with_updates(当前路径=path)


BLOCK_REGISTRY = load_all_blocks(BLOCK_DEFS_DIR)


class FlowBuildError(Exception):
    pass


def build_executable_blocks(parsed_flow: dict):
    executable = []
    for block_spec in parsed_flow["blocks"]:
        name = block_spec["name"]
        arg = block_spec["arg"]
        named_args = block_spec["named_args"]
        line = block_spec["line"]

        if name not in BLOCK_REGISTRY:
            raise FlowBuildError(f"第{line}行: 未知块名 '{name}'")

        block = BLOCK_REGISTRY[name]
        inject_keys = block.param_inject_keys  # 现在是列表

        # 构建注入字典: {内部State字段: 值}
        injections = {}

        # 处理旧式单参数（向后兼容）
        if inject_keys and arg is not None:
            # 取第一个参数映射
            injections[inject_keys[0][1]] = arg

        # 处理新的具名参数
        for external_name, internal_key in inject_keys:
            if external_name in named_args:
                injections[internal_key] = named_args[external_name]

        # 检查：有参数映射但没提供值
        if inject_keys:
            provided = set(named_args.keys())
            if arg is not None:
                provided.add(inject_keys[0][0])
            for external_name, internal_key in inject_keys:
                if external_name not in provided:
                    raise FlowBuildError(
                        f"第{line}行: 块 '{name}' 缺少参数 '{external_name}'"
                    )

        # 检查：提供了参数但块没有声明任何映射
        if not inject_keys and (arg is not None or named_args):
            raise FlowBuildError(
                f"第{line}行: 块 '{name}' 不接受参数，但提供了参数"
            )

        executable.append((block, injections))

    return executable
