"""Buổi tối — Mở Quán. Một đơn đi qua chờ nấu, đã giao bếp và đang ăn."""

import math
from collections import Counter
from decimal import Decimal

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from ..inventory import validate_items
from ..scenario import _nonneg_int, _pos
from .ramp import ramp_velocity
from .quan_stock import QuanStock

STOVE_FIELDS = ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")
TABLE_FIELDS = ("id", "pos")
CUSTOMER_FIELDS = {"id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left",
                   "eat_ticks_left", "order_status", "reserved", "base_price", "tip"}
DISH_FIELDS = {"order_id", "dish_id", "base_price"}


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, *, day_plan=None, money=0, earned=0):
        t = tuning["quan"]
        self.t = t
        menu = tuning["menu"]
        self.kinds = {kind for dish in menu.values() for kind in dish["recipe"]}
        self.menu = menu
        if day_plan is not None:
            dishes = day_plan.get("dishes") if isinstance(day_plan, dict) else None
            if not isinstance(dishes, dict) or not dishes or not dishes.keys() <= menu.keys():
                raise BadInput("kế hoạch ngày phải dùng món trong thực đơn")
            self.menu = {dish_id: menu[dish_id] for dish_id in dishes}
        self.rng = streams
        self.ids = ids
        self.tick_hz = tuning["tick_hz"]
        self.tick = 0
        self.patience_ticks = self._ticks(t["patience_s"])
        self.eat_ticks = self._ticks(t["eat_s"])
        self.customer_interval = self._ticks(t["customer_interval_s"])
        self.next_customer_tick = t["first_customer_tick"]
        self.random_customers = scenario.get("random_customers", True)
        if not isinstance(self.random_customers, bool):
            raise BadInput("random_customers phải là boolean")
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        if not all(math.isfinite(c) for c in self.vel):
            raise BadInput("quan.player.vel phải chứa hai số hữu hạn")
        self.ramp_max_ticks = t["ramp_max_ticks"]
        self._tgt = None
        self._ramp_left = 0
        if inventory is not None and "stock" in scenario:
            raise BadInput("vừa có quan.stock vừa có kho bàn giao")
        self.freshness = tuning.get("freshness")
        source = inventory if inventory is not None else scenario.get("stock", [] if self.freshness else {})
        self.fresh_stock = None
        if self.freshness is not None:
            self.fresh_stock = source if isinstance(source, QuanStock) else QuanStock(source, self.kinds, self.freshness, self.tick_hz)
        else:
            self.stock = validate_items(source, self.kinds)
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", self._ticks(t["duration_s"]))
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        if (type(self.reputation) not in (int, float) or
                not t["reputation_min"] <= self.reputation <= t["reputation_max"]):
            raise BadInput("reputation phải là số trong giới hạn uy tín")
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge("stoves", scenario.get("stoves", []), STOVE_FIELDS)]
        self.tables = self._merge("tables", scenario.get("tables", []), TABLE_FIELDS)
        self.customers = [self._load_customer(c) for c in scenario.get("customers", [])]
        self._validate_stock_claims()
        self._match_scenario_orders()
        _nonneg_int("money", money)
        _nonneg_int("earned", earned)
        if money > earned:
            raise BadInput("money không được vượt earned")
        self.money = money
        self.earned = earned
        self.shift_earned = 0
        self.done = False
        self.reason = None

    def _merge(self, name, updates, fields):
        by_id = {d["id"]: dict(d) for d in self.t[name]}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            self._check_fields(f"{name}.{u['id']}", u, fields)
            if "pos" in u:
                _pos(f"{name}.{u['id']}.pos", u["pos"], self.t["bounds"], axes=("x", "z"))
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _ticks(self, seconds):
        return max(1, round(seconds * self.tick_hz))

    def _available_dishes(self):
        if self.fresh_stock is not None:
            claimed = self._claimed()
            return [dish_id for dish_id, dish in sorted(self.menu.items())
                    if self.fresh_stock.reserve(dish["recipe"], claimed) is not None]
        reserved = Counter()
        for customer in self.customers:
            reserved.update(customer["reserved"])
        return [dish_id for dish_id, dish in sorted(self.menu.items())
                if all(self.stock.get(kind, 0) - reserved[kind] >= count
                       for kind, count in dish["recipe"].items())]

    def _claimed(self, except_customer=None):
        return {item_id for c in self.customers if c is not except_customer for item_id in c["reserved"]}

    def _validate_stock_claims(self):
        if self.fresh_stock is None:
            available = self.stock.copy()
            for customer in sorted(self.customers, key=self._order_priority):
                for kind, count in customer["reserved"].items():
                    available[kind] = available.get(kind, 0) - count
                    if available[kind] < 0:
                        raise BadInput(f"customers.{customer['id']}: giữ chỗ vượt số lượng còn trong kho")
            return
        claimed = set()
        ordered = sorted(self.customers, key=self._order_priority)
        # Giữ chỗ khai tường minh thuộc fixture. Cấp các đơn còn thiếu theo thứ tự gọi món.
        for c in ordered:
            if "reserved" in c:
                recipe = self.menu[c["dish_id"]]["recipe"] if c["order_status"] == "reserved" else {}
                self.fresh_stock.validate_reservation(recipe, c["reserved"], claimed)
                claimed.update(c["reserved"])
        for c in ordered:
            if "reserved" in c:
                continue
            recipe = self.menu[c["dish_id"]]["recipe"] if c["order_status"] == "reserved" else {}
            reserved = self.fresh_stock.reserve(recipe, claimed)
            if reserved is None:
                raise BadInput(f"customers.{c['id']}: không đủ cá thể để giữ chỗ")
            c["reserved"] = reserved
            claimed.update(reserved)

    def _load_customer(self, source):
        name = f"customers.{source['id']}"
        self._check_fields(name, source, CUSTOMER_FIELDS)
        if not isinstance(source.get("dish_id"), str) or source["dish_id"] not in self.menu:
            raise BadInput(f"{name}.dish_id phải là món có trong thực đơn")
        if not any(t["id"] == source.get("table_id") for t in self.tables):
            raise BadInput(f"{name}.table_id phải là bàn có thật")

        customer = dict(state="waiting", order_tick=0, order_status="reserved", eat_ticks_left=0,
                        patience_ticks_left=self.patience_ticks, base_price=0, tip=0)
        customer.update(source)
        status = customer["order_status"]
        state = customer["state"]
        if ((state == "waiting" and status not in ("reserved", "assigned", "unfulfillable")) or
                (state == "eating" and status != "served") or state not in ("waiting", "eating")):
            raise BadInput(f"{name}: state và order_status không khớp")
        for field in ("order_tick", "patience_ticks_left", "eat_ticks_left", "base_price", "tip"):
            _nonneg_int(f"{name}.{field}", customer[field])
        if customer["patience_ticks_left"] > self.patience_ticks:
            raise BadInput(f"{name}.patience_ticks_left vượt quá kiên nhẫn tối đa")
        if state == "eating":
            if not (0 < customer["eat_ticks_left"] <= self.eat_ticks and customer["base_price"] > 0 and "tip" in source):
                raise BadInput(f"{name}: khách đang ăn cần timer, base_price và tip đã chốt")
        elif customer["eat_ticks_left"] != 0 or customer["tip"] != 0:
            raise BadInput(f"{name}: khách đang chờ chưa có timer ăn hoặc tiền boa")
        if self.fresh_stock is None:
            reserved = self.menu[customer["dish_id"]]["recipe"] if status == "reserved" else {}
            actual = customer.get("reserved", reserved)
            validate_items(actual, self.kinds)
            if actual != reserved:
                raise BadInput(f"{name}.reserved không khớp trạng thái và công thức")
            customer["reserved"] = dict(reserved)
        self.ids.reserve(customer["id"])
        return customer

    @staticmethod
    def _check_fields(name, entity, allowed):
        extra = set(entity).difference(allowed)
        if extra:
            raise BadInput(f"{name}: trường lạ/chưa hỗ trợ: {sorted(extra)}")

    @staticmethod
    def _order_priority(customer):
        return customer["order_tick"], id_key(customer["table_id"])

    def _match_scenario_orders(self):
        unmatched = {c["id"]: c for c in self.customers if c["order_status"] == "assigned"}

        for stove in self.stoves:
            name = f"stoves.{stove['id']}"
            cook, ready = stove["cook_ticks_left"], stove["ready_ticks"]
            _nonneg_int(f"{name}.cook_ticks_left", cook)
            _nonneg_int(f"{name}.ready_ticks", ready)
            state, dish = stove["state"], stove["dish"]
            if not ((state == "idle" and dish is None and cook == ready == 0) or
                    (state == "cooking" and dish is not None and cook > 0 and ready == 0) or
                    (state == "ready" and dish is not None and cook == 0)):
                raise BadInput(f"{name}: trạng thái bếp, món và timer không khớp")
            if dish is not None:
                self._match_dish(f"{name}.dish", dish, unmatched)
        if self.hand is not None:
            self._match_dish("hand", self.hand, unmatched)
        if unmatched:
            raise BadInput("đơn assigned thiếu món ở bếp hoặc trên tay")

    @staticmethod
    def _match_dish(name, dish, unmatched):
        if not isinstance(dish, dict) or set(dish) != DISH_FIELDS:
            raise BadInput(f"{name} phải chứa order_id, dish_id và base_price")
        order_id = dish["order_id"]
        customer = unmatched.pop(order_id, None) if isinstance(order_id, str) else None
        if customer is None or dish["dish_id"] != customer["dish_id"]:
            raise BadInput(f"{name}: món phải khớp một đơn assigned chưa có món")
        price = dish["base_price"]
        if type(price) is not int or price <= 0 or customer["base_price"] not in (0, price):
            raise BadInput(f"{name}.base_price không khớp giá đã chốt")
        customer["base_price"] = price

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": self.fresh_stock.snapshot() if self.fresh_stock is not None else
                     {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{field: s[field] for field in STOVE_FIELDS} for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        events = []
        self.tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self._advance_customers()
        if self.fresh_stock is not None:
            spoiled = self.fresh_stock.advance()
            events.extend(spoiled)
            if spoiled:
                self._refresh_reservations()
        self._advance_stoves(events)
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        self._settle_customers(events)
        if self.time_left_ticks == 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        elif self.random_customers and self.tick == self.next_customer_tick:
            self.next_customer_tick += self.customer_interval
            self._arrive(events)
        return events

    def _refresh_reservations(self):
        for customer in sorted(self.customers, key=self._order_priority):
            if customer["order_status"] != "reserved":
                continue
            recipe = self.menu[customer["dish_id"]]["recipe"]
            reserved = self.fresh_stock.replace_spoiled(recipe, customer["reserved"], self._claimed(customer))
            if reserved is None:
                customer.update(order_status="unfulfillable", reserved=[])
            else:
                customer["reserved"] = reserved

    def _arrive(self, events):
        occupied = {c["table_id"] for c in self.customers}
        table = next((t for t in self.tables if t["id"] not in occupied), None)
        if table is None:
            return
        dishes = self._available_dishes()
        if not dishes:
            events.append(("no_dish", {}))
            return
        dish_id = self.rng.get("customer_order").choice(dishes)
        recipe = self.menu[dish_id]["recipe"]
        reserved = dict(recipe) if self.fresh_stock is None else self.fresh_stock.reserve(recipe, self._claimed())
        customer = {"id": self.ids.new("C"), "table_id": table["id"], "dish_id": dish_id,
                    "state": "waiting", "order_tick": self.tick, "order_status": "reserved",
                    "patience_ticks_left": self.patience_ticks, "eat_ticks_left": 0, "base_price": 0, "tip": 0,
                    "reserved": reserved}
        self.customers.append(customer)
        events.append(("customer_arrived", self._order(customer)))

    @staticmethod
    def _order(customer):
        return {"order_id": customer["id"], "table_id": customer["table_id"],
                "dish_id": customer["dish_id"]}

    @staticmethod
    def _stove_order(stove):
        return {"order_id": stove["dish"]["order_id"], "stove_id": stove["id"], "dish_id": stove["dish"]["dish_id"]}

    @staticmethod
    def _clear_stove(stove):
        stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)

    def _advance_stoves(self, events):
        for stove in self.stoves:
            if stove["state"] == "cooking":
                stove["cook_ticks_left"] = max(0, stove["cook_ticks_left"] - 1)
                if stove["cook_ticks_left"] == 0:
                    stove.update(state="ready", ready_ticks=0)
                    events.append(("dish_ready", self._stove_order(stove)))
            elif stove["state"] == "ready":
                stove["ready_ticks"] += 1

    def _advance_customers(self):
        for customer in self.customers:
            timer = "eat_ticks_left" if customer["state"] == "eating" else "patience_ticks_left"
            customer[timer] = max(0, customer[timer] - 1)

    def _settle_customers(self, events):
        closing = self.time_left_ticks == 0
        for customer in sort_by_id(self.customers, key=lambda c: c["table_id"]):
            if customer["state"] == "eating":
                if customer["eat_ticks_left"] == 0:
                    self._pay(customer, "finished_eating", events)
                elif closing:
                    self._pay(customer, "closing", events)
            elif closing:
                self._leave(customer, "closing", events)
            elif customer["patience_ticks_left"] == 0:
                self._leave(customer, "patience", events)

    def _leave(self, customer, reason, events):
        order_id = customer["id"]
        for stove in self.stoves:
            if stove["dish"] is not None and stove["dish"]["order_id"] == order_id:
                self._clear_stove(stove)
        if self.hand is not None and self.hand["order_id"] == order_id:
            self.hand = None
        self.customers.remove(customer)
        if reason == "patience":
            self._change_reputation(self.t["left_reputation_delta"])
        events.append(("customer_left", {"order_id": order_id, "table_id": customer["table_id"],
                                         "reason": reason, "reputation": self.reputation}))

    def _pay(self, customer, reason, events):
        price, tip = customer["base_price"], customer["tip"]
        total = price + tip
        self.money += total
        self.earned += total
        self.shift_earned += total
        if tip:
            self._change_reputation(self.t["tip_reputation"])
        self.customers.remove(customer)
        events.append(("paid", {"order_id": customer["id"], "table_id": customer["table_id"],
                                "base_price": price, "tip": tip, "amount": total, "reason": reason}))

    def _change_reputation(self, delta):
        reputation = float(Decimal(str(self.reputation)) + Decimal(str(delta)))
        self.reputation = min(self.t["reputation_max"], max(self.t["reputation_min"], reputation))

    def _interact(self, events):
        nearby = []
        for priority, group in enumerate((self.stoves, self.tables)):
            for entity in group:
                distance = math.dist(self.pos, entity["pos"])
                if distance <= self.t["interact_radius"]:
                    nearby.append((distance, priority, id_key(entity["id"]), entity))
        if not nearby:
            return
        _, priority, _, target = min(nearby, key=lambda candidate: candidate[:3])
        if priority == 0:
            self._use_stove(target, events)
        else:
            self._serve(target, events)

    def _use_stove(self, stove, events):
        if stove["state"] == "ready" and self.hand is None:
            order = self._stove_order(stove)
            self.hand = stove["dish"]
            self._clear_stove(stove)
            events.append(("dish_picked", order))
        elif stove["state"] == "idle":
            customer = min((c for c in self.customers if c["order_status"] == "reserved"),
                           key=self._order_priority, default=None)
            if customer is None:
                return
            dish_id = customer["dish_id"]
            price = self.menu[dish_id]["price"]
            if self.fresh_stock is None:
                items = []
                for kind, count in sorted(customer["reserved"].items()):
                    self.stock[kind] -= count
                    items.extend([kind] * count)
                empty = {}
            else:
                items, price = self.fresh_stock.consume(customer["reserved"], price, self.freshness["initial"])
                empty = []
            customer.update(order_status="assigned", reserved=empty, base_price=price)
            dish = {"order_id": customer["id"], "dish_id": dish_id, "base_price": price}
            stove.update(state="cooking", dish=dish,
                         cook_ticks_left=self._ticks(self.menu[dish_id]["cook_s"]), ready_ticks=0)
            events.append(("cook_started", dict(self._stove_order(stove), items=items, base_price=price)))

    def _serve(self, table, events):
        if self.hand is None:
            return
        customer = next((c for c in self.customers if c["table_id"] == table["id"]), None)
        if customer is None or customer["id"] != self.hand["order_id"]:
            return
        price = self.hand["base_price"]
        tip_threshold = self.patience_ticks * Decimal(str(self.t["tip_min_patience_ratio"]))
        early = customer["patience_ticks_left"] >= tip_threshold
        tip = int(price * Decimal(str(self.t["tip_rate"]))) if early else 0
        customer.update(state="eating", order_status="served", eat_ticks_left=self.eat_ticks, base_price=price, tip=tip)
        self.hand = None
        events.append(("served", dict(self._order(customer), patience_ticks_left=customer["patience_ticks_left"],
                                      base_price=price, tip=tip)))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), self.ramp_max_ticks)
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / self.tick_hz
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
