import unittest

from chonoi.errors import BadInput
from chonoi.sim.quan_stock import QuanStock


FRESHNESS = {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30}


def item(item_id, fresh, kind="ca_loc"):
    return {"id": item_id, "kind": kind, "fresh": fresh}


class QuanStockPhase3(unittest.TestCase):
    def build(self, items):
        return QuanStock(items, {"ca_loc", "ca_keo"}, FRESHNESS, 60)

    def test_spoiled_only_when_crossing_threshold_and_in_id_order(self):
        stock = self.build([item("I10", 30), item("I2", 30), item("I7", 30.0125), item("I3", 0)])
        self.assertEqual([row["id"] for row in stock.snapshot()], ["I2", "I3", "I7", "I10"])
        self.assertEqual(stock.reserve({"ca_loc": 2}, set()), ["I7", "I2"])
        self.assertEqual(stock.advance(), [
            ("spoiled", {"item_id": "I2", "kind": "ca_loc", "location": "stock"}),
            ("spoiled", {"item_id": "I10", "kind": "ca_loc", "location": "stock"}),
        ])
        self.assertEqual(stock.advance(), [])
        self.assertEqual(stock.advance(), [])
        fresh = {row["id"]: row["fresh"] for row in stock.snapshot()}
        self.assertEqual(fresh["I7"], 30)
        self.assertEqual(fresh["I3"], 0)
        self.assertEqual(stock.advance(), [("spoiled", {"item_id": "I7", "kind": "ca_loc", "location": "stock"})])
        self.assertEqual(stock.advance(), [])
        self.assertIsNone(stock.reserve({"ca_loc": 1}, set()))
        self.assertEqual(len(stock.snapshot()), 4)

    def test_pick_freshest_then_id_and_exclude_other_orders(self):
        stock = self.build([item("I10", 75), item("I2", 75), item("I1", 65), item("I3", 90, "ca_keo")])
        recipe = {"ca_loc": 1, "ca_keo": 1}
        self.assertEqual(stock.reserve(recipe, {"I2"}), ["I3", "I10"])
        stock.validate_reservation(recipe, ["I3", "I10"], {"I2"})
        for impossible in (["I2", "I3"], ["I1", "I10"], ["I3", "I3"], ["I3", "I4"]):
            with self.subTest(reserved=impossible), self.assertRaises(BadInput):
                stock.validate_reservation(recipe, impossible, {"I2"})
        self.assertIsNone(stock.reserve(recipe, {"I3"}))

    def test_reject_count_schema_and_invalid_items(self):
        for invalid in ({"ca_loc": 1}, [item("I1", 30), item("I1", 40)], [item("I1", float("nan"))],
                        [item("I1", 101)], [item("I1", 30, "unknown")], [item("", 30)]):
            with self.subTest(invalid=invalid), self.assertRaises(BadInput):
                self.build(invalid)
