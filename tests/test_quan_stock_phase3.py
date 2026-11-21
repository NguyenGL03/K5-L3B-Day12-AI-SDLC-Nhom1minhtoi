import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.headless import main
from chonoi.inputs import InputPlayer
from chonoi.inventory import read_inventory
from chonoi.runner import Session, run
from chonoi.sim.quan_stock import QuanStock

from helpers import Workdir, events, read_jsonl, snapshots, write_json


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

    def test_gather_file_preserves_freshness_threshold_for_quan_adapter(self):
        tuning = load_contract()["tuning"]
        tuning["freshness"] = FRESHNESS
        fixture = {"hold": [item("I9", 30.008333333333333), item("I2", 100)], "monsters": [], "random_fish": False}
        with Workdir() as temp:
            path = temp.path("stock.json")
            out = temp.path("gather.jsonl")
            run("gather", tuning, fixture, 1, [{"tick": 0, "interact": True}], 1, out, 1, inventory_out=path)
            trace = events(read_jsonl(out))
            self.assertEqual([row["name"] for row in trace], ["spoiled", "gather_end"])
            saved = read_inventory(path, {"ca_loc"}, version="1.2")
            self.assertEqual(saved, trace[-1]["data"]["inventory"]["items"])
            self.assertEqual([row["id"] for row in saved], ["I2", "I9"])
            self.assertLess(saved[1]["fresh"], 30)
            stock = self.build(saved)
            self.assertEqual(stock.snapshot(), saved)
            self.assertEqual(stock.reserve({"ca_loc": 1}, set()), ["I2"])
            self.assertIsNone(stock.reserve({"ca_loc": 2}, set()))
            with self.assertRaises(BadInput):
                read_inventory(path, {"ca_loc"}, version="1.1")

    def test_quan_replaces_spoiled_claims_before_cooking_and_locks_price(self):
        tuning = load_contract()["tuning"]
        scenario = {"stock": [item("I1", 30), item("I2", 90), item("I3", 100)], "player": {"pos": [2, 8]},
                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]},
                                  {"id": "C2", "table_id": "T2", "dish_id": "ca_loc_nuong_trui", "reserved": ["I3"]}]}
        session = Session("quan", tuning, scenario, 1)
        player = InputPlayer([{"tick": 0, "interact": True}])
        trace = session.step(player.advance(0))
        self.assertEqual([row["name"] for row in trace], ["spoiled", "cook_started"])
        cooked = trace[-1]["data"]
        self.assertEqual(cooked["base_price"], 53)  # 90% trừ 1/240 trước lúc chốt giá.
        self.assertEqual([row["id"] for row in cooked["items"]], ["I2"])
        state = session.snapshot()
        self.assertEqual(state["stoves"][0]["dish"]["base_price"], 53)
        self.assertEqual([c["reserved"] for c in state["customers"]], [[], ["I3"]])

    def test_quan_leaves_unfulfillable_order_waiting_and_releases_claims(self):
        scenario = {"stock": [item("I1", 30), item("I2", 90)], "player": {"pos": [2, 8]},
                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung",
                                   "reserved": ["I1", "I2"]}]}
        for article in scenario["stock"]:
            article["kind"] = "bong_sung"
        session = Session("quan", load_contract()["tuning"], scenario, 1)
        trace = session.step(InputPlayer([{"tick": 0, "interact": True}]).advance(0))
        self.assertEqual([row["name"] for row in trace], ["spoiled"])
        person = session.snapshot()["customers"][0]
        self.assertEqual((person["state"], person["order_status"], person["reserved"]), ("waiting", "unfulfillable", []))

    def test_release_cli_rejects_old_file_and_transfers_fresh_stock_in_day(self):
        with Workdir() as temp:
            out = temp.path("out.jsonl")
            old = write_json(temp.path("old.json"), {"items": {"ca_loc": 1}})
            self.assertEqual(main(["--mode", "quan", "--seed", "1", "--ticks", "0", "--out", out, "--inventory", old]), 2)
            scenario = write_json(temp.path("day.json"), {"gather": {"hold": [item("I9", 100)], "time_left_ticks": 1},
                                                           "quan": {"time_left_ticks": 1}})
            self.assertEqual(main(["--mode", "day", "--seed", "1", "--ticks", "2", "--out", out, "--scenario", scenario]), 0)
            rows = read_jsonl(out)
            gather = next(row for row in events(rows) if row["name"] == "gather_end")
            evening, shop = snapshots(rows)[1:]
            self.assertEqual(evening["stock"], gather["data"]["inventory"]["items"])
            self.assertEqual(evening["stock"][0]["id"], "I9")
            self.assertAlmostEqual(evening["stock"][0]["fresh"] - shop["stock"][0]["fresh"], 1 / 240)
