"""Chạy nhiều Ngày liên tiếp bằng mô phỏng headless trong một tiến trình."""

import argparse
import json
import math
import sys
from pathlib import Path
from time import perf_counter

from .contract import load_contract
from .inputs import InputState
from .runner import Session


def bot_input(session):
    sim = session.sim
    tick = session.cycle.phase_tick
    hz = session.tuning["tick_hz"]
    if sim.phase == "gather" and tick < 16 * hz:
        edges = {"interact"} if tick >= 3 * hz and tick % (hz // 2) == 0 else set()
        return InputState((1, 0), {}, edges)
    if sim.phase == "gather":
        edges = {"interact"} if math.dist(sim.pos, sim.t["dock_pos"]) <= sim.t["dock_radius"] else set()
        return InputState((-1, 0), {}, edges)
    if sim.phase == "quan":
        if sim.hand is not None:
            order = next(c for c in sim.customers if c["id"] == sim.hand["order_id"])
            target = next(t for t in sim.tables if t["id"] == order["table_id"])
        else:
            target = sim.stoves[0]
        distance = math.dist(sim.pos, target["pos"])
        if distance > sim.t["interact_radius"] * 0.75:
            return InputState(tuple((b - a) / distance for a, b in zip(sim.pos, target["pos"])), {}, set())
        return InputState((0, 0), {}, {"interact"} if tick % 2 == 0 else set())
    if sim.phase == "shop" and tick == 0:
        for name, levels in sim.rules["upgrades"].items():
            level = sim.upgrades.get(name, 0)
            if level < len(levels) and levels[level]["price"] <= sim.money:
                return InputState((0, 0), {}, set(), buy=name)
    return InputState((0, 0), {}, set())


def play(tuning, seed, days):
    started = perf_counter()
    report = {"days": days, "days_completed": 0, "crashes": 0, "results": []}
    try:
        session = Session("day", tuning, {}, seed, days=days)
        limit = days * (sum(round(tuning[phase]["duration_s"] * tuning["tick_hz"])
                            for phase in ("gather", "quan")) + tuning["shop"]["max_ticks"])
        while not session.done and session.tick < limit:
            for row in session.step(bot_input(session)):
                if row["name"] == "shop_end":
                    end = session.end_row()
                    report["results"].append({"day": row["day"], **{
                        field: end[field] for field in ("earned", "reputation", "score")
                    }})
                    report["days_completed"] = session.cycle.days_completed
    except Exception as exc:
        report["crashes"] = 1
        print(f"soak: {exc}", file=sys.stderr)
    report["duration_s"] = perf_counter() - started
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be positive")
    report = play(load_contract()["tuning"], args.seed, args.days)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return int(report["crashes"] != 0 or report["days_completed"] != args.days)


if __name__ == "__main__":
    sys.exit(main())
