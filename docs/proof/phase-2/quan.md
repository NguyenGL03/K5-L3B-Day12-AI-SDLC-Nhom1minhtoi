# Phase 2 — Kiểm chứng phần Quán

Các ca dưới đây chạy trực tiếp `QuanSim` với dữ liệu chuẩn của TICKET-02. [Fixture](../../../tests/fixtures/quan_phase2.json) chứa các vị trí bếp và bàn, ba món bổ sung, cùng kế hoạch D1–D5 để đối chiếu khi cập nhật manifest chung.

| Ca kiểm tra | Kết quả |
|---|---|
| Hai bếp và bốn bàn | B1 nhận đơn cũ hơn dù id khách lớn hơn. B2 nhận đơn còn lại khi B1 đang nấu. Kho trừ đủ bốn cá kèo cho hai đơn. |
| Thực đơn và kế hoạch | Quán độc lập xét cả sáu món. Quán có kế hoạch chỉ xét các món trong ngày. Tổng nguyên liệu D1–D5 khớp công thức nhân số suất. |
| Số suất và số dư xuyên ngày | Khách vẫn gọi lại món sau khi quán đã bán đủ số suất dự kiến. Với số dư đầu ca 200 và tổng thu đầu ca 250, một khoản thanh toán 72 cho `money=272`, `earned=322` và `shift_earned=72`. |

```powershell
python -m unittest discover -s tests -p test_quan_phase2.py -v
```

Khi tích hợp `day`, truyền kế hoạch hiện tại qua `day_plan`, tiền và tổng thu qua `money` và `earned`. Dùng `scenario.reputation` nội bộ cho uy tín chuyển từ ngày trước, sau khi đã kiểm tra fixture `day` của người chơi. Truyền phần mang về qua `inventory`. Luồng `day`, manifest v1.1 và kiểm chứng CLI với dữ liệu tích hợp cần phối hợp với phần dùng chung.
