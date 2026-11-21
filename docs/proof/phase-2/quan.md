# Phase 2 — Kiểm chứng phần Quán

Các ca dưới đây chạy trực tiếp `QuanSim` từ manifest v1.1 và đối chiếu vị trí bếp, bàn, món mới và kế hoạch D1–D5 với [fixture kỳ vọng](../../../tests/fixtures/quan_phase2.json).

| Ca kiểm tra | Kết quả |
|---|---|
| Hai bếp và bốn bàn | B1 nhận đơn cũ hơn dù id khách lớn hơn. B2 nhận đơn còn lại khi B1 đang nấu. Kho trừ đủ bốn cá kèo cho hai đơn. |
| Thực đơn và kế hoạch | Quán độc lập xét cả sáu món. Quán có kế hoạch chỉ xét các món trong ngày. Tổng nguyên liệu D1–D5 khớp công thức nhân số suất. |
| Số suất và số dư xuyên ngày | Khách vẫn gọi lại món sau khi quán đã bán đủ số suất dự kiến. Với số dư đầu ca 200 và tổng thu đầu ca 250, một khoản thanh toán 72 cho `money=272`, `earned=322` và `shift_earned=72`. |

```powershell
python -m unittest discover -s tests -p test_quan_phase2.py -v
```

Chạy kiểm chứng cả vòng ngày qua CLI bằng `python tools/check_day.py`. [Ma trận Phase 2](../../verification/phase-2.md)
