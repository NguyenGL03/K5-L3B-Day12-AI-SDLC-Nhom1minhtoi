# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 10:45 | Nhóm thực tế có 2 thành viên (`ArsNeonci`, `NguyenGL03`), trong khi `tools/check_team.py` kiểm tra 4–6 người. Cấu hình `TEAM.md` và `team_size` thế nào? | Điền đúng 2 thành viên thực tế vào `TEAM.md`, đặt `"team_size": 2` trong `game.contract.json` theo hướng dẫn tại `docs/plan/phan-cong-lab12.md`, và xác nhận với giảng viên. | PO (`ArsNeonci`) |
| 2 | 2026-11-21 10:50 | Thứ tự đếm `zero_oxy_ticks` khi `oxygen_ticks` vừa giảm từ 1 xuống 0 dưới nước? | Tick tiêu thụ nốt đơn vị oxy cuối cùng (`1 -> 0`) sẽ phát `oxygen_empty` và giữ `zero_oxy_ticks = 0`; từ tick kế tiếp khi đầu pha oxy đã ở mức `0` dưới nước mới tăng `zero_oxy_ticks` (`1..choke_interval_ticks`), đủ 60 tick thì phát `choke`, trừ 1 Máu và reset `zero_oxy_ticks = 0`. | PO (`ArsNeonci`) |
| 3 | 2026-11-21 10:55 | Khi bấm `interact` hái nút hoặc `catch` bắt cá mà sức chứa còn lại của giỏ không đủ `node_yield` / `fish_yield[kind]` thì xử lý thế nào? | Phát sự kiện `hold_full`, giữ nguyên nút hái (`ready`) hoặc đàn cá dưới sông để không làm mất tài nguyên của người chơi. Khi đủ chỗ thì thêm nguyên liệu vào cuối `hold` (LIFO), nút chuyển sang đếm ngược `regrow_ticks`, đàn cá đã bắt được xóa khỏi danh sách `fish`. | PO (`ArsNeonci`) |

