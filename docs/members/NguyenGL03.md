# NguyenGL03 — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Lập kế hoạch phân công nhóm 2 người tại `docs/plan/phan-cong-lab12.md` ([`40c42aa`](https://github.com/NguyenGL03/K5-L3B-Day12-AI-SDLC-Nhom1minhtoi/commit/40c42aa)).
  - Cài đặt toàn bộ luật chơi buổi tối `chonoi/sim/quan.py` cho Phase 1 (khách đến, giữ chỗ, nấu bếp, bưng phục vụ, thanh toán, boa, uy tín — [`7936b69`](https://github.com/NguyenGL03/K5-L3B-Day12-AI-SDLC-Nhom1minhtoi/commit/7936b69)) kèm `tests/test_quan_phase1.py` và `docs/proof/phase-1/quan.md`.
  - Mở rộng `QuanSim` cho Phase 2 hỗ trợ 2 bếp, 4 bàn, 6 món, kế hoạch ngày `day_plan` và kết chuyển số dư ([`b8ec20b`](https://github.com/NguyenGL03/K5-L3B-Day12-AI-SDLC-Nhom1minhtoi/commit/b8ec20b)).
  - Thiết kế lớp `QuanStock` (`chonoi/sim/quan_stock.py`) cho Phase 3 quản lý độ tươi cá thể và sự kiện `spoiled` ([`3691aeb`](https://github.com/NguyenGL03/K5-L3B-Day12-AI-SDLC-Nhom1minhtoi/commit/3691aeb)).
- **Tôi đã review (kèm link):**
  - Đọc chéo phần `chonoi/sim/gather.py` và file kho bàn giao `gather-kho.json` từ `ArsNeonci` ([`0d26d73`](https://github.com/NguyenGL03/K5-L3B-Day12-AI-SDLC-Nhom1minhtoi/commit/0d26d73), [`4c0f6b7`](https://github.com/NguyenGL03/K5-L3B-Day12-AI-SDLC-Nhom1minhtoi/commit/4c0f6b7)).
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - Phép trừ độ tươi mỗi tick (`0.25 / 60`) nếu dùng `float` dễ gây sai số ở biên ngưỡng ươn `30`; tôi phát hiện khi viết test biên `30.0125` và chuyển sang `fractions.Fraction`.
- **Điều tôi học được:**
  - Dùng kiểu số chính xác (`Decimal`, `Fraction`) và tách lớp `QuanStock` giúp vừa đáp ứng yêu cầu mở rộng vừa giữ toàn bộ test hồi quy luôn xanh.
