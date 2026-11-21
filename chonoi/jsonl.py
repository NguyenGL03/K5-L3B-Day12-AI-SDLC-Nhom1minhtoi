"""Ghi JSONL tất định, giữ độ tươi qua ngưỡng và làm tròn tọa độ khi xuất."""

import json


def _clean(v):
    if isinstance(v, float):
        r = round(v, 3)
        return 0.0 if r == 0 else r  # tránh -0.0
    if isinstance(v, dict):
        return {k: x if k == "fresh" and isinstance(x, float) else _clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    return v


def dumps(obj) -> str:
    return json.dumps(_clean(obj), ensure_ascii=False, separators=(",", ":"))


class JsonlWriter:
    def __init__(self, path: str):
        self._f = open(path, "w", encoding="utf-8", newline="\n")

    def write(self, obj):
        self._f.write(dumps(obj) + "\n")

    def close(self):
        self._f.close()
