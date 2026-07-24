import sys
sys.path.insert(0, '/data/data/com.termux/files/home/kuai')

from flow.runner import run_flow_file

if __name__ == "__main__":
    final_state = run_flow_file("flows/backup.flow")
    print("\n=== 最终状态 ===")
    print(final_state.to_json())
