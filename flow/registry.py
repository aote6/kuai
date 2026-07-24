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
        inject_keys = block.param_inject_keys

        injections = {}

        if inject_keys and arg is not None:
            injections[inject_keys[0][1]] = arg

        for external_name, internal_key in inject_keys:
            if external_name in named_args:
                injections[internal_key] = named_args[external_name]

        # 检查缺失参数：先收集所有缺失的，一次性报错
        if inject_keys:
            provided = set(named_args.keys())
            if arg is not None:
                provided.add(inject_keys[0][0])
            missing = []
            for external_name, internal_key in inject_keys:
                if external_name not in provided:
                    missing.append(external_name)
            if missing:
                raise FlowBuildError(
                    f"第{line}行: 块 '{name}' 缺少参数 {missing}"
                )

        # 检查未知参数
        if inject_keys:
            known_external = set(k[0] for k in inject_keys)
            for k in named_args:
                if k not in known_external:
                    raise FlowBuildError(
                        f"第{line}行: 块 '{name}' 不接受未知参数 '{k}'"
                    )

        if not inject_keys and (arg is not None or named_args):
            raise FlowBuildError(
                f"第{line}行: 块 '{name}' 不接受参数"
            )

        executable.append((block, injections))

    return executable
