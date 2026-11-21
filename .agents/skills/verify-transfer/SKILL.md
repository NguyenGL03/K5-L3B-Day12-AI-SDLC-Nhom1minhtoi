---
name: verify-transfer
description: Kiểm chứng luồng bàn giao file kho End-to-End từ chế độ gather sang chế độ quan, đối chiếu stock đầu ca và xác minh tính tất định byte-for-byte của quan.
---

# Skill: Verify Inventory Transfer & End-to-End Flow (`verify-transfer`)

Dùng skill này khi cần kiểm tra tích hợp giữa hai chế độ `gather` (`chonoi/sim/gather.py`) và `quan` (`chonoi/sim/quan.py`):
1. Đảm bảo file kho `docs/proof/phase-1/gather-kho.json` được sinh từ lượt chạy `gather` thật (hái `bong_dien_dien` + bắt `ca_linh`).
2. Chạy headless chế độ `quan` nạp `--inventory docs/proof/phase-1/gather-kho.json` cùng kịch bản điều khiển đầu bếp nấu món `lau_ca_linh_dien_dien`, bưng món và phục vụ khách `C1` tại bàn `T1` cho tới khi khách thanh toán (`paid`).
3. Kiểm tra:
   - `snapshot[0].stock` của `quan` khớp chính xác với `items` trong `gather-kho.json`.
   - Chuỗi sự kiện đầy đủ: `customer_arrived` → `cook_started` → `dish_ready` → `dish_picked` → `served` → `paid`.
   - Hai lần chạy cùng `--seed` cho kết quả JSONL giống từng byte.
4. Lưu log `docs/proof/phase-1/quan-from-gather.jsonl` và báo cáo `docs/proof/phase-4/transfer-summary.md`.

## Lệnh chạy

```bash
python3 .agents/skills/verify-transfer/scripts/run_verify_transfer.py
```
