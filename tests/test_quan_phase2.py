import json
import unittest
from collections import Counter
from pathlib import Path

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputPlayer
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


from helpers import use_count_contract


def setUpModule():
    use_count_contract()


class QuanPhase2(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def build(self, scenario, **params):
        return QuanSim(self.tuning, scenario, Streams(1), IdAllocator(), **params)

    def test_manifest_matches_ticket(self):
        path = Path(__file__).with_name("fixtures") / "quan_phase2.json"
        expected = json.loads(path.read_text(encoding="utf-8"))
        for key, value in expected["quan"].items():
            self.assertEqual(self.tuning["quan"][key], value)
        for dish_id, dish in expected["menu_additions"].items():
            self.assertEqual(self.tuning["menu"][dish_id], dish)
        self.assertEqual(self.tuning["day_plan"], expected["day_plan"])

    def test_day_plans_match_recipes_and_allowed_menu(self):
        for plan in self.tuning["day_plan"]:
            with self.subTest(day=plan["day"]):
                ingredients = Counter()
                for dish_id, servings in plan["dishes"].items():
                    ingredients.update({kind: count * servings for kind, count in self.tuning["menu"][dish_id]["recipe"].items()})
                self.assertEqual(ingredients, plan["ingredients"])
                stock = dict.fromkeys({kind for dish in self.tuning["menu"].values() for kind in dish["recipe"]}, 12)
                sim = self.build({"stock": stock}, day_plan=plan)
                self.assertEqual(sim._available_dishes(), sorted(plan["dishes"]))
                self.assertEqual(self.build({"stock": stock})._available_dishes(), sorted(self.tuning["menu"]))

    def test_two_stoves_take_oldest_orders_and_reserve_across_tables(self):
        scenario = {"random_customers": False, "player": {"pos": [2, 8]}, "stock": {"ca_keo": 4},
                    "customers": [
                        {"id": "C1", "table_id": "T4", "dish_id": "ca_keo_nuong", "order_tick": 3},
                        {"id": "C2", "table_id": "T2", "dish_id": "ca_keo_nuong", "order_tick": 1},
                    ]}
        sim = self.build(scenario)
        inputs = InputPlayer([{"tick": 0, "interact": True}, {"tick": 1, "interact": False, "move": [1, 0]},
                              {"tick": 46, "interact": True, "move": [0, 0]}])
        trace = [event for tick in range(47) for event in sim.step(inputs.advance(tick))]
        self.assertEqual([e[0] for e in trace], ["cook_started", "cook_started"])
        self.assertEqual([(data["stove_id"], data["order_id"]) for _, data in trace], [("B1", "C2"), ("B2", "C1")])
        self.assertEqual(sim.snapshot()["stock"], {})
        self.assertEqual(len(sim.snapshot()["tables"]), 4)

    def test_day_plan_quantities_do_not_limit_sales_and_opening_balance_carries(self):
        dish = "ca_loc_nuong_trui"
        plan = {"day": 1, "dishes": {dish: 1}, "ingredients": {"ca_loc": 1}}
        scenario = {"customers": [{"id": "C1", "table_id": "T1", "dish_id": dish, "state": "eating",
                                   "order_status": "served", "eat_ticks_left": 1, "base_price": 60, "tip": 12}],
                    "reputation": 4.0}
        sim = self.build(scenario, inventory={"ca_loc": 2, "ca_keo": 4}, day_plan=plan, money=200, earned=250)
        inputs = InputPlayer([])
        stop = self.tuning["quan"]["first_customer_tick"] + round(self.tuning["quan"]["customer_interval_s"] * self.tuning["tick_hz"])
        trace = [event for tick in range(stop) for event in sim.step(inputs.advance(tick))]
        self.assertEqual([data["dish_id"] for name, data in trace if name == "customer_arrived"], [dish, dish])
        self.assertEqual((sim.money, sim.earned, sim.shift_earned, sim.reputation), (272, 322, 72, 4.2))
