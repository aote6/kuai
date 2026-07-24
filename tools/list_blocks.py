import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flow.registry import BLOCK_REGISTRY


def export_manifest():
    manifest = []
    for name, block in BLOCK_REGISTRY.items():
        entry = {
            "name": name,
            "input": block.input_schema,
            "output": block.output_schema,
            "output_constants": getattr(block, "output_constants", {}),
            "params": [k[0] for k in (getattr(block, "param_inject_keys", None) or [])],
            "idempotent": getattr(block, "is_idempotent", None),
        }
        manifest.append(entry)
    return manifest


if __name__ == "__main__":
    manifest = export_manifest()
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
