# Bằng chứng kiểm chứng Phase 1 — Chế độ `gather` (`ArsNeonci`)

## 1. Kết quả chạy bộ test (`unittest`)
- Lệnh: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Kết quả: **38/38 tests PASS** (gồm 32 test starter + 6 test mới trong `tests/test_gather.py`).

## 2. Các ca kiểm chứng Headless trong `docs/proof/phase-1/`
- `gather-inputs.json`: Kịch bản phím bấm điều khiển Út Sen bơi từ bến `(2, 0)` tới nút `N1 (12, 0)` hái `bong_dien_dien`, lặn xuống `F1 (15, 5)` bắt `ca_linh`, nổi lên mặt nước và quay về bến cập bến.
- `gather-docked.jsonl`: Log JSONL tất định của lượt chơi (đã kiểm chứng chạy 2 lần cùng `--seed 1` khớp từng byte), ghi nhận đầy đủ các sự kiện `gather`, `dive`, `fish_caught`, `surface`, `gather_end` (`reason: "docked"`).
- `gather-kho.json`: File kho xuất ra khi kết thúc lượt chơi:
  ```json
  {"items":{"bong_dien_dien":1,"ca_linh":3}}
  ```
- `gather-fainted.jsonl`: Log JSONL kiểm chứng trường hợp cạn oxy dưới nước (`oxygen_empty` → đếm `zero_oxy_ticks` đủ 60 tick → `choke` → Máu về 0 → `faint` → `gather_end` với `reason: "fainted"` và giỏ bị xóa rỗng).
