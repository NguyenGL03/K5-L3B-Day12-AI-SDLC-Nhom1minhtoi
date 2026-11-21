# Kiểm chứng Phase 3 — Chuyển đổi kho cá thể

| Yêu cầu trong Phase 3 | Cách kiểm chứng | Kết quả |
|---|---|---|
| Kho cá thể giữ id, loại và độ tươi qua file. | Chạy CLI Gather cập bến và ghi file, rồi chạy CLI Quán nạp file tại tick 0. Đối chiếu `gather_end`, file và snapshot, kể cả cá thể vừa ươn. [`test_current_contract.py`](../../tests/test_current_contract.py) | Đạt trên manifest v1.3. |
| Giữ chỗ theo cá thể và phát `spoiled` đúng tick. | Ca nhiều id ươn cùng bước, đủ và thiếu nguyên liệu, trùng phần giữ và hòa về độ tươi. [Bằng chứng Quán](../proof/phase-3/quan.md) | Đạt ở bộ kho độc lập. |
| HUD báo hàng ươn. | Client đọc cả kho đếm và kho cá thể, nhận ngưỡng từ snapshot live và đánh dấu hàng ươn. | Đã bổ sung hiển thị. Còn chờ smoke trong lượt v1.2 tích hợp. |
| Giá theo độ tươi, giữ lại sau khi hỏng, snapshot Quán và luồng `day`. | Nguyên liệu ươn được thay trước bước nấu. Món cá lóc lấy nguyên liệu vừa giảm dưới 90 tươi chốt giá 53. Đơn thiếu phần bù chuyển `unfulfillable` và nhả toàn bộ phần giữ. Test CLI xác nhận chuyển kho từ Gather tới Quán rồi Shop. [`test_quan_stock_phase3.py`](../../tests/test_quan_stock_phase3.py) | Đạt các ca đã chạy. |

Manifest v1.3 dùng gameplay và schema kho của Phase 3. Quy tắc giá và giữ lại do nhóm thiết kế theo trao đổi. [Clarify](../clarify.md)
