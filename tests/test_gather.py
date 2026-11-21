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


class GatherSlice2Test(unittest.TestCase):
    def test_gather_node_tiebreak_regrow_and_hold_full(self):
        tuning = _tuning()
        g = tuning["gather"]
        regrow_ticks = int(round(g["regrow_s"] * 60))
        cap = int(g["hold_capacity"])
        # Hai nút cách đều x=10 (N10 ở 9.0, N2 ở 11.0) -> phải chọn N2 trước vì id_key("N2") < id_key("N10")
        sc = {
            "player": {"pos": [10.0, 0.0]},
            "nodes": [
                {"id": "N10", "kind": "bong_sung", "pos": [9.0, 0.0]},
                {"id": "N2", "kind": "bong_dien_dien", "pos": [11.0, 0.0]},
            ],
            "hold": ["ca_loc"] * (cap - 1),
        }
        s = Session("gather", tuning, sc, 1)
        ip = InputPlayer([
            {"tick": 0, "interact": True},
            {"tick": 1, "interact": False},
            {"tick": 2, "interact": True},
        ])
        ev0 = s.step(ip.advance(0))
        self.assertEqual(len(ev0), 1)
        self.assertEqual(ev0[0]["name"], "gather")
        self.assertEqual(ev0[0]["data"]["node_id"], "N2")
        self.assertEqual(s.sim.hold[-1], "bong_dien_dien")
        self.assertEqual(len(s.sim.hold), cap)
        n2 = next(n for n in s.sim.nodes if n["id"] == "N2")
        self.assertEqual(n2["regrow_ticks"], regrow_ticks)

        s.step(ip.advance(1))
        # Bước tick 2: N10 vẫn ready nhưng giỏ đã đầy -> phát hold_full, N10 vẫn ready
        ev2 = s.step(ip.advance(2))
        self.assertEqual([e["name"] for e in ev2], ["hold_full"])
        n10 = next(n for n in s.sim.nodes if n["id"] == "N10")
        self.assertEqual(n10["regrow_ticks"], 0)

    def test_node_regrown_after_countdown(self):
        tuning = _tuning()
        sc = {
            "player": {"pos": [50.0, 0.0]},
            "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [12.0, 0.0], "regrow_ticks": 2}],
        }
        s = Session("gather", tuning, sc, 1)
        ip = InputPlayer([])
        self.assertEqual(s.step(ip.advance(0)), [])
        ev1 = s.step(ip.advance(1))
        self.assertEqual(ev1, [{"type": "event", "tick": 2, "phase": "gather", "name": "node_regrown", "data": {"node_id": "N1"}}])
        self.assertTrue(s.snapshot()["nodes"][0]["ready"])

    def test_catch_fish_underwater_cooldown_and_hold_full(self):
        tuning = _tuning()
        g = tuning["gather"]
        cd_ticks = int(round(g["catch_cooldown_s"] * 60))
        cap = int(g["hold_capacity"])
        # Hai đàn cá cách đều (20, 10): F10 (ca_loc, yield 1) và F2 (ca_linh, yield 3) -> bắt F2 trước
        sc = {
            "player": {"pos": [20.0, 10.0]},
            "fish": [
                {"id": "F10", "kind": "ca_loc", "pos": [19.0, 10.0]},
                {"id": "F2", "kind": "ca_linh", "pos": [21.0, 10.0]},
            ],
        }
        s = Session("gather", tuning, sc, 1)
        ip = InputPlayer([
            {"tick": 0, "catch": True},
            {"tick": 1, "catch": False},
            {"tick": 2, "catch": True},  # đang cooldown -> không bắt được F10
        ])
        ev0 = s.step(ip.advance(0))
        self.assertEqual(len(ev0), 1)
        self.assertEqual(ev0[0]["name"], "fish_caught")
        self.assertEqual(ev0[0]["data"]["fish_id"], "F2")
        self.assertEqual(s.sim.hold, ["ca_linh"] * g["fish_yield"]["ca_linh"])
        self.assertEqual(s.sim.catch_cd_ticks, cd_ticks)
        self.assertEqual([f["id"] for f in s.sim.fish], ["F10"])

        s.step(ip.advance(1))
        ev2 = s.step(ip.advance(2))
        self.assertEqual(ev2, [], "đang trong thời gian hồi chiêu catch_cd_ticks thì không bắt được")
        self.assertEqual([f["id"] for f in s.sim.fish], ["F10"])

        # Kiểm tra hold_full khi bắt ca_linh (yield 3) nhưng giỏ chỉ còn 2 chỗ trống
        s_full = Session("gather", tuning, {
            "player": {"pos": [15.0, 5.0]},
            "hold": ["ca_loc"] * (cap - 2),
        }, 1)
        ev_full = s_full.step(InputPlayer([{"tick": 0, "catch": True}]).advance(0))
        self.assertEqual([e["name"] for e in ev_full], ["hold_full"])
        self.assertEqual(len(s_full.sim.fish), 6, "giỏ không đủ chỗ thì đàn cá không bị mất")


if __name__ == "__main__":
    unittest.main()
