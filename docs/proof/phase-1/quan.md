# Kiểm chứng Phase 1 — Quán

Các ca dưới đây đối chiếu Quán với Test Contract v1.0 mục D–G trong PRD-0.

| Ca kiểm tra | Kết quả thực tế |
|---|---|
| CLI nạp kho mẫu qua `--inventory` | Snapshot tick 0 có `bong_sung: 2`, `ca_loc: 1`. Với seed 1, khách `C1` ở bàn `T1` gọi `ca_loc_nuong_trui` tại tick 120. |
| Nấu, lấy món, phục vụ, thanh toán | Chuỗi của `C1` đi từ `customer_arrived` qua `cook_started`, `dish_ready`, `dish_picked`, `served` đến `paid`. Bộ test đối chiếu tick và toàn bộ payload sự kiện. Bếp chín và người chơi lấy món trong cùng tick. Quán thu 72 gồm giá 60 và boa 12. Uy tín tăng từ 3,0 lên 3,2. |
| Khách hết kiên nhẫn | Khách chờ rời bàn thì nguyên liệu được bỏ giữ chỗ. Nếu khách rời khi bếp đã bắt đầu nấu, bếp trở về `idle` và nguyên liệu vẫn được tính là đã dùng. |
| Phục vụ sát hạn, đóng ca | Phục vụ được khi kiên nhẫn về 0 ở tick cuối. Cùng tick, khách trả tiền với `reason: closing`, rồi quán phát `quan_end`. Khách đang chờ rời với `reason: closing` và giữ nguyên uy tín. Lịch khách bỏ qua tick đóng ca. |
| Thiếu món hoặc fixture mâu thuẫn | Kho trống phát `no_dish` với payload `{}` và bàn vẫn trống. Đơn `assigned` thiếu món và khách `eating` thiếu `tip` thoát mã 2 trước khi ghi đầu ra. |
| Bàn giao kho theo mục G | Hai tiến trình chạy với seed 42 và fixture cập bến của PRD. `catch.json`, `gather_end.data.inventory` và `stock` trong snapshot Quán tick 0 cùng có hai bông súng và một cá lóc. |
| Tính tất định và hồi quy | Hai lượt `quan` cùng seed, kho và input cho JSONL giống từng byte. Toàn bộ 40 test pass trên Windows khi lệnh headless trong bộ smoke dùng interpreter Python đã cài. |

Chạy ca kiểm thử Quán và mở demo từ thư mục gốc. Lệnh kiểm thử tương thích PowerShell với Python đã cài.

```powershell
python -m unittest discover -s tests -p test_quan_phase1.py -v
python -m chonoi.headless --mode quan --seed 1 --ticks 120 --inventory docs/contracts/inventory.sample.json --out quan.jsonl
python -m chonoi.live --mode quan --seed 1 --inventory docs/contracts/inventory.sample.json
```

Trong demo, đi tới bếp `B1` và bấm **E** khi khách đã gọi món. Đợi bếp chuyển sang trạng thái chín, bấm **E** lấy món, rồi tới bàn `T1` bấm **E** phục vụ. Sau khi khách ăn xong, xem tiền và uy tín trên HUD.

## Phần cần phối hợp khi tích hợp

- HUD ở `chonoi/web/index.html` cần đọc `stove.dish.dish_id` từ payload món mới và hiển thị kho khả dụng bằng `stock` trừ tổng `customers[].reserved`.
- Chạy lại ca bàn giao với lượt Gather thu thập thật, rồi đưa bằng chứng vào ma trận kiểm chứng chung của Phase 1.
