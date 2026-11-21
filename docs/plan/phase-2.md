# Kế hoạch Phase 2 (≤ 1 trang)

- **Mục tiêu:** Mở rộng hệ thống Quán hỗ trợ nhiều bếp (`B1`, `B2`), nhiều bàn (`T1`–`T4`), thực đơn 6 món, lọc món theo kế hoạch ngày (`day_plan` `D1`–`D5`) và kết chuyển số dư (`money`, `earned`, `reputation`) xuyên ngày mà không phá vỡ test hồi quy Phase 1.
- **Việc / người / phụ thuộc:**
  - **Khương Hoàng Nguyên (`NguyenGL03`):** Cập nhật `QuanSim` trong `chonoi/sim/quan.py` để nhận `day_plan`, `money`, `earned`; xử lý ưu tiên đơn cũ nhất `(order_tick, id_key(table_id))` khi nhiều bếp rảnh; tạo `tests/fixtures/quan_phase2.json`, `tests/test_quan_phase2.py` và `docs/proof/phase-2/quan.md`.
  - **Chu Quang Linh (`ArsNeonci`):** Xây dựng skill `.agents/skills/gather-proof/`, kiểm chứng tính tất định của `gather` và đảm bảo luồng xuất kho tương thích với thực đơn mở rộng; cập nhật `docs/verification/phase-2.md` và `docs/retro.md` (mục Phase 2).
- **Rủi ro:**
  - Thay đổi chữ ký `QuanSim.__init__` có thể làm hỏng `runner.build_sim`: giải quyết bằng tham số keyword-only có giá trị mặc định (`*, day_plan=None, money=0, earned=0`).
