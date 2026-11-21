"""Chạy và đối chiếu hai lượt headless theo manifest hiện tại."""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "game.contract.json").read_text(encoding="utf-8"))
    tuning = manifest["tuning"]
    max_ticks = sum(round(tuning[phase]["duration_s"] * tuning["tick_hz"]) for phase in ("gather", "quan"))
    max_ticks += tuning["shop"]["max_ticks"]
    headless = [sys.executable, "-m", "chonoi.headless", "--mode", "day", "--days", "1", "--seed", "1",
                "--ticks", str(max_ticks)]
    with tempfile.TemporaryDirectory() as directory:
        outputs = []
        for suffix in ("first", "second"):
            out = Path(directory) / f"{suffix}.jsonl"
            started = time.perf_counter()
            subprocess.run([*headless, "--out", str(out)], cwd=root, check=True)
            print(f"{suffix}: {time.perf_counter() - started:.2f} s")
            outputs.append(out.read_bytes())
    if outputs[0] != outputs[1]:
        raise SystemExit("Hai lượt cùng seed cho JSONL khác nhau")
    rows = [json.loads(line) for line in outputs[0].splitlines()]
    phases = [row["phase"] for row in rows if row.get("name") == "phase_start"]
    end = rows[-1]
    if phases != ["gather", "quan", "shop"] or end.get("reason") != "days_complete" or end.get("days_completed") != 1:
        raise SystemExit("Lượt headless chưa hoàn tất đúng một Ngày")
    print(f"gather -> quan -> shop, {end['sim_tick']} ticks, byte-identical JSONL")


if __name__ == "__main__":
    main()
