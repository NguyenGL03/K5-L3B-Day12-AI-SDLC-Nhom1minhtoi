"""Script tự động kiểm chứng chế độ gather và sinh bằng chứng vào docs/proof/phase-<n>/."""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def run_cmd(args):
    res = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(f"Lệnh thất bại ({res.returncode}): {' '.join(args)}\n{res.stderr}\n")
        sys.exit(res.returncode)
    return res


def main():
    p = argparse.ArgumentParser(description="Sinh bằng chứng headless cho chế độ gather.")
    p.add_argument("--phase", type=int, default=1, help="Số thứ tự phase (mặc định: 1)")
    a = p.parse_args()

    out_dir = os.path.join(ROOT, "docs", "proof", f"phase-{a.phase}")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Kịch bản bơi từ bến (2,0) -> hái N1 (12,0) -> lặn bắt F1 (15,5) -> bơi về bến (2,0) cập bến
    inputs_path = os.path.join(out_dir, "gather-inputs.json")
    frames = {
        "frames": [
            {"tick": 0, "move": [1, 0]},
            {"tick": 155, "move": [0, 0], "interact": True},
            {"tick": 156, "interact": False, "move": [0.5, 1]},
            {"tick": 245, "move": [0, 0], "catch": True},
            {"tick": 246, "catch": False, "move": [-1, -0.45]},
            {"tick": 460, "move": [0, 0], "interact": True},
        ]
    }
    with open(inputs_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(frames, f, ensure_ascii=False, indent=2)
        f.write("\n")

    docked_jsonl = os.path.join(out_dir, "gather-docked.jsonl")
    docked_jsonl_2 = os.path.join(out_dir, "gather-docked-verify.jsonl")
    kho_json = os.path.join(out_dir, "gather-kho.json")

    run_cmd([
        "-m", "chonoi.headless", "--mode", "gather", "--seed", "1", "--ticks", "600",
        "--inputs", inputs_path, "--inventory-out", kho_json, "--out", docked_jsonl,
    ])
    run_cmd([
        "-m", "chonoi.headless", "--mode", "gather", "--seed", "1", "--ticks", "600",
        "--inputs", inputs_path, "--out", docked_jsonl_2,
    ])

    with open(docked_jsonl, "rb") as f1, open(docked_jsonl_2, "rb") as f2:
        if f1.read() != f2.read():
            sys.stderr.write("LỖI: Kết quả headless không tất định (byte mismatch)!\n")
            sys.exit(1)
    os.remove(docked_jsonl_2)

    # 2. Kịch bản ngất dưới nước (fainted -> mất giỏ, kho rỗng)
    faint_sc = os.path.join(out_dir, "gather-faint-scenario.json")
    faint_jsonl = os.path.join(out_dir, "gather-fainted.jsonl")
    with open(faint_sc, "w", encoding="utf-8", newline="\n") as f:
        json.dump({
            "gather": {
                "player": {"pos": [20, 10], "oxygen_ticks": 2, "hp": 1},
                "hold": ["ca_loc", "bong_sung"],
            }
        }, f, ensure_ascii=False)
        f.write("\n")

    run_cmd([
        "-m", "chonoi.headless", "--mode", "gather", "--seed", "1", "--ticks", "100",
        "--scenario", faint_sc, "--out", faint_jsonl,
    ])
    os.remove(faint_sc)

    with open(kho_json, encoding="utf-8") as f:
        inv = json.load(f)
    print(f"OK: Đã sinh bằng chứng phase-{a.phase} tại {out_dir}")
    print(f"Kho xuất ra (gather-kho.json): {json.dumps(inv, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
