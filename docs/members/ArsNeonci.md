# ArsNeonci — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Thiết lập cấu hình nhóm 2 thành viên (`TEAM.md`, `game.contract.json`), ghi nhật ký làm rõ yêu cầu (`docs/clarify.md`) và kế hoạch Phase 1 (`docs/plan/phase-1.md`).
  - Cài đặt Lát 1 (`dive`/`surface`, oxy, ngạt `zero_oxy_ticks`, `choke`, `faint`, giỏ LIFO) và Lát 2 (hái nút, mọc lại `node_regrown`, bắt cá dưới nước, hồi chiêu `catch_cd_ticks`, xuất kho) trong `chonoi/sim/gather.py`.
  - Viết bộ unit/black-box test riêng trong `tests/test_gather.py` và xây dựng skill `.agents/skills/gather-proof/` để sinh bằng chứng `docs/proof/phase-1/`.
- **Tôi đã review (kèm link):**
  - Rà soát hợp đồng tích hợp file kho (`inventory.sample.json` / `gather-kho.json`) và đọc chéo luồng `chonoi/sim/quan.py` cùng `NguyenGL03`.
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - Khi chạy lệnh gộp trên Windows PowerShell 5.1, AI dùng `&&` khiến lệnh lỗi cú pháp; phát hiện qua mã thoát và đổi sang kiểm tra `$LASTEXITCODE`. Ngoài ra, rà kỹ mốc giảm oxy từ `1 -> 0` để không đếm chồng tick ngạt đầu tiên vào tick vừa cạn oxy.
- **Điều tôi học được:**
  - Chia ranh giới file theo module (`gather.py` + `test_gather.py` tách khỏi `quan.py` + `test_quan.py`) giúp làm việc nhóm với AI tốc độ cao mà không xảy ra xung đột Git.
