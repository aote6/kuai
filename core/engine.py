from core.state import State


class SkipRemainingSteps(Exception):
    def __init__(self, state: State):
        self.state = state


class Engine:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.trace = []

    def run_sequence(self, blocks: list, initial_state: State) -> State:
        current_state = initial_state
        self.trace.append({"step": "初始", "state": dict(current_state)})

        for i, block in enumerate(blocks):
            if self.verbose:
                print(f"→ 执行: {block.name}")
            try:
                current_state = block.execute(current_state)
            except SkipRemainingSteps as skip:
                if self.verbose:
                    remaining = len(blocks) - i - 1
                    print(f"  ⏭ 触发跳过，剩余 {remaining} 个步骤未执行")
                current_state = skip.state
                self.trace.append({"step": f"{block.name}(跳过剩余)", "state": dict(current_state)})
                break
            self.trace.append({"step": block.name, "state": dict(current_state)})
            if self.verbose:
                print(f"  状态: {current_state}")

        return current_state

    def print_trace(self):
        print("\n=== 执行轨迹 ===")
        for entry in self.trace:
            print(f"[{entry['step']}] {entry['state']}")
