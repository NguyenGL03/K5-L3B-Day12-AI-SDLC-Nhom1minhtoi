# Phase 3 — Kiểm chứng kho cá thể của Quán

Các ca dưới đây chạy trên `QuanStock`, phần xử lý kho cá thể ở phía Quán.

| Ca kiểm tra | Kết quả |
|---|---|
| Nhập kho | Giữ id, loại và độ tươi, kể cả hàng đã ươn. Từ chối kho đếm, id trùng hoặc rỗng, loại lạ và độ tươi ngoài miền. |
| Hao tươi | Độ tươi đúng 30 vẫn dùng được. Từ 30,0125 về đúng 30 sau ba tick và phát `spoiled` ở tick thứ tư. Nhiều cá thể vừa ươn cùng tick phát theo thứ tự id. Hàng ươn vẫn nằm trong kho. |
| Giữ nguyên liệu | Chọn cá thể tươi nhất theo từng loại, hòa theo id. Bỏ qua hàng ươn và cá thể đã giữ cho đơn khác. Fixture giữ trùng, sai công thức hoặc tham chiếu thiếu bị từ chối. |
| Chuyển file từ Gather | Cập bến với hai cá thể gần và xa ngưỡng ươn. JSONL và file giữ đủ độ tươi để bộ kho Quán phân nhánh chính xác. |

```powershell
python -m unittest discover -s tests -p test_quan_stock_phase3.py -v
```

Reader/writer v1.2 đã dùng chung với Gather và được kiểm qua file. HUD có thể đếm hàng ươn và kho khả dụng khi nhận snapshot cá thể. Bản ticket đã nhận thiếu công thức chốt giá theo độ tươi và chi tiết thay phần giữ vừa ươn cho đơn thường. Sau khi có hai quy tắc đó, nối `QuanStock` vào tick Quán sau khi giảm timer và trước khi xét bếp, rồi kiểm chứng giữ chỗ, thanh toán, HUD và bàn giao qua cả file lẫn `day` trước khi bật v1.2. [Ma trận Phase 3](../../verification/phase-3.md)
