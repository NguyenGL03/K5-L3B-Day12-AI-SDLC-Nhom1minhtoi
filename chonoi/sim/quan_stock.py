"""Kho cá thể của Quán theo Test Contract v1.2."""

from collections import Counter
from fractions import Fraction

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from ..inventory import decay_freshness, exact_freshness, public_freshness, validate_individual_items


class QuanStock:
    def __init__(self, items, kinds, freshness, tick_hz, *, exact=False):
        self.threshold = Fraction(str(freshness["spoiled_below"]))
        self.decay_per_tick = Fraction(str(freshness["quan_decay_per_s"])) / tick_hz
        items = [item.copy() for item in items] if exact else exact_freshness(validate_individual_items(items, kinds))
        self.items = {item["id"]: item for item in items}

    def advance(self):
        return decay_freshness(self.items.values(), self.decay_per_tick, self.threshold, "stock")

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

    def replace_spoiled(self, recipe, held, claimed):
        good = [item_id for item_id in held if self.items[item_id]["fresh"] >= self.threshold]
        if len(good) == len(held):
            return held
        required = Counter(recipe)
        required.subtract(self.items[item_id]["kind"] for item_id in good)
        replacement = self.reserve(required, claimed.union(good))
        return good + replacement if replacement is not None else None

    def consume(self, reserved, list_price, initial_freshness):
        items = sorted((self.items.pop(item_id) for item_id in reserved), key=lambda item: (item["kind"], id_key(item["id"])))
        mean = sum(item["fresh"] for item in items) / len(items)
        price = (list_price * mean) // Fraction(str(initial_freshness))
        return public_freshness(items, self.threshold), price

    def snapshot(self):
        return public_freshness(sort_by_id(self.items.values()), self.threshold)
