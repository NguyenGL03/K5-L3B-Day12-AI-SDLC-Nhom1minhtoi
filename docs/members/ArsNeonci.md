# ArsNeonci — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Thiết lập cấu hình nhóm (`TEAM.md`, `game.contract.json`), `docs/clarify.md` và kế hoạch Phase 1 ([`fe3052a`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/fe3052a)).
  - Cài đặt Lát 1 (`dive`/`surface`, oxy, ngạt, `choke`, `faint`, giỏ LIFO — [`0d26d73`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/0d26d73)) và Lát 2 (hái nút, mọc lại, bắt cá, hồi chiêu — [`4c0f6b7`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/4c0f6b7)) trong `chonoi/sim/gather.py` cùng `tests/test_gather.py`.
  - Xây dựng 2 skills Harness AI (`gather-proof`, `verify-transfer` — [`f095664`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/f095664)), merge tích hợp nhánh `develop` ([`2ca7983`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/2ca7983)), nâng cấp HUD `chonoi/web/index.html` và hoàn thiện hồ sơ kiểm chứng/retro.
- **Tôi đã review (kèm link):**
  - Đọc chéo các commit `quan` của `NguyenGL03`: [`7936b69`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/7936b69), [`b8ec20b`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/b8ec20b), [`3691aeb`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/commit/3691aeb) và đồng bộ hiển thị `stove.dish.dish_id` trên UI.
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - Script `run_gather_proof.py` do AI sinh thiếu một bậc `os.path.dirname` ở biến `ROOT` gây lỗi `ModuleNotFoundError: No module named 'chonoi'`; tôi phát hiện ngay khi chạy lệnh kiểm chứng thực tế và sửa lại.
- **Điều tôi học được:**
  - Cô lập phạm vi file theo module và tự động hóa kiểm chứng bằng skill giúp nhóm 2 người ghép code với 0% xung đột Git.
