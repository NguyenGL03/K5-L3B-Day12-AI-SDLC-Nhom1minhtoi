# Kiểm chứng Phase 4 — bản sửa v1.0.1

| AC | Cách kiểm chứng và bằng chứng | Kết quả |
|---|---|---|
| AC-P4-01 · Benchmark cảnh lặn | Edge headless ở 1280×720, seed 42, đo 30 giây theo `requestAnimationFrame`. [bench.json](../proof/phase-4/bench.json) | 138,9 FPS trung bình, 1% low 35,4 FPS, tải 0,81 giây. Đạt cả ba mốc tại máy đo. |
| AC-P4-02 · Ba cảnh báo và tương phản cao | Dựng fixture Gather có oxy thấp và Cá Sấu gần, fixture Quán có khách gần hết kiên nhẫn. Bật nút tương phản trong Edge rồi kiểm chữ và màu hiển thị. [contrast.json](../proof/phase-4/contrast.json) | Ba cảnh báo có chữ trắng trên nền đen. |
| AC-P4-03 · Soak 10 ngày | Chạy `soak_cmd` hai lần với seed 7. So toàn bộ kết quả gameplay sau khi bỏ `duration_s`. [soak.json](../proof/phase-4/soak.json) | 10/10 ngày, 0 crash. Hai lượt có kết quả giống nhau, điểm cuối 658. |
| AC-P4-04 · Hồi quy và kho cá thể | `python -m unittest discover -s tests` kiểm hợp đồng kho đếm trên fixture phiên bản cũ và kho cá thể trên manifest hiện tại. `python tools/check_day.py` so hai lượt đầy đủ từng byte. [Phase 2](phase-2.md) · [Phase 3](phase-3.md) | 61 test đạt. Một lượt đầy đủ có 22.200 tick. |
| AC-P4-05 · Bản đóng gói và lệnh chạy | Đóng gói từ cây Git bằng `git archive`. Kiểm lệnh live, test, headless và manifest trong [README](../../README.md). [Ghi chú phát hành](../release-notes.md) | Kiểm chạy từ ZIP trên Windows. macOS và Linux chưa chạy trực tiếp tại máy này. |
| AC-P4-06 · Bằng chứng nhóm | [Retro](../retro.md) · [Nhật ký AI](../ai-usage-log.md) · [Phản tư từng thành viên](../members/) · [Bằng chứng bàn giao Phase 1](../proof/phase-4/transfer-summary.md) | Đã lưu hồ sơ, dữ liệu benchmark và kết quả soak. |

Tag lịch sử `phase-4` và `v1.0.0` giữ tại `62092e2`. Bản sửa đóng gói và phát hành dưới tag `v1.0.1` theo quyết định của nhóm.

## Rà soát cả bốn phase

| Phạm vi | Kết quả rà |
|---|---|
| Phase 1 | Chạy lại `gather-proof` và `verify-transfer` trên bản sạch cùng fixture v1.0. Hái, bắt, cập bến, nhập kho, nấu, phục vụ và thanh toán cho kết quả tất định. [Bằng chứng Phase 1](phase-1.md) |
| Phase 2 | Vòng ngày, Shop, pause, lên cấp, cá bơi, Cá Sấu và manifest có test. Bài test demo chạy đủ một ngày có thanh toán và đóng Shop. [Bằng chứng Phase 2](phase-2.md) |
| Phase 3 | Đã so id và độ tươi giữa file kho, sự kiện `gather_end` và `stock` tick 0 của Quán. Loại nguyên liệu hoặc trường fixture không hợp lệ trả mã 2 trước khi tạo output. [Bằng chứng Phase 3](phase-3.md) |
| Phase 4 | Benchmark, soak, tương phản cao và ZIP có bằng chứng ở v1.0.1. Bản bàn giao nguồn đạt 64 test, gồm ca demo và hồi quy validate bổ sung sau bản phát hành. |
| Nộp bài | GitHub đã xác nhận fork công khai có tên `K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi`, theo mẫu trong đề. Chủ repo có quyền admin và `ArsNeonci` có quyền Write. GitHub gắn 5 commit thường trên `main` với mỗi thành viên. Repo thực tế có hai thành viên. Bốn tag `phase-1` đến `phase-4` cùng trỏ tới manifest v1.0 tại `62092e2`, còn bản v1.3 nằm ở release `v1.0.1`. |

## Demo và nộp bài

Nhóm chọn nộp [video demo MP4](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/releases/download/v1.0.1/chonoi-demo.mp4) dài **3 phút 8 giây**. Clip ghi lượt chơi qua Gather, Quán và Shop, kèm phần chạy kiểm thử. `NguyenGL03` đã duyệt phản tư cá nhân. [Phản tư của nhóm](../members/)

Video và ZIP được lưu cùng [GitHub Release v1.0.1](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/releases/tag/v1.0.1). Video quay với bản nguồn có cảnh sông mới, cá và bông súng bổ sung. ZIP vẫn là bản đóng gói tại tag `v1.0.1`. [Mã nguồn bàn giao trên `main`](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/tree/main)

Nhóm đã xác nhận các điều kiện nộp còn lại. Hồ sơ ghi đúng số thành viên thực tế là hai. Các tag lịch sử giữ nguyên theo quyết định của nhóm.

### Tập và quay trên Windows

Chạy từ workspace đã cập nhật. Bản tập dùng bố trí cố định, ca Quán 27 giây và Shop 5 giây. Hãy nói rõ điều này khi demo. Đồng hồ Shop bắt đầu khi bấm **Vào Shop** ở màn hình kết quả.

```powershell
python -m chonoi.live --mode day --days 1 --seed 7 --scenario docs/proof/phase-4/demo-scenario.json --shop-seconds 5
```

1. **0:00–2:30 · Chơi một ngày.** Mở địa chỉ in trong terminal rồi bấm **Chơi**. Bơi sang phải đến hai nút bông súng và bấm **E** ở từng nút. Cá lóc nằm ngay dưới nút thứ hai. Lặn xuống, bấm **Space**, nổi lên rồi bơi trái về bến và bấm **E**. Khi mở Quán, đợi khách ở T1 gọi món, bấm **E** tại B1 để nấu. Bấm **E** lấy món khi bếp báo đã chín, đi chéo xuống phải tới T1 và bấm **E** phục vụ. Đợi khách thanh toán, qua màn kết quả, vào Shop và bấm **Đóng Shop**.
2. **2:30–3:00 · Chạy test.** Mở terminal khác, chạy `python -m unittest discover -s tests -v` và giữ dòng `OK` trên màn hình.
3. **3:00–4:30 · Chỉ bằng chứng.** Mở [phân công](../plan/phan-cong-lab12.md), hai [bản phản tư](../members/) và lịch sử commit để nói mỗi người đã làm gì. Mở ma trận này rồi chỉ ra file [benchmark](../proof/phase-4/bench.json), [soak](../proof/phase-4/soak.json) và liên kết Release. Nếu quay video, kiểm tra video đã xuất là `.mp4`, có thể xem được và dài dưới 5 phút trước khi nộp.

Nếu chỉ có ZIP v1.0.1, chạy `python -m chonoi.live --mode day --days 1 --seed 7` để chơi ngày mặc định. Hai nút bông súng nằm tại x=44 và x=60.
