"""Vòng ngày headless gồm Lặn, Quán và Shop."""

from ..inventory import ingredient_kinds
from ..scenario import resolve_day_plans
from .gather import GatherSim
from .quan import QuanSim
from .quan_stock import QuanStock


class Shop:
    phase = "shop"

    def __init__(self, rules, quan, upgrades):
        self.rules = rules
        self.stock = quan.snapshot()["stock"]
        self.money = quan.money
        self.earned = quan.earned
        self.reputation = quan.reputation
        self.upgrades = upgrades
        self.time_left_ticks = rules["max_ticks"]
        self.done = False

    def snapshot(self):
        return {"stock": self.stock}

    def step(self, inp):
        self.time_left_ticks -= 1
        events = []
        if inp.buy is not None:
            events.append(self._buy(inp.buy))
        if inp.pressed("shop_done") or self.time_left_ticks == 0:
            self.done = True
            events.append(("shop_end", {"reason": "done" if inp.pressed("shop_done") else "time"}))
        return events

    def _buy(self, name):
        levels = self.rules["upgrades"].get(name)
        level = self.upgrades.get(name, 0)
        if levels is None:
            return "buy_failed", {"action": name, "reason": "unknown"}
        if level >= len(levels):
            return "buy_failed", {"action": name, "reason": "max_level"}
        upgrade = levels[level]
        price = upgrade["price"]
        if self.money < price:
            return "buy_failed", {"action": name, "reason": "funds"}
        self.money -= price
        self.upgrades[name] = upgrade["level"]
        return "bought", {"upgrade": name, "level": upgrade["level"], "price": price, "money": self.money}


class DayCycle:
    def __init__(self, tuning, scenario, streams, ids, days):
        self.tuning = tuning
        self.scenario = scenario
        self.streams = streams
        self.ids = ids
        self.days = days
        fixture = scenario.get("day", {})
        self.schedule = tuple(resolve_day_plans(tuning, fixture.get("day_plan", [])).values())
        self.upgrades = {name: level for name, level in fixture.get("upgrades", {}).items() if level}
        self.day = 1
        self.days_completed = 0
        self.done = False
        self.reason = None
        self.phase_tick = 0
        self.current = self._gather(fixture.get("money", 0), fixture.get("earned", 0),
                                    fixture.get("reputation", tuning["quan"]["reputation_initial"]))

    def _gather(self, money, earned, reputation):
        self.active_upgrades = self.upgrades.copy()
        sim = GatherSim(self.tuning, self.scenario.get("gather", {}), self.streams, self.ids,
                        day=self.day, upgrades=self.active_upgrades)
        sim.money, sim.earned, sim.reputation = money, earned, reputation
        return sim

    def metadata(self):
        return {"day": self.day, "day_plan": self.plan,
                "upgrades": self.upgrades.copy(), "active_upgrades": self.active_upgrades.copy()}

    @property
    def plan(self):
        return dict(self.schedule[(self.day - 1) % len(self.schedule)], day=self.day)

    def _events(self, events):
        return [dict(phase=self.current.phase, day=self.day, name=name, data=data) for name, data in events]

    def initial_events(self):
        plan = self.plan
        return self._events([("day_start", {}), ("day_plan", {"dishes": plan["dishes"], "ingredients": plan["ingredients"]}),
                             ("phase_start", {})])

    def step(self, inp):
        sim = self.current
        events = self._events(sim.step(inp))
        self.phase_tick += 1
        if not sim.done:
            return events
        if sim.phase == "gather":
            context = dict(self.scenario.get("quan", {}), reputation=sim.reputation)
            inventory = (sim.inventory_items() if sim.freshness is None else
                         QuanStock(sim.hold, ingredient_kinds(self.tuning), sim.freshness, sim.tick_hz, exact=True))
            self.current = QuanSim(self.tuning, context, self.streams, self.ids, inventory=inventory,
                                   day_plan=self.plan, money=sim.money, earned=sim.earned)
        elif sim.phase == "quan":
            self.current = Shop(self.tuning["shop"], sim, self.upgrades)
        else:
            self.days_completed += 1
            if self.days_completed == self.days:
                self.done = True
                self.reason = "days_complete"
            else:
                self.day += 1
                self.phase_tick = 0
                self.current = self._gather(sim.money, sim.earned, sim.reputation)
                events.extend(self.initial_events())
            return events
        self.phase_tick = 0
        events.extend(self._events([("phase_start", {})]))
        return events
