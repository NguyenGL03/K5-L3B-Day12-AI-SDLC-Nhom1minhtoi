"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.

`Session` là API bước tick gọn dùng chung cho headless (`run`) và cửa sổ chơi trực tiếp (`chonoi.live`):
cả hai chạy CÙNG một lớp sim, không nhân đôi logic.
"""

import math

from .ids import IdAllocator
from .inputs import BUTTONS_V10, BUTTONS_V11, InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.day import DayCycle
from .sim.gather import GatherSim
from .sim.quan import QuanSim


def build_sim(mode, tuning, scenario, seed, inventory):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    return QuanSim(tuning, scenario, streams, ids, inventory=inventory)


def _common(sim, mode, tick, sim_tick, phase_tick, tuning, state):
    mult = tuning["score"]["reputation_multiplier"]
    return {
        "type": "snapshot", "tick": tick, "sim_tick": sim_tick, "mode": mode, "phase": sim.phase,
        "phase_tick": phase_tick, "state": state, "time_left_ticks": sim.time_left_ticks,
        "money": sim.money, "earned": sim.earned, "reputation": sim.reputation,
        "score": sim.earned + mult * math.floor(sim.reputation),
    }


class Session:
    """Một lượt chơi: dựng sim, bước từng tick, lấy snapshot / dòng end."""

    def __init__(self, mode, tuning, scenario, seed, inventory=None, days=1):
        self.mode = mode
        self.tuning = tuning
        self.cycle = DayCycle(tuning, scenario, Streams(seed), IdAllocator(), days) if mode == "day" else None
        self.independent = None if self.cycle else build_sim(mode, tuning, scenario, seed, inventory)
        self.tick = 0
        self.sim_tick = 0
        self.paused = False

    @property
    def sim(self):
        return self.cycle.current if self.cycle else self.independent

    @property
    def done(self) -> bool:
        return self.cycle.done if self.cycle else self.sim.done

    @property
    def state(self):
        return "finished" if self.done else "paused" if self.paused else "playing"

    def snapshot(self) -> dict:
        phase_tick = self.cycle.phase_tick if self.cycle else self.sim_tick
        s = _common(self.sim, self.mode, self.tick, self.sim_tick, phase_tick, self.tuning, self.state)
        if self.cycle:
            s.update(self.cycle.metadata())
        s.update(self.sim.snapshot())
        return s

    def step(self, inp) -> list:
        """Chạy một bước với `inp` (chonoi.inputs.InputState); trả các dòng event (tick = k + 1)."""
        self.tick += 1
        events = []
        if inp.pressed("pause"):
            self.paused = not self.paused
            event = dict(phase=self.sim.phase, name="paused" if self.paused else "resumed", data={})
            if self.cycle:
                event["day"] = self.cycle.day
            events.append(event)
        if not self.paused:
            self.sim_tick += 1
            if self.cycle:
                events.extend(self.cycle.step(inp))
            else:
                events.extend(dict(phase=self.sim.phase, name=name, data=data) for name, data in self.sim.step(inp))
        return self._event_rows(events)

    def _event_rows(self, events):
        return [dict(type="event", tick=self.tick, **event) for event in events]

    def initial_events(self):
        return self._event_rows(self.cycle.initial_events()) if self.cycle else []

    def end_row(self) -> dict:
        sim = self.sim
        score = _common(sim, self.mode, self.tick, self.sim_tick, 0, self.tuning, self.state)["score"]
        reason = self.cycle.reason if self.cycle else sim.reason
        row = {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": self.mode,
                "state": self.state, "reason": reason if self.done else "tick_limit",
                "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": score}
        if self.cycle:
            row["days_completed"] = self.cycle.days_completed
        return row

    def write_inventory_if_done(self, inventory_out):
        """File kho: ghi MỘT lần khi có gather_end; chưa kết thúc thì giữ nguyên file đích."""
        if self.mode == "gather" and self.sim.done and inventory_out:
            write_inventory(inventory_out, self.sim.inventory_items())


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None, *, days=1):
    sess = Session(mode, tuning, scenario, seed, inventory, days)
    player = InputPlayer(frames, BUTTONS_V11 if "day_plan" in tuning else BUTTONS_V10)
    w = JsonlWriter(out_path)
    try:
        for row in sess.initial_events():
            w.write(row)
        w.write(sess.snapshot())
        last_snapped = 0
        while sess.tick < ticks and not sess.done:
            inp = player.advance(sess.tick)  # bước k đọc input có tick == k
            events = sess.step(inp)
            for row in events:
                w.write(row)
            if sess.tick % snapshot_every == 0 or sess.done or any(row["name"] == "phase_start" for row in events):
                w.write(sess.snapshot())
                last_snapped = sess.tick
        if last_snapped != sess.tick:
            w.write(sess.snapshot())
        w.write(sess.end_row())
    finally:
        w.close()
    sess.write_inventory_if_done(inventory_out)
    return sess.sim
