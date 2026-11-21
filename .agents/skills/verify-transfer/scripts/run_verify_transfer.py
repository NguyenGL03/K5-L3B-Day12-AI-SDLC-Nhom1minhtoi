"""Script tự động kiểm chứng luồng bàn giao kho gather -> gather-kho.json -> quan (End-to-End)."""

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
    p1_dir = os.path.join(ROOT, "docs", "proof", "phase-1")
    p4_dir = os.path.join(ROOT, "docs", "proof", "phase-4")
    os.makedirs(p1_dir, exist_ok=True)
    os.makedirs(p4_dir, exist_ok=True)

    # 1. Đảm bảo đã có gather-kho.json từ skill gather-proof
    gather_script = os.path.join(ROOT, ".agents", "skills", "gather-proof", "scripts", "run_gather_proof.py")
    run_cmd([gather_script, "--phase", "1"])

    kho_path = os.path.join(p1_dir, "gather-kho.json")
    with open(kho_path, encoding="utf-8") as f:
        kho_data = json.load(f)

    # 2. Tạo kịch bản phím bấm cho Quán:
    # Khách C1 đến ở tick 120 gọi lau_ca_linh_dien_dien (vì kho có ca_linh: 3, bong_dien_dien: 1).
    # Người chơi từ (8,5) đi tới bếp B1 (2,8), bấm interact ở tick 200 để nấu (cook_s=10s -> 600 ticks -> chín ở tick 800),
    # bấm interact ở tick 805 để bưng món, đi tới bàn T1 (9,2) bấm interact ở tick 950 để phục vụ,
    # khách ăn 10s (600 ticks) -> trả tiền (paid) ở tick 1550.
    quan_inputs_path = os.path.join(p1_dir, "quan-inputs.json")
    quan_frames = {
        "frames": [
            {"tick": 0, "move": [-1, 0.5]},
            {"tick": 110, "move": [0, 0]},
            {"tick": 125, "interact": True},
            {"tick": 126, "interact": False},
            {"tick": 730, "interact": True},
            {"tick": 731, "interact": False, "move": [1, -0.86]},
            {"tick": 865, "move": [0, 0], "interact": True},
            {"tick": 866, "interact": False},
        ]
    }
    with open(quan_inputs_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(quan_frames, f, ensure_ascii=False, indent=2)
        f.write("\n")

    quan_jsonl = os.path.join(p1_dir, "quan-from-gather.jsonl")
    quan_jsonl_2 = os.path.join(p1_dir, "quan-from-gather-verify.jsonl")

    run_cmd([
        "-m", "chonoi.headless", "--mode", "quan", "--seed", "1", "--ticks", "1500",
        "--inventory", kho_path, "--inputs", quan_inputs_path, "--out", quan_jsonl,
    ])
    run_cmd([
        "-m", "chonoi.headless", "--mode", "quan", "--seed", "1", "--ticks", "1500",
        "--inventory", kho_path, "--inputs", quan_inputs_path, "--out", quan_jsonl_2,
    ])

    with open(quan_jsonl, "rb") as f1, open(quan_jsonl_2, "rb") as f2:
        if f1.read() != f2.read():
            sys.stderr.write("LỖI: Kết quả headless của quan không tất định (byte mismatch)!\n")
            sys.exit(1)
    os.remove(quan_jsonl_2)

    with open(quan_jsonl, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    snap0 = rows[0]
    if snap0.get("stock") != kho_data.get("items"):
        sys.stderr.write(f"LỖI: stock đầu ca ({snap0.get('stock')}) khác gather-kho.json ({kho_data.get('items')})\n")
        sys.exit(1)

    ev_rows = [r for r in rows if r["type"] == "event"]
    ev_names = [r["name"] for r in ev_rows]
    required = ["customer_arrived", "cook_started", "dish_ready", "dish_picked", "served", "paid"]
    for req in required:
        if req not in ev_names:
            sys.stderr.write(f"LỖI: Thiếu sự kiện {req} trong luồng tích hợp gather -> quan (đã có: {ev_names})\n")
            sys.exit(1)

    end_row = rows[-1]
    summary_path = os.path.join(p4_dir, "transfer-summary.md")
    lines = [
        "# Bằng chứng tích hợp End-to-End: `gather` → `gather-kho.json` → `quan`",
        "",
        f"- **Kho xuất từ `gather` (`docs/proof/phase-1/gather-kho.json`):** `{json.dumps(kho_data['items'], ensure_ascii=False)}`",
        f"- **`stock` tại snapshot tick 0 của `quan`:** `{json.dumps(snap0['stock'], ensure_ascii=False)}` (khớp 100%)",
        "- **Tính tất định byte-for-byte:** Đạt (chạy 2 lần cùng `--seed 1` khớp từng byte).",
        "",
        "## Chuỗi sự kiện ghi nhận trong `docs/proof/phase-1/quan-from-gather.jsonl`",
        "",
        "| Tick | Sự kiện | Payload `data` |",
        "|---|---|---|",
    ]
    for r in ev_rows:
        lines.append(f"| `{r['tick']}` | `{r['name']}` | `{json.dumps(r['data'], ensure_ascii=False)}` |")
    lines.extend([
        "",
        f"## Kết quả cuối lượt (`end` row tại tick `{end_row['ticks']}`)",
        f"- `money`: `{end_row['money']}` · `earned`: `{end_row['earned']}` · `reputation`: `{end_row['reputation']}` · `score`: `{end_row['score']}`",
        "",
    ])
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    print("OK: Kiểm chứng chuyển kho gather -> quan thành công!")
    print(f"Sự kiện: {ev_names}")
    print(f"Kết quả cuối: money={end_row['money']}, reputation={end_row['reputation']}, score={end_row['score']}")


if __name__ == "__main__":
    main()
