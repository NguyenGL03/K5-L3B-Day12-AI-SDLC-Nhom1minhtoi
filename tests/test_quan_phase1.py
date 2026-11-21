"""Kiểm chứng headless cho phần Quán bằng kho mẫu và scenario riêng của Quán."""

import json
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from chonoi.contract import load_contract
from chonoi.headless import main

from helpers import ROOT, Workdir, events, frames, read_jsonl, snapshots, write_json


class QuanPhase1(unittest.TestCase):
    def run_quan(self, ticks, out, *args):
        return main(["--mode", "quan", "--seed", "1", "--ticks", str(ticks),
                     "--out", out, "--snapshot-every", "1", *args])

    def test_serve_and_pay_from_sample_inventory(self):
        tuning = load_contract()["tuning"]
        quan, menu, hz = tuning["quan"], tuning["menu"], tuning["tick_hz"]
        stove = quan["stoves"][0]["pos"]
        table = quan["tables"][0]["pos"]
        first = quan["first_customer_tick"]
        inventory = Path(ROOT, "docs", "contracts", "inventory.sample.json")
        sample_stock = json.loads(inventory.read_text(encoding="utf-8"))["items"]
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"quan": {"player": {"pos": stove}}})
            args = ("--inventory", str(inventory), "--scenario", scenario)
            out = w.path("quan.jsonl")
            self.assertEqual(self.run_quan(first, out, *args), 0)
            arrival_run = read_jsonl(out)
            self.assertEqual(snapshots(arrival_run)[0]["stock"], sample_stock)
            arrival, = events(arrival_run, "customer_arrived")
            self.assertEqual(arrival["tick"], first)
            dish = menu[arrival["data"]["dish_id"]]

            pick = first + round(dish["cook_s"] * hz)
            move = pick + 1
            turn = move + round((table[0] - stove[0]) * hz / quan["walk_speed"])
            serve = turn + round((stove[1] - table[1]) * hz / quan["walk_speed"])
            paid = serve + round(quan["eat_s"] * hz) + 1
            moves = write_json(w.path("inputs.json"), frames(
                {"tick": first, "interact": True},
                {"tick": first + 1, "interact": False},
                {"tick": pick, "interact": True},
                {"tick": move, "interact": False, "move": [1, 0]},
                {"tick": turn, "move": [0, -1]},
                {"tick": serve, "interact": True, "move": [0, 0]},
            ))
            self.assertEqual(self.run_quan(paid, out, *args, "--inputs", moves), 0)
            rows = read_jsonl(out)
            order_id = arrival["data"]["order_id"]
            trace = [event for event in events(rows) if event["data"].get("order_id") == order_id]
            self.assertEqual([(e["name"], e["tick"]) for e in trace], [
                ("customer_arrived", first), ("cook_started", first + 1),
                ("dish_ready", pick + 1), ("dish_picked", pick + 1),
                ("served", serve + 1), ("paid", paid),
            ])
            tip = int(dish["price"] * quan["tip_rate"])
            dish_id = arrival["data"]["dish_id"]
            table_id = quan["tables"][0]["id"]
            stove_id = quan["stoves"][0]["id"]
            order = {"order_id": order_id, "dish_id": dish_id, "table_id": table_id}
            stove_order = {"order_id": order_id, "dish_id": dish_id, "stove_id": stove_id}
            items = [kind for kind, count in sorted(dish["recipe"].items()) for _ in range(count)]
            payment = {"order_id": order_id, "table_id": table_id, "base_price": dish["price"],
                       "tip": tip, "amount": dish["price"] + tip, "reason": "finished_eating"}
            patience = round(quan["patience_s"] * hz) - (serve + 1 - first)
            self.assertEqual([e["data"] for e in trace], [
                order, dict(stove_order, items=items, base_price=dish["price"]), stove_order, stove_order,
                dict(order, patience_ticks_left=patience, base_price=dish["price"], tip=tip), payment,
            ])
            cooked = snapshots(rows)[first + 1]
            self.assertEqual(cooked["customers"][0]["order_status"], "assigned")
            self.assertEqual(cooked["customers"][0]["reserved"], {})
            self.assertEqual(cooked["stoves"][0]["dish"], {"order_id": order_id, "dish_id": dish_id,
                                                         "base_price": dish["price"]})
            self.assertEqual(rows[-1]["money"], dish["price"] + tip)
            self.assertEqual(rows[-1]["earned"], rows[-1]["money"])
            self.assertAlmostEqual(rows[-1]["reputation"], quan["reputation_initial"] + quan["tip_reputation"])
            remaining = {kind: count - dish["recipe"].get(kind, 0) for kind, count in sample_stock.items()}
            self.assertEqual(snapshots(rows)[-1]["stock"], {kind: count for kind, count in remaining.items() if count})
            replay = w.path("replay.jsonl")
            self.assertEqual(self.run_quan(paid, replay, *args, "--inputs", moves), 0)
            self.assertEqual(Path(out).read_bytes(), Path(replay).read_bytes())

    def test_waiting_customer_releases_reservation_on_timeout(self):
        quan = load_contract()["tuning"]["quan"]
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"quan": {
                "stock": {"ca_loc": 1}, "time_left_ticks": quan["first_customer_tick"] + 1,
                "customers": [{"id": "C9", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                               "patience_ticks_left": 1}],
            }})
            out = w.path("quan.jsonl")
            self.assertEqual(self.run_quan(quan["first_customer_tick"] + 1, out, "--scenario", scenario), 0)
            rows = read_jsonl(out)
            self.assertEqual([e["name"] for e in events(rows)],
                             ["customer_left", "customer_arrived", "customer_left", "quan_end"])
            arrival = snapshots(rows)[quan["first_customer_tick"]]
            self.assertEqual(arrival["stock"], {"ca_loc": 1})
            self.assertEqual(arrival["customers"][0]["id"], "C10")
            self.assertEqual(arrival["customers"][0]["reserved"], {"ca_loc": 1})
            self.assertEqual(snapshots(rows)[-1]["customers"], [])
            exits = [event["data"] for event in events(rows, "customer_left")]
            self.assertEqual([exit["reason"] for exit in exits], ["patience", "closing"])
            self.assertAlmostEqual(exits[0]["reputation"], quan["reputation_initial"] + quan["left_reputation_delta"])
            self.assertEqual(exits[1]["reputation"], exits[0]["reputation"])

    def test_no_dish_leaves_table_empty(self):
        first = load_contract()["tuning"]["quan"]["first_customer_tick"]
        with Workdir() as w:
            out = w.path("quan.jsonl")
            self.assertEqual(self.run_quan(first, out), 0)
            rows = read_jsonl(out)
            self.assertEqual([e["name"] for e in events(rows)], ["no_dish"])
            self.assertEqual(events(rows, "no_dish")[0]["data"], {})
            self.assertEqual(snapshots(rows)[-1]["customers"], [])

    def test_timeout_during_cooking_releases_stove_but_keeps_stock_consumed(self):
        tuning = load_contract()["tuning"]
        stove = tuning["quan"]["stoves"][0]
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"quan": {
                "stock": {"ca_loc": 1}, "random_customers": False,
                "player": {"pos": stove["pos"]},
                "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                               "patience_ticks_left": 2}],
            }})
            inputs = write_json(w.path("inputs.json"), frames({"tick": 0, "interact": True}))
            out = w.path("quan.jsonl")
            self.assertEqual(self.run_quan(2, out, "--scenario", scenario, "--inputs", inputs), 0)
            rows = read_jsonl(out)
            self.assertEqual([e["name"] for e in events(rows)], ["cook_started", "customer_left"])
            last = snapshots(rows)[-1]
            self.assertEqual(last["stock"], {})
            self.assertEqual(last["customers"], [])
            self.assertEqual(last["stoves"][0]["state"], "idle")

    def test_assigned_order_requires_a_dish(self):
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"quan": {"customers": [
                {"id": "C1", "table_id": "T1", "order_status": "assigned", "dish_id": "ca_loc_nuong_trui"},
            ]}})
            out = w.path("quan.jsonl")
            with redirect_stderr(StringIO()):
                self.assertEqual(self.run_quan(0, out, "--scenario", scenario), 2)
            self.assertFalse(Path(out).exists())

    def test_serve_on_patience_deadline_and_pay_on_closing_tick(self):
        tuning = load_contract()["tuning"]
        quan = tuning["quan"]
        dish_id = "ca_loc_nuong_trui"
        price = tuning["menu"][dish_id]["price"]
        table = quan["tables"][0]
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"quan": {
                "time_left_ticks": 1, "player": {"pos": table["pos"]},
                "hand": {"order_id": "C1", "dish_id": dish_id, "base_price": price},
                "customers": [{"id": "C1", "table_id": table["id"], "dish_id": dish_id,
                               "order_status": "assigned", "patience_ticks_left": 1}],
            }})
            inputs = write_json(w.path("inputs.json"), frames({"tick": 0, "interact": True}))
            out = w.path("quan.jsonl")
            self.assertEqual(self.run_quan(1, out, "--scenario", scenario, "--inputs", inputs), 0)
            rows = read_jsonl(out)
            self.assertEqual([(e["name"], e["tick"]) for e in events(rows)],
                             [("served", 1), ("paid", 1), ("quan_end", 1)])
            served, paid, end = events(rows)
            self.assertEqual(served["data"]["patience_ticks_left"], 0)
            self.assertEqual(paid["data"]["reason"], "closing")
            self.assertEqual(paid["data"]["tip"], 0)
            self.assertEqual(end["data"]["shift_earned"], price)
            final = snapshots(rows)[-1]
            self.assertIsNone(final["hand"])
            self.assertEqual(final["customers"], [])
            self.assertEqual(final["reputation"], quan["reputation_initial"])

    def test_eating_fixture_requires_committed_price_and_tip(self):
        dish_id = "ca_loc_nuong_trui"
        price = load_contract()["tuning"]["menu"][dish_id]["price"]
        customer = {"id": "C1", "table_id": "T1", "dish_id": dish_id, "state": "eating",
                    "order_status": "served", "eat_ticks_left": 1, "base_price": price}
        with Workdir() as w:
            scenario = w.path("scenario.json")
            out = w.path("quan.jsonl")
            write_json(scenario, {"quan": {"customers": [customer]}})
            with redirect_stderr(StringIO()):
                self.assertEqual(self.run_quan(1, out, "--scenario", scenario), 2)
            self.assertFalse(Path(out).exists())
            write_json(scenario, {"quan": {"customers": [dict(customer, tip=0)], "time_left_ticks": 1}})
            self.assertEqual(self.run_quan(1, out, "--scenario", scenario), 0)
            paid, = events(read_jsonl(out), "paid")
            self.assertEqual(paid["data"]["reason"], "finished_eating")

    def test_closing_tick_does_not_spawn(self):
        first = load_contract()["tuning"]["quan"]["first_customer_tick"]
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), {"quan": {"stock": {"ca_loc": 1},
                                                                      "time_left_ticks": first}})
            out = w.path("quan.jsonl")
            self.assertEqual(self.run_quan(first, out, "--scenario", scenario), 0)
            self.assertEqual([e["name"] for e in events(read_jsonl(out))], ["quan_end"])
