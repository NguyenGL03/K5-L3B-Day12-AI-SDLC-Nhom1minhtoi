"""Nạp và kiểm scenario (Contract D). Trả về dict của đúng khối theo mode.

KHUNG: kiểm cú pháp, id trùng, bộ đếm âm, khoang vượt sức chứa, trường lạ.
TODO(nhóm): bổ sung kiểm mâu thuẫn mức luật mà nhóm cần (khách giữ chỗ quá kho, đơn assigned
phải có đúng một món, khách eating thiếu giá/tip...) — xem PRD-0 mục D và 'Mâu thuẫn -> mã 2'.
"""

import json
import math
from collections import Counter

from .errors import BadInput
from .inventory import ingredient_kinds, validate_individual_items, validate_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "random_fish", "time_left_ticks"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks"}
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


def resolve_day_plans(tuning, overrides):
    defaults = {entry["day"]: entry for entry in tuning["day_plan"]}
    menu = tuning["menu"]
    by_day = {}
    if not isinstance(overrides, list):
        raise BadInput("day.day_plan phải là mảng")
    for plan in overrides:
        if not isinstance(plan, dict) or set(plan) - {"day", "dishes", "ingredients"}:
            raise BadInput("mỗi kế hoạch cần day và dishes")
        day = plan.get("day")
        if type(day) is not int or day not in defaults or day in by_day:
            raise BadInput("day_plan.day phải có trong lịch và không trùng")
        by_day[day] = plan
    plans = {}
    for day in sorted(defaults):
        plan = by_day.get(day, defaults[day])
        dishes = plan.get("dishes")
        if not isinstance(dishes, dict) or not dishes or not dishes.keys() <= menu.keys():
            raise BadInput("day_plan phải dùng món có trong thực đơn")
        ingredients = Counter()
        for dish, servings in dishes.items():
            if type(servings) is not int or servings <= 0:
                raise BadInput("số suất trong day_plan phải là số nguyên dương")
            for kind, amount in menu[dish]["recipe"].items():
                ingredients[kind] += amount * servings
        if "ingredients" in plan and validate_items(plan["ingredients"], ingredient_kinds(tuning)) != ingredients:
            raise BadInput("day_plan.ingredients không khớp công thức")
        plans[day] = {"day": day, "dishes": dishes, "ingredients": dict(sorted(ingredients.items()))}
    return plans


def _validate_day(data, tuning):
    day = data.get("day", {})
    if not isinstance(day, dict) or set(day) - {"money", "earned", "reputation", "upgrades", "day_plan"}:
        raise BadInput("trường lạ trong day")
    if ("money" in day) != ("earned" in day):
        raise BadInput("day phải khai cả money và earned")
    for key in ("money", "earned"):
        _nonneg_int(f"day.{key}", day.get(key, 0))
    if day.get("money", 0) > day.get("earned", 0):
        raise BadInput("day.money không được vượt earned")
    upgrades = day.get("upgrades", {})
    catalog = tuning["shop"]["upgrades"]
    if not isinstance(upgrades, dict) or set(upgrades) - set(catalog):
        raise BadInput("day.upgrades không hợp lệ")
    q = tuning["quan"]
    reputation = day.get("reputation", q["reputation_initial"])
    if not _num(reputation) or not q["reputation_min"] <= reputation <= q["reputation_max"]:
        raise BadInput("day.reputation ngoài giới hạn")
    resolve_day_plans(tuning, day.get("day_plan", []))
    effective = dict(tuning, gather=dict(tuning["gather"]))
    for name, level in upgrades.items():
        _nonneg_int(f"day.upgrades.{name}", level)
        if level > len(catalog[name]):
            raise BadInput(f"day.upgrades.{name} vượt cấp tối đa")
        if level:
            effective["gather"].update(catalog[name][level - 1])
    quan = data.get("quan", {})
    if isinstance(quan, dict) and (quan.keys() & {"stock", "reputation"}):
        raise BadInput("mode day không nhận quan.stock hoặc quan.reputation")
    _validate_block(data.get("gather", {}), "gather", effective)
    _validate_block(quan, "quan", tuning)


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    allowed = {"day", "gather", "quan"} if mode == "day" else {mode}
    if not isinstance(data, dict) or not set(data) <= allowed:
        raise BadInput(f"khối scenario không hợp lệ cho mode {mode}")
    if mode == "day":
        _validate_day(data, tuning)
        return data
    block = data.get(mode, {})
    _validate_block(block, mode, tuning)
    return block


