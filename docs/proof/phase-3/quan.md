# Phase 3 — Kiểm chứng kho cá thể của Quán

Các ca dưới đây chạy trên `QuanStock`, phần xử lý kho cá thể ở phía Quán.

| Ca kiểm tra | Kết quả |
|---|---|
| Nhập kho | Giữ id, loại và độ tươi, kể cả hàng đã ươn. Từ chối kho đếm, id trùng hoặc rỗng, loại lạ và độ tươi ngoài miền. |
| Hao tươi | Độ tươi đúng 30 vẫn dùng được. Từ 30,0125 về đúng 30 sau ba tick và phát `spoiled` ở tick thứ tư. Nhiều cá thể vừa ươn cùng tick phát theo thứ tự id. Hàng ươn vẫn nằm trong kho. |
| Giữ nguyên liệu | Chọn cá thể tươi nhất theo từng loại, hòa theo id. Bỏ qua hàng ươn và cá thể đã giữ cho đơn khác. Fixture giữ trùng, sai công thức hoặc tham chiếu thiếu bị từ chối. |

```powershell
python -m unittest discover -s tests -p test_quan_stock_phase3.py -v
```

Toàn bộ 46 test hiện tại pass trên Windows khi smoke test dùng interpreter Python đã cài cho subprocess headless.

Để tích hợp v1.2, thống nhất adapter file kho và bàn giao từ Gather, rồi nối `QuanStock` vào tick Quán sau khi giảm timer và trước khi xét bếp. Bản ticket đã nhận thiếu công thức chốt giá theo độ tươi và chi tiết thay phần giữ vừa ươn cho đơn thường. Sau khi có hai quy tắc đó, cần chạy lại kiểm chứng hỏng hàng giữ chỗ, thanh toán và bàn giao thật qua cả file lẫn `day` trước khi bật v1.2. HUD dùng chung đọc danh sách cá thể và phần giữ theo id sau khi tích hợp.
