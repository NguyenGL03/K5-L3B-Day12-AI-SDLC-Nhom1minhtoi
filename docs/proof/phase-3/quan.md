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

Reader/writer đã được kiểm qua file và trong vòng ngày. HUD đếm hàng ươn và kho khả dụng từ snapshot cá thể. Test Quán xác nhận hàng ươn được thay trước khi nấu, giá chốt theo độ tươi lúc dùng và đơn thiếu phần bù nhả toàn bộ phần giữ. [Ma trận Phase 3](../../verification/phase-3.md)
