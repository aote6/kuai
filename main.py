import sys
sys.path.insert(0, '/data/data/com.termux/files/home/kuai')

from core.state import State
from core.engine import Engine
from blocks.copy_block import CopyBlock
from blocks.zip_block import ZipBlock
from blocks.send_block import SendBlock


def main():
    # 修改为你要测试的实际路径
    test_path = "/data/data/com.termux/files/home/test_project"

    initial_state = State({"当前路径": test_path})

    engine = Engine(verbose=True)
    blocks = [CopyBlock, ZipBlock, SendBlock]

    final_state = engine.run_sequence(blocks, initial_state)

    print("\n=== 最终状态 ===")
    print(final_state.to_json())

    engine.print_trace()


if __name__ == "__main__":
    main()
