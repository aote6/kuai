from core.state import State


class Engine:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.trace = []

    def run_sequence(self, blocks: list, initial_state: State) -> State:
        current_state = initial_state
        self.trace.append({"step": "初始", "state": dict(current_state)})

        for block in blocks:
            if self.verbose:
                print(f"→ 执行: {block.name}")
            current_state = block.execute(current_state)
            self.trace.append({"step": block.name, "state": dict(current_state)})
            if self.verbose:
                print(f"  状态: {current_state}")

        return current_state

    def print_trace(self):
        print("\n=== 执行轨迹 ===")
        for entry in self.trace:
            print(f"[{entry['step']}] {entry['state']}")
