# Ma trận truy vết Phase 3

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-3/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| **AC-P3-S1: Nhập kho cá thể (`id`, `kind`, `fresh`) và kiểm lỗi schema nghiêm ngặt** | Unit test `test_reject_count_schema_and_invalid_items` trong `tests/test_quan_stock_phase3.py` | [`docs/proof/phase-3/quan.md`](../proof/phase-3/quan.md) · [`chonoi/sim/quan_stock.py`](../../chonoi/sim/quan_stock.py) | **Đạt** (từ chối id trùng/rỗng, loại nguyên liệu lạ, độ tươi ngoài `[0, 100]` hoặc `NaN` bằng `BadInput`) |
| **AC-P3-S2: Hao độ tươi chính xác mỗi tick (dùng `Fraction`) và phát sự kiện `spoiled` theo thứ tự `id`** | Unit test `test_spoiled_only_when_crossing_threshold_and_in_id_order` | [`docs/proof/phase-3/quan.md`](../proof/phase-3/quan.md) · [`tests/test_quan_stock_phase3.py`](../../tests/test_quan_stock_phase3.py) | **Đạt** (độ tươi bằng đúng ngưỡng `30` vẫn dùng được; khi vượt qua ngưỡng `< 30` mới phát `spoiled` đúng một lần theo thứ tự `sort_by_id`) |
| **AC-P3-S3: Giữ chỗ nguyên liệu ưu tiên cá thể tươi nhất (`-fresh`, `id_key`)** | Unit test `test_pick_freshest_then_id_and_exclude_other_orders` | [`docs/proof/phase-3/quan.md`](../proof/phase-3/quan.md) · [`chonoi/sim/quan_stock.py`](../../chonoi/sim/quan_stock.py) | **Đạt** (chọn cá thể tươi nhất chưa được giữ chỗ và chưa ươn, hòa độ tươi chọn `id` nhỏ hơn; kiểm tra chặt `validate_reservation`) |
| **AC-P3-REG: Giữ tương thích ngược toàn bộ test Phase 1 & Phase 2** | Chạy toàn bộ `unittest discover -s tests -v` | [`tests/test_smoke_p1.py`](../../tests/test_smoke_p1.py) · [`tests/test_gather.py`](../../tests/test_gather.py) | **Đạt** (tách module `chonoi/sim/quan_stock.py` giúp toàn bộ test Phase 1, Phase 2 và Phase 3 đều PASS 100%) |

## Đánh giá ngắn
- **Yêu cầu nào đạt / chưa đạt:** Mô hình kho cá thể `QuanStock` (nhập kho, hao tươi bằng số hữu tỉ `Fraction` không sai số dấu phẩy động, phát `spoiled`, giữ chỗ ưu tiên độ tươi) đã **Đạt**. Việc nối trực tiếp `QuanStock` thay thế kho đếm trong CLI mặc định được giữ tách biệt để bảo toàn tính tương thích với hợp đồng v1.0 trong `game.contract.json`.
- **Điều cần chỉnh cho phase sau:** Hoàn thiện giao diện trực quan `chonoi/web/index.html`, bổ sung skill kiểm chứng luồng chuyển kho `verify-transfer`, hoàn tất tài liệu retro và đóng gói Release `v1.0.0`.