def _validate_block(block, mode, tuning):
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = GATHER_KEYS if mode == "gather" else QUAN_KEYS
    if mode == "gather" and "monsters" in tuning["gather"]:
        allowed = allowed | {"monsters"}
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    dur = int(round(tuning[mode]["duration_s"] * 60))
    if "time_left_ticks" in block:
        t = block["time_left_ticks"]
        if isinstance(t, bool) or not isinstance(t, int) or not (1 <= t <= dur):
            raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    for arr in ("nodes", "fish", "monsters"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        kinds = ingredient_kinds(tuning)
        if "freshness" in tuning:
            validate_individual_items(h, kinds)
        elif not isinstance(h, list) or any(not isinstance(k, str) or k not in kinds for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = int(round(g["oxygen_max_s"] * 60))
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        if not isinstance(n.get("kind"), str) or n["kind"] not in {node["kind"] for node in g["nodes"]}:
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        if not isinstance(f.get("kind"), str) or f["kind"] not in g["fish_yield"]:
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {FISH_KINDS}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")


        if "age_ticks" in f:
            _nonneg_int(f"fish.{f['id']}.age_ticks", f["age_ticks"])
        if "fish_depths" in g and b.get("random_fish", True):
            _pos(f"fish.{f['id']}.pos", f["pos"], {"x": g["fish_x"], "d": g["fish_depths"][f["kind"]]})
    for monster in b.get("monsters", []):
        _validate_monster(monster, g)


def _validate_monster(monster, gather):
    name = f"monsters.{monster['id']}"
    if set(monster) - {"id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir"}:
        raise BadInput(f"{name}: trường lạ")
    known = gather["monsters"]["species"]
    kind = monster.get("kind")
    if not isinstance(kind, str) or kind not in known:
        raise BadInput(f"{name}: kind không hợp lệ")
    bounds = {"x": gather["bounds"]["x"], "d": known[kind]["depths"]}
    _pos(f"{name}.pos", monster.get("pos"), bounds)
    waypoints = monster.get("waypoints")
    if not isinstance(waypoints, list) or len(waypoints) != 2:
        raise BadInput(f"{name}: cần hai waypoint")
    for waypoint in waypoints:
        _pos(f"{name}.waypoints", waypoint, bounds)
    index = monster.get("target_idx", 1)
    if type(index) is not int or index not in (0, 1):
        raise BadInput(f"{name}: target_idx phải là 0 hoặc 1")
    state, vector = monster.get("state", "patrol"), monster.get("recoil_dir")
    ticks = monster.get("state_ticks_left", 0)
    _nonneg_int(f"{name}.state_ticks_left", ticks)
    if state == "recoil":
        if not (ticks > 0 and isinstance(vector, list) and len(vector) == 2 and all(_num(n) for n in vector)
                and math.isclose(math.hypot(*vector), 1, abs_tol=1e-6)):
            raise BadInput(f"{name}: recoil cần timer dương và vector đơn vị")
    elif state not in ("patrol", "chase") or ticks != 0 or vector is not None:
        raise BadInput(f"{name}: trạng thái hoặc timer không hợp lệ")


def _validate_quan(b, tuning):
    for arr in ("stoves", "tables", "customers"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "stock" in b:
        validate = validate_individual_items if "freshness" in tuning else validate_items
        validate(b["stock"], ingredient_kinds(tuning))
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    table_ids = [c.get("table_id") for c in b.get("customers", [])]
    known = {t["id"] for t in tuning["quan"]["tables"]} | {t.get("id") for t in b.get("tables", [])}
    for c in b.get("customers", []):
        if not isinstance(c.get("table_id"), str) or c["table_id"] not in known:
            raise BadInput(f"customers.{c['id']}: table_id phải là bàn có thật")
    if len(table_ids) != len(set(table_ids)):
        raise BadInput("hai khách cùng bàn")
