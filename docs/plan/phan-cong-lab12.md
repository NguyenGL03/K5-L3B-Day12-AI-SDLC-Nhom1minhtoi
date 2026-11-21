# Phân công Lab 12 — Quán Ăn Chợ Nổi

**Người 1** phụ trách buổi sáng (`gather`) và làm đầu mối hỏi giảng viên (PO). **Người 2** phụ trách buổi tối (`quan`), tích hợp và phát hành. Cả hai tự kiểm chứng phần mình và đọc chéo thay đổi của nhau.

**Quy mô nhóm.** Bảng này chia việc cho hai người. Lab yêu cầu nhóm nộp bài có 4–6 thành viên, và `tools/check_team.py` kiểm tra điều đó. Nếu nhóm thực tế chỉ có hai người, Người 1 ghi câu hỏi vào `docs/clarify.md` và xác nhận với giảng viên cách nộp. Khi chốt danh sách, điền `TEAM.md` và đặt `team_size` theo số thành viên thực tế.

## Phần việc mỗi người

| | Người 1 — Gather và PO | Người 2 — Quán và tích hợp |
|---|---|---|
| Luật chơi Phase 1 | Hoàn thiện `chonoi/sim/gather.py`. Xử lý lặn/nổi, oxy, ngạt, Máu, ngất, giỏ LIFO, hái và mọc lại, bắt cá và hồi chiêu. Kiểm tra kết thúc ở bến, hết giờ và ngất, cùng file kho tương ứng. | Hoàn thiện `chonoi/sim/quan.py`. Xử lý khách và chọn món, giữ chỗ nguyên liệu, kiên nhẫn và bỏ đi, nấu–bưng–phục vụ, trả tiền, boa, uy tín và hết ca. Kiểm tra nạp kho từ `gather`. |
| Tài liệu và kiểm chứng | Giữ `docs/clarify.md`. Đối chiếu AC của `gather` với PRD và lưu ca kiểm chứng, JSONL, file kho mẫu chạy được vào `docs/proof/phase-n/`. | Giữ tài liệu tích hợp trong `docs/contracts/` theo thỏa thuận của cả hai. Đối chiếu AC của `quan`, gom ma trận `docs/verification/phase-n.md` từ bằng chứng của hai người và ghi kết quả thực tế. |
| Git và phát hành | Đọc chéo thay đổi `quan`, chuẩn bị phần trình diễn lặn, hái và bắt cá. | Đọc chéo thay đổi `gather`, chuẩn bị phần trình diễn nấu và phục vụ, chạy kiểm tra tích hợp, gắn tag và tạo Release. |

Chốt sớm ba điểm bàn giao theo PRD-0 và [hợp đồng tích hợp](../contracts/README.md): schema kho, lệnh và snapshot giữa mô phỏng với UI, tên và payload sự kiện. Người 2 có thể làm `quan` song song bằng [`inventory.sample.json`](../contracts/inventory.sample.json). Khi `gather` xuất được kho, chạy luồng `gather` → file kho → `quan` và đối chiếu `stock` ở snapshot đầu với `items` trong file. Lấy số liệu từ `game.contract.json`, dùng `Streams` cho ngẫu nhiên và giữ quy ước cấp/sắp ID của repo.

## Lịch 3 giờ

Các mốc dưới đây theo [README](../../README.md). Yêu cầu chi tiết mở theo giờ trên [Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg). Với Phase 2–4, bảng phân công đầu mối và việc bàn giao. Đầu mỗi phase, cả hai đọc yêu cầu vừa mở, chia AC theo module và chốt người làm cho từng thay đổi dùng chung.

| Phase và hạn | Người 1 | Người 2 | Bàn giao |
|---|---|---|---|
| **1 · trước 1:00** | Đọc PRD-0, xác nhận các chỗ mơ hồ, làm luật `gather` và tạo kho từ lượt chạy thật. | Chốt giao diện tích hợp, làm luật `quan` với kho mẫu rồi chạy với kho do `gather` tạo. | Khởi tạo fork công khai theo tên lab, thêm collaborator, điền `TEAM.md`. Chạy headless hai mode, lưu bằng chứng, cập nhật `AGENTS.md` và gắn `phase-1`. |
| **2 · trước 1:55** | Đọc yêu cầu mới, xử lý AC phía `gather` hoặc lát được giao, lưu bằng chứng và ghi câu hỏi phát sinh. | Xử lý AC phía `quan` hoặc lát được giao, rà thay đổi hợp đồng, kiểm thử lại luồng giữa hai mode. | Cập nhật ma trận kiểm chứng và `AGENTS.md`, ghi retro nhanh cùng một hành động cho Phase 3, gắn `phase-2`. |
| **3 · trước 2:30** | Làm lát theo yêu cầu mới phía `gather` hoặc lát dùng chung đã nhận, thực hiện hành động từ retro Phase 2. | Làm lát theo yêu cầu mới phía `quan` hoặc lát dùng chung đã nhận, tích hợp và chạy lại các ca phase trước. | Lưu bằng chứng, cập nhật `AGENTS.md` và gắn `phase-3`. |
| **4 · trước 3:00** | Hoàn tất lát được giao, chuẩn bị demo và tổng hợp retro cuối. | Hoàn tất lát được giao, chạy kiểm tra cuối và thực hiện phát hành. | Hoàn tất kiểm chứng, nhật ký AI, phản tư cá nhân và `AGENTS.md`. Gắn `phase-4` và tạo Release `v1.0.0`. |

## Kiểm tra và ghi nhận đóng góp

- Mỗi người có ít nhất **3 commit có nội dung** bằng GitHub handle trong `TEAM.md`. Có thể tách theo các phần như oxy/ngất, hái/bắt cá, kiểm chứng kho cho Người 1 và vòng đời khách, phục vụ/tính điểm, kiểm chứng tích hợp cho Người 2. Khi làm cặp, ghi `Co-authored-by:`.
- Mỗi phase, cả hai ghi việc dùng AI vào `docs/ai-usage-log.md`, dẫn bằng chứng từ `docs/verification/phase-n.md` và ghi phần chưa đạt. Trước khi gắn tag, đọc chéo thay đổi và chạy test. Đến hạn thì gắn tag tại bản chạy được và ghi rõ phần còn thiếu. Mỗi người tự hoàn thành `docs/members/<handle>.md` kèm link commit và phần đã review.
- Cả hai cùng làm bộ tối thiểu hai skill, hook hoặc lệnh tự viết theo `AGENTS.md`. Có thể giao Người 1 viết lệnh tạo bằng chứng headless và Người 2 viết lệnh kiểm tra chuyển kho. Ghi tên và cách dùng khi công cụ đã chạy được.

Lệnh kiểm tra cơ bản của starter, chạy từ thư mục gốc bằng Bash. Ca bàn giao kho dùng lượt `gather` kết thúc bằng cập bến hoặc hết giờ để tạo `kho.json`, rồi truyền file qua `--inventory` cho `quan`.

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out gather.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --out quan.jsonl
```
