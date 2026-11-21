import unittest
from pathlib import Path

from chonoi.contract import load_contract
from chonoi.headless import main
from chonoi.inputs import BUTTONS_V11, InputPlayer
from chonoi.runner import Session

from helpers import Workdir, events, frames, read_jsonl, snapshots, write_json


from helpers import use_count_contract


def setUpModule():
    use_count_contract()


class DayPhase2(unittest.TestCase):
    def test_day_closes_only_after_shop_and_next_day_applies_purchase(self):
        tuning = load_contract()["tuning"]
        fixture = {"day": {"money": 200, "earned": 200}, "gather": {"hold": ["ca_loc"], "time_left_ticks": 1},
                   "quan": {"time_left_ticks": 1}}
        with Workdir() as w:
            scenario = write_json(w.path("scenario.json"), fixture)
            inputs = write_json(w.path("inputs.json"), frames(
                {"tick": 2, "pause": True, "buy": "hp", "shop_done": True},
                {"tick": 3, "pause": False, "shop_done": False},
                {"tick": 4, "pause": True, "buy": "oxygen"},
                {"tick": 5, "pause": False, "shop_done": True},
                {"tick": 6, "shop_done": False}, {"tick": 8, "shop_done": True}))
            args = ["--mode", "day", "--days", "2", "--seed", "23", "--ticks", "9", "--snapshot-every", "1",
                    "--scenario", scenario, "--inputs", inputs]
            out = w.path("out.jsonl")
            self.assertEqual(main([*args, "--out", out]), 0)
            rows = read_jsonl(out)
            data = {row["tick"]: row for row in snapshots(rows)}
            self.assertEqual([(row["name"], row["tick"]) for row in events(rows)[:5]],
                             [("day_start", 0), ("day_plan", 0), ("phase_start", 0), ("gather_end", 1), ("phase_start", 1)])
            self.assertEqual(data[1]["stock"], {"ca_loc": 1})
            self.assertEqual((data[1]["phase"], data[1]["phase_tick"]), ("quan", 0))
            self.assertEqual((data[3]["state"], data[3]["sim_tick"], data[4]["sim_tick"]), ("paused", 2, 2))
            self.assertEqual(data[5]["upgrades"], {"oxygen": 1})
            self.assertEqual(data[5]["active_upgrades"], {})
            self.assertEqual(data[6]["day"], 2)
            self.assertEqual(data[6]["phase_tick"], 0)
            self.assertEqual(data[6]["active_upgrades"], {"oxygen": 1})
            self.assertEqual(data[6]["player"]["oxygen_max_ticks"], tuning["shop"]["upgrades"]["oxygen"][0]["oxygen_max_s"] * tuning["tick_hz"])
            self.assertEqual((rows[-1]["reason"], rows[-1]["days_completed"], rows[-1]["money"], rows[-1]["earned"]),
                             ("days_complete", 2, 0, 200))
            replay = w.path("replay.jsonl")
            self.assertEqual(main([*args, "--out", replay]), 0)
            self.assertEqual(Path(out).read_bytes(), Path(replay).read_bytes())

    def test_crocodile_hits_once_and_faint_loses_remaining_hold(self):
        tuning = load_contract()["tuning"]
        crocodile = {"id": "M1", "kind": "ca_sau", "pos": [60, 24], "waypoints": [[60, 24], [64, 24]]}
        sim = Session("gather", tuning, {"monsters": [crocodile], "random_fish": False,
                                        "player": {"pos": [60, 24], "hp": 1},
                                        "hold": ["ca_loc", "ca_linh", "bong_sung"]}, 5)
        rows = sim.step(InputPlayer([], BUTTONS_V11).advance(0))
        self.assertEqual([row["name"] for row in rows], ["monster_hit", "faint", "gather_end"])
        self.assertEqual(rows[0]["data"]["lost"], ["bong_sung"])
        self.assertEqual(rows[1]["data"], {"cause": "monster", "lost": ["ca_linh", "ca_loc"], "hp": 0})
        self.assertEqual(rows[2]["data"]["inventory"], {"items": {}})

    def test_fish_reflect_then_spawn_at_exact_tick(self):
        tuning = load_contract()["tuning"]
        sim = Session("gather", tuning, {"fish": [{"id": "F10", "kind": "ca_loc", "pos": [95.99, 16]}],
                                        "monsters": []}, 5)
        inputs = InputPlayer([])
        rows = sim.step(inputs.advance(0))
        fish = sim.snapshot()["fish"][0]
        self.assertAlmostEqual(fish["pos"][0], 95.985)
        self.assertAlmostEqual(fish["heading_deg"], 180)
        self.assertFalse(rows)
        schedule = tuning["gather"]["fish_spawn_ticks"]
        timeline = [row for tick in range(1, schedule) for row in sim.step(inputs.advance(tick))]
        self.assertEqual([(row["name"], row["tick"], row["data"]["id"]) for row in timeline],
                         [("fish_spawned", schedule, "F11")])
        self.assertEqual(sim.snapshot()["fish"][-1]["age_ticks"], 0)
