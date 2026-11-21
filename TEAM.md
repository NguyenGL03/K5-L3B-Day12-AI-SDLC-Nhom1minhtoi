# TEAM

**Tên nhóm:** Nhom1minhtoi  **Số người:** 2  (khớp `team_size` trong `game.contract.json`; đã ghi nhận quy mô 2 người trong `docs/clarify.md`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Chu Quang Linh (Leader · 2A202603809) | `ArsNeonci` | `sim/gather`, `qa/gather` | PO, Lead Gather | `sim/quan` |
| Khương Hoàng Nguyên (2A202603987) | `NguyenGL03` | `sim/quan`, `client/ui` | Integrator, Scrum/Release, Lead Quan | `sim/gather` |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: Nhắn tin trực tiếp / call khi cần chốt hợp đồng hoặc đổi yêu cầu.
- Khi bất đồng về thiết kế: Trao đổi tối đa 2 phút; chưa chốt được thì Integrator quyết và ghi lại lý do vào `docs/adr/` hoặc `docs/clarify.md`.
- Khi ai đó trễ hoặc vướng quá 10 phút: Báo ngay để người còn lại hỗ trợ hoặc nhận phần việc ưu tiên cao hơn.
- Giờ standup giữa phase: Giữa mỗi phase (2–3 phút), cập nhật 1 dòng/người vào `docs/standup.md`.
- Cách đọc code của nhau: Đọc chéo commit/PR của nhau trước khi gắn tag mỗi phase (A đọc `quan`, B đọc `gather`).
- Cách làm việc với Git: Làm theo lát nhỏ, chạy test xanh trước khi push lên `main` (hoặc nhánh ngắn rồi merge); `NguyenGL03` (Integrator) kiểm tra tích hợp, gắn tag `phase-1..4` và tạo Release `v1.0.0`.
