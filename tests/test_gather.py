"""Unit & black-box tests cho chế độ gather (Người 1 - ArsNeonci).
Tách riêng file test_gather.py để không xung đột Git với test_quan.py.
"""

import json
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import InputPlayer
from chonoi.runner import Session
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


def _tuning():
    return load_contract()["tuning"]


class GatherSlice1Test(unittest.TestCase):
    def test_dive_and_surface_events(self):
        tuning = _tuning()
        sd = tuning["gather"]["surface_depth"]
        # Bắt đầu trên mặt nước ngay sát ngưỡng surface_depth, bơi xuống rồi bơi lên
        s = Session("gather", tuning, {"player": {"pos": [10.0, sd]}}, 1)
        ip = InputPlayer([
            {"tick": 0, "move": [0, 1]},
            {"tick": 3, "move": [0, -1]},
        ])
        all_events = []
        for k in range(15):
            all_events.extend(s.step(ip.advance(k)))
        names = [e["name"] for e in all_events]
        self.assertIn("dive", names)
        self.assertIn("surface", names)
        dive_ev = next(e for e in all_events if e["name"] == "dive")
        surf_ev = next(e for e in all_events if e["name"] == "surface")
        self.assertGreater(dive_ev["data"]["pos"][1], sd)
        self.assertLessEqual(surf_ev["data"]["pos"][1], sd)

    def test_oxygen_drain_empty_and_refill_clamp(self):
        tuning = _tuning()
        g = tuning["gather"]
        omax = int(round(g["oxygen_max_s"] * 60))
        refill = int(g["oxygen_refill_per_tick"])
        # Dưới nước với 2 tick oxy -> tick 1 còn 1, tick 2 về 0 và phát oxygen_empty
        s = Session("gather", tuning, {"player": {"pos": [10.0, 5.0], "oxygen_ticks": 2}}, 1)
        ip = InputPlayer([])
        ev1 = s.step(ip.advance(0))
        self.assertEqual(s.sim.oxygen_ticks, 1)
        self.assertEqual(ev1, [])
        ev2 = s.step(ip.advance(1))
        self.assertEqual(s.sim.oxygen_ticks, 0)
        self.assertEqual([e["name"] for e in ev2], ["oxygen_empty"])
        self.assertEqual(s.sim.zero_oxy_ticks, 0)

        # Trên mặt nước: hồi oxygen_refill_per_tick và kẹp ở oxygen_max, xóa zero_oxy_ticks
        s2 = Session("gather", tuning, {"player": {"pos": [10.0, 0.0], "oxygen_ticks": omax - refill // 2}}, 1)
        s2.step(ip.advance(0))
        self.assertEqual(s2.sim.oxygen_ticks, omax)
        self.assertEqual(s2.sim.zero_oxy_ticks, 0)

    def test_choke_and_faint_clears_hold_and_writes_empty_inventory(self):
        tuning = _tuning()
        choke_ticks = int(tuning["gather"]["choke_interval_ticks"])
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [20.0, 10.0], "oxygen_ticks": 0, "hp": 2},
                    "hold": ["ca_loc", "bong_sung"],
                }
            })
            inv = w.path("inv.json")
            out = w.path("out.jsonl")
            code, err = run_headless(
                "--mode", "gather", "--seed", "1", "--ticks", str(choke_ticks * 3),
                "--scenario", sc, "--inventory-out", inv, "--out", out
            )
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            chokes = events(rows, "choke")
            faints = events(rows, "faint")
            ends = events(rows, "gather_end")
            self.assertEqual(len(chokes), 2)
            self.assertEqual(chokes[0]["tick"], choke_ticks)
            self.assertEqual(chokes[0]["data"]["hp"], 1)
            self.assertEqual(chokes[1]["tick"], choke_ticks * 2)
            self.assertEqual(chokes[1]["data"]["hp"], 0)
            self.assertEqual(len(faints), 1)
            self.assertEqual(faints[0]["tick"], choke_ticks * 2)
            self.assertEqual(len(ends), 1)
            self.assertEqual(ends[0]["data"]["reason"], "fainted")
            self.assertEqual(ends[0]["data"]["inventory"], {"items": {}})
            self.assertEqual(snapshots(rows)[-1]["hold"], [])
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {}})


if __name__ == "__main__":
    unittest.main()
