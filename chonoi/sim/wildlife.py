"""Đàn cá và Cá Sấu trong buổi lặn."""

import math

from ..ids import id_key, sort_by_id


def direction(origin, target):
    distance = math.dist(origin, target)
    if distance == 0:
        return [1, 0]
    return [(b - a) / distance for a, b in zip(origin, target)]


def spawn_fish(tuning, fish, streams, ids):
    points = {}
    for kind, depths in sorted(tuning["fish_spawn_depths"].items()):
        candidates = ([x, depth] for x in tuning["fish_spawn_x"] for depth in depths)
        points[kind] = [point for point in candidates if all(
            math.dist(point, school["pos"]) > tuning["fish_spawn_clearance"] for school in fish
        )]
    kinds = [kind for kind, candidates in points.items() if candidates]
    if not kinds:
        return None
    rng = streams.get("fish_spawn")
    kind = rng.choices(kinds, [tuning["fish_weights"][kind] for kind in kinds])[0]
    school = {"id": ids.new("F"), "kind": kind, "pos": rng.choice(points[kind]),
              "heading_deg": rng.random() * 360, "age_ticks": 0}
    fish.append(school)
    return school


def move_fish(school, tuning, streams, tick_hz):
    school["age_ticks"] += 1
    if school["age_ticks"] % tuning["fish_turn_ticks"] == 0:
        school["heading_deg"] = streams.get("fish_turn").random() * 360
    angle = math.radians(school["heading_deg"])
    heading = [math.cos(angle), math.sin(angle)]
    speed = tuning["fish_speed"] / tick_hz
    for axis, (low, high) in enumerate((tuning["fish_x"], tuning["fish_depths"][school["kind"]])):
        coordinate = school["pos"][axis] + heading[axis] * speed
        if coordinate < low or (coordinate == low and heading[axis] < 0):
            coordinate = 2 * low - coordinate
            heading[axis] *= -1
        elif coordinate > high or (coordinate == high and heading[axis] > 0):
            coordinate = 2 * high - coordinate
            heading[axis] *= -1
        school["pos"][axis] = coordinate
    school["heading_deg"] = math.degrees(math.atan2(heading[1], heading[0])) % 360


class Monsters:
    def __init__(self, tuning, scenario, ids, day, tick_hz):
        self.config = tuning.get("monsters", {})
        self.tick_hz = tick_hz
        self.x_bounds = tuning["bounds"]["x"]
        defaults = [{k: v for k, v in monster.items() if k != "from_day"}
                    for monster in self.config.get("spawns", []) if monster["from_day"] <= day]
        self.entities = sort_by_id([
            dict(m, pos=list(m["pos"]), target_idx=m.get("target_idx", 1), state=m.get("state", "patrol"),
                 state_ticks_left=m.get("state_ticks_left", 0), recoil_dir=m.get("recoil_dir"))
            for m in scenario.get("monsters", defaults)
        ])
        for monster in self.entities:
            ids.reserve(monster["id"])

    def step(self, player_pos, invulnerable):
        nearby = []
        for monster in self.entities:
            species = self.config["species"][monster["kind"]]
            if monster["state"] == "recoil":
                speed = species["recoil_dist"] / species["recoil_ticks"]
                self._move(monster, monster["recoil_dir"], speed, species)
                monster["state_ticks_left"] -= 1
                if monster["state_ticks_left"] == 0:
                    monster.update(state="patrol", recoil_dir=None)
                continue
            depth = player_pos[1] >= species["depths"][0]
            radius = species["exit_radius"] if monster["state"] == "chase" else species["detect_radius"]
            chasing = depth and math.dist(monster["pos"], player_pos) <= radius
            monster["state"] = "chase" if chasing else "patrol"
            target = player_pos if chasing else monster["waypoints"][monster["target_idx"]]
            speed = species[f"{monster['state']}_speed"] / self.tick_hz
            distance = math.dist(monster["pos"], target)
            self._move(monster, direction(monster["pos"], target), min(speed, distance), species)
            if not chasing and distance <= speed:
                monster["target_idx"] = 1 - monster["target_idx"]
            hit_distance = math.dist(monster["pos"], player_pos)
            if not invulnerable and depth and hit_distance <= species["hit_radius"]:
                nearby.append((hit_distance, id_key(monster["id"]), monster))
        if not nearby:
            return None
        _, _, monster = min(nearby)
        species = self.config["species"][monster["kind"]]
        monster.update(state="recoil", state_ticks_left=species["recoil_ticks"],
                       recoil_dir=direction(player_pos, monster["pos"]))
        return monster["id"]

    def _move(self, monster, heading, distance, species):
        for axis, (low, high) in enumerate((self.x_bounds, species["depths"])):
            monster["pos"][axis] = min(high, max(low, monster["pos"][axis] + heading[axis] * distance))
