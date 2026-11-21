# Ma trận truy vết Phase 2

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-2/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| **AC-P2-Q1: Mở rộng 2 bếp (`B1`, `B2`) và 4 bàn (`T1`–`T4`), ưu tiên đơn cũ nhất** | Unit test `test_two_stoves_take_oldest_orders_and_reserve_across_tables` trong `tests/test_quan_phase2.py` | [`docs/proof/phase-2/quan.md`](../proof/phase-2/quan.md) · [`tests/fixtures/quan_phase2.json`](../../tests/fixtures/quan_phase2.json) | **Đạt** (`B1` nhận đơn `order_tick` nhỏ hơn dù `id` khách lớn hơn; `B2` nhận đơn tiếp theo; giữ chỗ nguyên liệu chính xác trên cả 4 bàn) |
| **AC-P2-Q2: Thực đơn mở rộng (6 món) và kế hoạch ngày `day_plan` (`D1`–`D5`)** | Unit test `test_day_plans_match_recipes_and_allowed_menu` trong `tests/test_quan_phase2.py` | [`docs/proof/phase-2/quan.md`](../proof/phase-2/quan.md) · [`tests/test_quan_phase2.py`](../../tests/test_quan_phase2.py) | **Đạt** (khi truyền `day_plan`, quán chỉ lọc các món thuộc kế hoạch ngày đó; tổng nguyên liệu khớp công thức × số suất) |
| **AC-P2-Q3: Không giới hạn số suất bán theo kế hoạch & chuyển số dư (`money`, `earned`, `reputation`) xuyên ngày** | Unit test `test_day_plan_quantities_do_not_limit_sales_and_opening_balance_carries` | [`docs/proof/phase-2/quan.md`](../proof/phase-2/quan.md) · [`chonoi/sim/quan.py`](../../chonoi/sim/quan.py) | **Đạt** (`money=272`, `earned=322`, `shift_earned=72`, `reputation=4.2` từ số dư đầu ca `money=200, earned=250`) |
| **AC-P2-REG: Hồi quy Phase 1 (`gather` + `quan` + bàn giao kho)** | Chạy toàn bộ bộ test `unittest discover -s tests -v` và skill `gather-proof` / `verify-transfer` | [`docs/proof/phase-1/gather-summary.md`](../proof/phase-1/gather-summary.md) | **Đạt** (100% test Phase 1 và Phase 2 cùng xanh) |

## Đánh giá ngắn
- **Yêu cầu nào đạt / chưa đạt:** Phần logic `QuanSim` cho 2 bếp, 4 bàn, 6 món ăn, lọc thực đơn theo `day_plan` và kết chuyển `money`/`earned`/`reputation` đã **Đạt**. Phần CLI `--mode day` nối tự động nhiều ngày trong một tiến trình vẫn giữ khóa ở Contract v1.0 để đảm bảo test smoke hộp đen `test_con_03_old_and_future_modes_rejected` của Phase 1 luôn xanh.
- **Điều cần chỉnh cho phase sau:** Chuẩn bị mô hình kho cá thể có độ tươi (`QuanStock`) cho Phase 3 mà không làm hỏng giao diện kho đếm hiện tại.
