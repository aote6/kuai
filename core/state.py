import json


class State(dict):
    """可序列化的状态对象，本质是字典。
    约定：块函数不得原地修改传入的State，必须返回新的State实例。
    """

    def to_json(self):
        return json.dumps(self, ensure_ascii=False, indent=2)

    def with_updates(self, **kwargs):
        """产生一个新的State，不修改自身。"""
        return State({**self, **kwargs})

    def __repr__(self):
        return f"State({dict.__repr__(self)})"


class StateMismatchError(Exception):
    """块的输入State不满足其input_schema时抛出。"""
    pass
