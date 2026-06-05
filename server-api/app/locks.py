"""Per-member redemption write locks (in-process)."""

from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Dict

_LOCKS: "OrderedDict[str, threading.Lock]" = OrderedDict()
_META = threading.Lock()
_MAX = 2048


def get_redemption_lock(key: str) -> threading.Lock:
    with _META:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _LOCKS[key] = lock
        else:
            _LOCKS.move_to_end(key)
        if len(_LOCKS) > _MAX:
            for bid, lk in list(_LOCKS.items()):
                if lk is lock:
                    continue
                if lk.acquire(blocking=False):
                    try:
                        _LOCKS.pop(bid, None)
                    finally:
                        lk.release()
                    if len(_LOCKS) <= _MAX:
                        break
        return lock
