import json
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from chonoi.headless import main

from helpers import ROOT, Workdir, events, read_jsonl, snapshots, write_json


class CurrentContract(unittest.TestCase):
    def test_invalid_gather_fixtures_are_rejected_before_output(self):
        invalid = [
            {"nodes": [{"id": "N1", "kind": "invalid", "pos": [20, 0]}]},
            {"fish": [{"id": "F1", "kind": "invalid", "pos": [15, 5]}]},
            {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [20, 0], "typo": 1}]},
            {"fish": [{"id": "F1", "kind": "ca_linh", "pos": [15, 5], "typo": 1}]},
            {"player": {"heading_deg": float("inf")}},
            {"player": {"vel": [float("nan"), 0]}},
        ]
        with Workdir() as w:
            out = w.path("out.jsonl")
            for fixture in invalid:
                with self.subTest(fixture=fixture), redirect_stderr(StringIO()):
                    scenario = write_json(w.path("scenario.json"), {"gather": fixture})
                    code = main(["--mode", "gather", "--seed", "1", "--ticks", "0", "--out", out, "--scenario", scenario])
                    self.assertEqual(code, 2)
                    self.assertFalse(Path(out).exists())

    def test_file_handoff_preserves_individual_freshness(self):
        with Workdir() as w:
            scenario = write_json(w.path("gather.json"), {"gather": {"hold": [
                {"id": "I10", "kind": "ca_linh", "fresh": 30}, {"id": "I2", "kind": "ca_loc", "fresh": 100}
            ]}})
            inputs = write_json(w.path("inputs.json"), {"frames": [{"tick": 0, "interact": True}]})
            gather, quan, stock = (w.path(name) for name in ("gather.jsonl", "quan.jsonl", "stock.json"))
            self.assertEqual(main(["--mode", "gather", "--seed", "7", "--ticks", "1", "--scenario", scenario,
                                   "--inputs", inputs, "--out", gather, "--inventory-out", stock]), 0)
            self.assertEqual(main(["--mode", "quan", "--seed", "7", "--ticks", "0", "--out", quan, "--inventory", stock]), 0)
            saved = json.loads(Path(stock).read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in saved["items"]], ["I2", "I10"])
            self.assertLess(saved["items"][1]["fresh"], 30)
            self.assertEqual(events(read_jsonl(gather), "gather_end")[0]["data"]["inventory"], saved)
            self.assertEqual(snapshots(read_jsonl(quan))[0]["stock"], saved["items"])

    def test_rehearsal_day_harvests_cooks_gets_paid_and_closes_shop(self):
        demo = Path(ROOT) / "docs/proof/phase-4"
        with Workdir() as w:
            out = w.path("day.jsonl")
            self.assertEqual(main(["--mode", "day", "--days", "1", "--seed", "7", "--ticks", "2050",
                                   "--out", out, "--scenario", str(demo / "demo-scenario.json"),
                                   "--inputs", str(demo / "demo-inputs.json")]), 0)
            rows = read_jsonl(out)
            trace = events(rows)
            self.assertEqual(len(events(rows, "gather")), 2)
            self.assertEqual(len(events(rows, "fish_caught")), 1)
            self.assertEqual(events(rows, "gather_end")[0]["data"]["reason"], "docked")
            self.assertTrue(events(rows, "cook_started"))
            self.assertTrue(events(rows, "paid"))
            self.assertEqual(trace[-1]["name"], "shop_end")
            self.assertEqual(trace[-1]["data"]["reason"], "done")
            self.assertEqual((rows[-1]["days_completed"], rows[-1]["reason"]), (1, "days_complete"))
