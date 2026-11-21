"""Kho cá thể của Quán theo Test Contract v1.2."""

from collections import Counter
from fractions import Fraction

from ..errors import BadInput
from ..ids import id_key, sort_by_id


class QuanStock:
    def __init__(self, items, kinds, freshness, tick_hz):
        self.threshold = Fraction(str(freshness["spoiled_below"]))
        self.decay_per_tick = Fraction(str(freshness["quan_decay_per_s"])) / tick_hz
        self.items = {}
        if not isinstance(items, list):
            raise BadInput("kho Quán v1.2 phải là mảng cá thể")
        for item in items:
            if not isinstance(item, dict) or item.keys() != {"id", "kind", "fresh"}:
                raise BadInput("cá thể phải chứa đúng id, kind và fresh")
            item_id, kind, fresh = item["id"], item["kind"], item["fresh"]
            if not isinstance(item_id, str) or not item_id or item_id in self.items:
                raise BadInput("id cá thể phải là chuỗi khác rỗng và duy nhất")
            if not isinstance(kind, str) or kind not in kinds:
                raise BadInput(f"nguyên liệu lạ: {kind}")
            if type(fresh) not in (int, float) or not 0 <= fresh <= 100:
                raise BadInput(f"{item_id}.fresh phải là số hữu hạn trong [0,100]")
            self.items[item_id] = {"id": item_id, "kind": kind, "fresh": Fraction(str(fresh))}

    def advance(self):
        events = []
        for item in sort_by_id(self.items.values()):
            previous = item["fresh"]
            item["fresh"] = max(0, previous - self.decay_per_tick)
            if item["fresh"] < self.threshold <= previous:
                events.append(("spoiled", {"item_id": item["id"], "kind": item["kind"], "location": "stock"}))
        return events

    def reserve(self, recipe, claimed):
        candidates = sorted(self.items.values(), key=lambda item: (-item["fresh"], id_key(item["id"])))
        required = Counter(recipe)
        selected = []
        for item in candidates:
            kind = item["kind"]
            if required[kind] > 0 and item["id"] not in claimed and item["fresh"] >= self.threshold:
                selected.append(item["id"])
                required[kind] -= 1
        return selected if not any(required.values()) else None

    def validate_reservation(self, recipe, reserved, claimed):
        if not isinstance(reserved, list) or any(not isinstance(item_id, str) for item_id in reserved):
            raise BadInput("reserved phải là mảng id cá thể")
        unique = set(reserved)
        if len(unique) != len(reserved) or unique.intersection(claimed):
            raise BadInput("mỗi cá thể chỉ được xuất hiện trong một phần giữ chỗ")
        counts = Counter()
        for item_id in reserved:
            item = self.items.get(item_id)
            if item is None or item["fresh"] < self.threshold:
                raise BadInput(f"cá thể {item_id} đã ươn hoặc không có trong kho")
            counts[item["kind"]] += 1
        if counts != recipe:
            raise BadInput("cá thể giữ chỗ không đủ đúng công thức")

    def snapshot(self):
        return [dict(item, fresh=float(item["fresh"])) for item in sort_by_id(self.items.values())]
