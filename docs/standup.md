# Standup giữa phase (mỗi người một dòng, 2–3 phút)

| Phase | Người | Đã xong | Sắp làm | Vướng gì |
|---|---|---|---|---|
| Phase 1 | `ArsNeonci` | Hoàn thành Lát 1 (oxy, ngạt, ngất, giỏ LIFO) & Lát 2 (hái nút, mọc lại, bắt cá, hồi chiêu) trong `chonoi/sim/gather.py`, viết `tests/test_gather.py`, tạo skill `gather-proof` và xuất `gather-kho.json` | Bàn giao `gather-kho.json` cho `NguyenGL03` chạy nối với `quan` và review chéo `chonoi/sim/quan.py` | Không |
| Phase 1 | `NguyenGL03` | Lập bảng phân công `docs/plan/phan-cong-lab12.md`, hoàn thiện `chonoi/sim/quan.py` Phase 1, viết `tests/test_quan_phase1.py` và `docs/proof/phase-1/quan.md` | Mở rộng `QuanSim` cho Phase 2 (2 bếp, 4 bàn, thực đơn 6 món và `day_plan`) | HUD `index.html` cần đọc `stove.dish.dish_id` |
| Phase 2 | `NguyenGL03` | Hoàn thành `QuanSim` Phase 2 (`day_plan`, kết chuyển `money`/`earned`), viết `tests/test_quan_phase2.py` và `docs/proof/phase-2/quan.md` | Cài đặt `QuanStock` cho Phase 3 (độ tươi cá thể và sự kiện `spoiled`) | Không |
| Phase 2 | `ArsNeonci` | Kiểm chứng hồi quy `gather` với bộ test mới, cập nhật `docs/verification/phase-2.md` và retro nhanh Phase 2 | Viết ADR-0001 và skill `verify-transfer` kiểm tra chuyển kho tự động | Không |
| Phase 3 | `NguyenGL03` | Hoàn thành `chonoi/sim/quan_stock.py`, `tests/test_quan_stock_phase3.py` và `docs/proof/phase-3/quan.md` | Phối hợp merge nhánh `develop` và `ars`, kiểm tra toàn bộ test suite | Không |
| Phase 3–4 | `ArsNeonci` | Merge `develop` và `ars` (0 conflict, 52/52 tests PASS), viết skill `verify-transfer`, nâng cấp `chonoi/web/index.html`, hoàn tất `docs/verification/phase-1..4.md` và `docs/retro.md` | Đóng gói nhánh `main`, gắn tag `phase-1..4` & `v1.0.0` | Không |


