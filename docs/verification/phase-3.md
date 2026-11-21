# Kiểm chứng Phase 3 — Chuyển đổi kho cá thể

| Yêu cầu trong Phase 3 | Cách kiểm chứng | Kết quả |
|---|---|---|
| Kho cá thể giữ id, loại và độ tươi qua file. | Fixture Gather cập bến, ghi file, đọc bằng schema v1.2 rồi nhập vào bộ kho Quán. So `gather_end` với file và kiểm nhánh sát 30. [`test_quan_stock_phase3.py`](../../tests/test_quan_stock_phase3.py) | Đạt ở mức adapter. |
| Giữ chỗ theo cá thể và phát `spoiled` đúng tick. | Ca nhiều id ươn cùng bước, đủ và thiếu nguyên liệu, trùng phần giữ và hòa về độ tươi. [Bằng chứng Quán](../proof/phase-3/quan.md) | Đạt ở bộ kho độc lập. |
| HUD báo hàng ươn. | Client đọc cả kho đếm và kho cá thể, nhận ngưỡng từ snapshot live và đánh dấu hàng ươn. | Đã bổ sung hiển thị. Còn chờ smoke trong lượt v1.2 tích hợp. |
| Giá theo độ tươi, giữ lại sau khi hỏng, snapshot Quán và luồng `day` v1.2. | Thiếu đoạn luật lõi về giá và giữ lại. Theo dõi tại [Clarify](../clarify.md). | Chưa hoàn thành. |

Trình tự tích hợp đã thực hiện gồm reader/writer kho cá thể, hao tươi trong Gather, rồi smoke tới bộ kho Quán. Sau khi có quy tắc giá và giữ lại, nối bộ kho vào `QuanSim`, chạy kiểm chứng HUD, CLI và `day`, rồi đổi manifest lên v1.2.
