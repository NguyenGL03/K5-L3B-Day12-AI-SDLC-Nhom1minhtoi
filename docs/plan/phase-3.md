# Kế hoạch Phase 3 (≤ 1 trang)

- **Mục tiêu:** Bổ sung cơ chế quản lý kho theo từng cá thể nguyên liệu có độ tươi (`fresh ∈ [0, 100]`), hao tươi mỗi tick, phát sự kiện `spoiled` khi xuống dưới ngưỡng `spoiled_below` và giữ chỗ ưu tiên cá thể tươi nhất.
- **Việc / người / phụ thuộc:**
  - **Khương Hoàng Nguyên (`NguyenGL03`):** Thiết kế lớp `QuanStock` trong module độc lập `chonoi/sim/quan_stock.py` dùng `fractions.Fraction` để tính hao tươi chính xác tuyệt đối không sai số dấu phẩy động; viết `tests/test_quan_stock_phase3.py` và `docs/proof/phase-3/quan.md`.
  - **Chu Quang Linh (`ArsNeonci`):** Ghi ADR `docs/adr/0001-file-isolation-and-inventory-handover.md` đánh giá tác động của change request kho cá thể, rà soát hồi quy Phase 1–2 và lập `docs/verification/phase-3.md`.
- **Rủi ro:**
  - Sai số số thực (`float`) khi trừ `0.25 / 60` mỗi tick làm lệch tick phát sự kiện `spoiled`: khắc phục triệt để bằng `Fraction(str(fresh))`.
  - Xung đột với schema kho đếm v1.0 của `test_smoke_p1.py`: tách `QuanStock` thành lớp riêng để cả test v1.0 lẫn test v1.2 đều xanh.
