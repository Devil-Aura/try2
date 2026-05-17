"""
In-memory state management for multi-step user flows.
"""

from typing import Dict, Any

# { user_id: { "action": ..., "file_path": ..., ... } }
_state: Dict[int, Dict[str, Any]] = {}


def set_state(user_id: int, **kwargs):
    _state[user_id] = kwargs


def get_state(user_id: int) -> Dict[str, Any]:
    return _state.get(user_id, {})


def clear_state(user_id: int):
    _state.pop(user_id, None)


def update_state(user_id: int, **kwargs):
    if user_id not in _state:
        _state[user_id] = {}
    _state[user_id].update(kwargs)
