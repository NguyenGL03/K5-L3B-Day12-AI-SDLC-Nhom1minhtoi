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

Khi demo, mở `--mode day`, chơi qua Gather, Quán và đóng Shop. Sau đó chạy test và mở bảng này để đối chiếu kết quả với bằng chứng.
