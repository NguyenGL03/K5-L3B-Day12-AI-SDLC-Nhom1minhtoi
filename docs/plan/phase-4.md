# Kế hoạch Phase 4 (≤ 1 trang)

- **Mục tiêu:** Hoàn thiện tích hợp End-to-End `gather` → `kho.json` → `quan`, bổ sung Skill AI thứ 2 (`verify-transfer`), nâng cấp giao diện trình duyệt `chonoi/web/index.html` (kèm mục sáng tạo tắt ở headless), hoàn tất toàn bộ hồ sơ kiểm chứng/retro và phát hành `v1.0.0`.
- **Việc / người / phụ thuộc:**
  - **Chu Quang Linh (`ArsNeonci`):** Viết skill `.agents/skills/verify-transfer/` kiểm chứng luồng bàn giao kho & tính tất định của cả hai chế độ; hoàn thiện `docs/retro.md`, `docs/members/ArsNeonci.md`, `CHANGELOG.md`, `CREDITS.md`.
  - **Khương Hoàng Nguyên (`NguyenGL03`):** Nâng cấp HUD & hiệu ứng trực quan trong `chonoi/web/index.html` (hiển thị đúng `stove.dish.dish_id`, kho khả dụng sau khi trừ `reserved`, hiệu ứng mặt nước/bọt khí), hoàn thiện `docs/members/NguyenGL03.md`, merge nhánh chính và gắn tag `phase-1`..`phase-4` + `v1.0.0`.
- **Rủi ro:**
  - Phần sáng tạo UI làm ảnh hưởng tới kết quả chấm headless: cô lập 100% phần mở rộng hiển thị trong `chonoi/web/index.html`, giữ nguyên lõi `chonoi/sim/` và `chonoi/headless.py`.
