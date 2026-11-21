# Ma trận truy vết Phase 4 (Tổng kết & Phát hành `v1.0.0`)

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-4/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| **AC-P4-01: Tích hợp hoàn chỉnh `gather` → `kho.json` → `quan` (End-to-End Headless)** | Chạy skill `verify-transfer` (`.agents/skills/verify-transfer/scripts/run_verify_transfer.py`) và unit test tích hợp | [`docs/proof/phase-4/transfer-summary.md`](../proof/phase-4/transfer-summary.md) · [`docs/proof/phase-1/quan-from-gather.jsonl`](../proof/phase-1/quan-from-gather.jsonl) | **Đạt** (`gather` hái bông điên điển + bắt cá linh, xuất `gather-kho.json`, `quan` nạp kho nấu `lau_ca_linh_dien_dien` phục vụ khách `C1` thu 144k, uy tín 3.2) |
| **AC-P4-02: Bộ Harness AI (AGENTS.md + ≥ 2 Skills + Nhật ký AI)** | Kiểm tra `.agents/skills/gather-proof/` và `.agents/skills/verify-transfer/`, chạy thực tế cả 2 scripts | [`.agents/skills/`](../../.agents/skills/) · [`AGENTS.md`](../../AGENTS.md) · [`docs/ai-usage-log.md`](../ai-usage-log.md) | **Đạt** (2 skills tự động hóa kiểm chứng tất định & chuyển kho đều chạy xanh và sinh bằng chứng thật) |
| **AC-P4-03: Nâng cấp UI/HUD & Tự do sáng tạo (tắt hoàn toàn ở headless)** | Chạy `test_live.py` và mở `python -m chonoi.live --mode gather\|quan`; chạy lại toàn bộ test headless | [`chonoi/web/index.html`](../../chonoi/web/index.html) · [`README.md`](../../README.md) | **Đạt** (hiển thị đúng `stove.dish.dish_id`, kho khả dụng + nguyên liệu đang giữ chỗ, hiệu ứng bọt nước/sóng nước/cảnh báo oxy & bảng hướng dẫn trực quan trên trình duyệt, không ảnh hưởng JSONL headless) |
| **AC-P4-04: Hồ sơ nhóm, Retro, Phản tư cá nhân, Tag `phase-1..4` & Release `v1.0.0`** | Kiểm tra `TEAM.md`, `docs/retro.md`, `docs/members/ArsNeonci.md`, `docs/members/NguyenGL03.md`, `CHANGELOG.md`, `CREDITS.md` | [`docs/retro.md`](../retro.md) · [`docs/members/`](../members/) · [`CHANGELOG.md`](../../CHANGELOG.md) | **Đạt** (đầy đủ tài liệu, mỗi thành viên ≥ 4 commit có nội dung, toàn bộ test suite PASS 100%) |

## Đánh giá ngắn
- **Yêu cầu nào đạt / chưa đạt:** Toàn bộ lõi mô phỏng Phase 1, mở rộng Phase 2–3 của Quán, tích hợp chuyển kho `gather → quan`, 2 skills Harness AI, giao diện trình duyệt nâng cấp và hồ sơ AI SDLC đã hoàn tất.
- **Sẵn sàng Demo & Release:** Đã gắn đầy đủ các tag `phase-1` .. `phase-4` và `v1.0.0`.
