# Kiểm chứng Phase 2 — Test Contract v1.1

| Yêu cầu trong TICKET-02 | Cách kiểm chứng | Kết quả |
|---|---|---|
| Cá bơi, phản xạ và sinh theo lịch. Cá Sấu chạm và làm rơi hàng. | Ca phản xạ và sinh tại tick 360, ca hit gây ngất với giỏ mất theo LIFO trong [`test_day_phase2.py`](../../tests/test_day_phase2.py). | Đạt các ca đã chạy. |
| 2 bếp, 4 bàn, 6 món và kế hoạch D1–D5. | So manifest với fixture kỳ vọng và chạy bếp song song. [Bằng chứng Quán](../proof/phase-2/quan.md) | Đạt các ca đã chạy. |
| Luồng ngày, pause, Shop và nâng cấp áp dụng ngày sau. | [`check_day.py`](../../tools/check_day.py), ca hai ngày mua oxy đúng giá và kiểm JSONL trong [`test_day_phase2.py`](../../tests/test_day_phase2.py), và CLI chạy đủ 5 ngày với seed 42. | Đạt các ca đã chạy. |
| Bàn giao kho đếm từ Gather sang Quán. | Smoke chạy hai tiến trình qua cờ `--inventory-out` và `--inventory`. Ca bổ sung chuyển cá kèo và kèo nèo ở snapshot tick 0. [`test_smoke_p1.py`](../../tests/test_smoke_p1.py) | Đạt. |
| Giao diện ngày và giới hạn thời gian. | HTTP `/state` và `/input` đi qua menu, các màn giới thiệu, kết quả, Shop và tổng kết. Chạy headless một Ngày đủ 22.200 tick mất 0,74 giây tại máy hiện tại. | Luồng HTTP và headless đạt. FPS trên trình duyệt và máy chấm chưa đo. |

Smoke P1 dùng số đàn từ manifest và kiểm `shop` bị từ chối với tư cách CLI mode, vì `day` đã hợp lệ. Ca giỏ đầy dựng đàn cá cố định để kiểm cooldown. Ca ngạt cập nhật theo quy tắc tính cả bước oxy vừa chạm 0.
