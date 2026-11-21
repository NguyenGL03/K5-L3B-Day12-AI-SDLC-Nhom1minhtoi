"""File kho v1.0 (Contract G): {"items": {id: số nguyên >= 0}}.

Đọc: từ chối sai schema / id lạ / số âm (BadInput -> mã 2).
Ghi: bỏ mục bằng 0, qua file tạm cùng thư mục rồi thay thế, byte-ổn-định.
"""

import json
import math
import os
import tempfile
from fractions import Fraction

from .ids import sort_by_id

from .errors import BadInput

KINDS_P1 = ("ca_loc", "ca_linh", "bong_dien_dien", "bong_sung")


def ingredient_kinds(tuning):
    return {kind for dish in tuning["menu"].values() for kind in dish["recipe"]}


def validate_items(items, kinds=KINDS_P1):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def validate_individual_items(items, kinds):
    if not isinstance(items, list):
        raise BadInput("kho v1.2 phải là mảng cá thể")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or item.keys() != {"id", "kind", "fresh"}:
            raise BadInput("cá thể phải chứa đúng id, kind và fresh")
        item_id, kind, fresh = item["id"], item["kind"], item["fresh"]
        if not isinstance(item_id, str) or not item_id or item_id in seen:
            raise BadInput("id cá thể phải là chuỗi khác rỗng và duy nhất")
        if not isinstance(kind, str) or kind not in kinds:
            raise BadInput(f"nguyên liệu lạ: {kind}")
        if type(fresh) not in (int, float) or not 0 <= fresh <= 100:
            raise BadInput(f"{item_id}.fresh phải là số hữu hạn trong [0,100]")
        seen.add(item_id)
    return [item.copy() for item in items]


def exact_freshness(items):
    return [dict(item, fresh=Fraction(str(item["fresh"]))) for item in items]


def public_freshness(items, threshold=None):
    result = []
    for item in items:
        exact = item["fresh"]
        value = float(exact)
        if threshold is not None and exact < threshold <= Fraction(str(value)):
            value = math.nextafter(value, -math.inf)
        result.append(dict(item, fresh=value))
    return result


def decay_freshness(items, decay, threshold, location):
    events = []
    for item in sort_by_id(items):
        previous = item["fresh"]
        item["fresh"] = max(0, previous - decay)
        if item["fresh"] < threshold <= previous:
            events.append(("spoiled", {"item_id": item["id"], "kind": item["kind"], "location": location}))
    return events


def read_inventory(path: str, kinds=KINDS_P1, *, version="1.0"):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    if version in ("1.2", "1.3"):
        return validate_individual_items(data["items"], kinds)
    return validate_items(data["items"], kinds)


def hold_to_items(hold: list) -> dict:
    """Khoang (mảng id theo thứ tự nhặt) -> object đếm, sắp theo id nguyên liệu."""
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def write_inventory(path: str, items):
    if isinstance(items, list):
        items = sort_by_id(items)
    else:
        items = {k: items[k] for k in sorted(items) if items[k] > 0}
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"items": items}, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
