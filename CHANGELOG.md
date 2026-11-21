# Changelog

## [v1.0.0] — Phase 4 (2026-11-21)
### Added
- Skill thứ 2 `.agents/skills/verify-transfer/` tự động kiểm chứng luồng bàn giao kho End-to-End (`gather` → `gather-kho.json` → `quan`) và sinh bằng chứng `docs/proof/phase-4/transfer-summary.md`.
- Nâng cấp giao diện trình duyệt `chonoi/web/index.html` (mục *Tự do sáng tạo*, tắt hoàn toàn ở headless):
  - Hiển thị tên món tiếng Việt và `stove.dish.dish_id`, trạng thái đơn của từng khách, lượng kho khả dụng tách riêng với nguyên liệu đang giữ chỗ (`reserved`).
  - Hiệu ứng gợn sóng mặt nước, bọt khí theo nhịp bơi khi lặn, viền cảnh báo đỏ khi oxy thấp / ngạt, và ánh đèn lồng ấm ở cảnh Quán buổi tối.
- Hoàn thiện toàn bộ tài liệu `docs/contracts/README.md`, `docs/verification/phase-1..4.md`, `docs/plan/phase-1..4.md`, `docs/adr/0001-file-isolation-and-inventory-handover.md`, `docs/retro.md`, `docs/members/ArsNeonci.md`, `docs/members/NguyenGL03.md`, `CREDITS.md`.

## [v0.3.0] — Phase 3 (2026-11-21)
### Added
- Lớp `QuanStock` (`chonoi/sim/quan_stock.py`) quản lý kho theo từng cá thể nguyên liệu có độ tươi (`fresh ∈ [0, 100]`), tính hao tươi chính xác bằng `fractions.Fraction`, phát sự kiện `spoiled` theo thứ tự `id` và giữ chỗ ưu tiên cá thể tươi nhất (`tests/test_quan_stock_phase3.py`).

## [v0.2.0] — Phase 2 (2026-11-21)
### Added
- Mở rộng `QuanSim` (`chonoi/sim/quan.py`) hỗ trợ nhiều bếp (`B1`, `B2`), 4 bàn (`T1`–`T4`), thực đơn 6 món, lọc món theo kế hoạch ngày `day_plan` (`D1`–`D5`) và kết chuyển số dư `money`, `earned`, `reputation` (`tests/test_quan_phase2.py`).

## [v0.1.0] — Phase 1 (2026-11-21)
### Added
- Hoàn thiện mô phỏng buổi sáng `GatherSim` (`chonoi/sim/gather.py`): lặn/nổi (`dive`/`surface`), oxy, ngạt (`zero_oxy_ticks`), trừ Máu (`choke`), ngất (`faint` + xóa giỏ LIFO), hái nút & mọc lại (`node_regrown`), bắt cá dưới nước & hồi chiêu (`catch_cd_ticks`), cập bến xuất kho (`tests/test_gather.py`).
- Hoàn thiện mô phỏng buổi tối `QuanSim` (`chonoi/sim/quan.py`): khách đến theo lịch, giữ chỗ nguyên liệu, nấu bếp, bưng món, phục vụ, tính tiền/boa/uy tín, kiểm lỗi fixture mức luật thoát mã 2 (`tests/test_quan_phase1.py`).
- Skill `.agents/skills/gather-proof/` tự động kiểm chứng tính tất định byte-for-byte và sinh bộ bằng chứng `docs/proof/phase-1/`.

