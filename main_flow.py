import sys
sys.path.insert(0, '/data/data/com.termux/files/home/kuai')

from flow.runner import run_flow_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        flow_file = sys.argv[1]
    else:
        flow_file = "flows/backup.flow"
    final_state = run_flow_file(flow_file)
    print("\n=== 最终状态 ===")
    print(final_state.to_json())
