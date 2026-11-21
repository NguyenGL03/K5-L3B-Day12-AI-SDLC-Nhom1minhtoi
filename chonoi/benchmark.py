"""Đo tốc độ vẽ của cảnh lặn trên Chromium ở 1280×720."""

import argparse
import json
import math
import os
import queue
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from secrets import token_urlsafe
from time import monotonic
from urllib.parse import urlencode

from .contract import load_contract
from .live import LiveGame, LiveServer


class DiveBenchmark(LiveGame):
    def _tick_once(self):
        tick = self.session.sim_tick
        beat = self.tuning["tick_hz"]
        leg = (tick // (4 * beat)) % 4
        move = ((1, 1), (1, 0), (-1, -1), (-1, 0))[leg]
        self.inputs.set(move=move, catch=tick % beat == 0)
        super()._tick_once()


def browser_executable():
    configured = os.environ.get("CHONOI_BROWSER")
    if configured:
        return shutil.which(configured) or (configured if Path(configured).is_file() else None)
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge"):
        candidate = shutil.which(name)
        if candidate:
            return candidate
    paths = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
             Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")]
    if sys.platform == "win32":
        for key in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
            if os.environ.get(key):
                root = Path(os.environ[key])
                paths += [root / "Microsoft/Edge/Application/msedge.exe", root / "Google/Chrome/Application/chrome.exe"]
        paths.sort(key=lambda path: "Edge" not in str(path))
    return next((str(path) for path in paths if path.is_file()), None)


def measure(tuning, browser, seed, duration):
    results = queue.SimpleQueue()
    token = token_urlsafe(18)
    fields = {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"}

    def receive(report):
        if not isinstance(report, dict) or report.pop("token", None) != token or report.keys() != fields:
            raise ValueError("báo cáo benchmark không hợp lệ")
        if any(type(n) not in (int, float) or not math.isfinite(n) or n <= 0 for n in report.values()):
            raise ValueError("số đo benchmark không hợp lệ")
        results.put(report)

    game = DiveBenchmark("gather", tuning, {"player": {"pos": [40, 2]}}, seed)
    server = LiveServer(game, port=0, benchmark_report=receive)
    query = urlencode({"bench_token": token, "bench_duration": duration})
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        server.start()
        process = None
        try:
            process = subprocess.Popen([
                browser, "--headless=new", "--no-first-run", "--no-default-browser-check",
                "--disable-background-networking", "--disable-extensions", "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
                "--window-size=1280,720", "--force-device-scale-factor=1", f"--user-data-dir={profile}",
                server.url + "?" + query,
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = monotonic() + duration + 25
            while monotonic() < deadline:
                try:
                    return results.get(timeout=0.5)
                except queue.Empty:
                    if process.poll() is not None:
                        raise RuntimeError(f"Chromium đã thoát với mã {process.returncode}") from None
            raise RuntimeError("Chromium không gửi kết quả đúng hạn")
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            server.stop()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("--duration phải là số giây dương hữu hạn")
    browser = browser_executable()
    if browser is None:
        parser.error("cần Chromium, Chrome hoặc Edge. Có thể đặt CHONOI_BROWSER tới file thực thi")
    try:
        report = measure(load_contract()["tuning"], browser, args.seed, args.duration)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, RuntimeError) as exc:
        print(f"benchmark: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
