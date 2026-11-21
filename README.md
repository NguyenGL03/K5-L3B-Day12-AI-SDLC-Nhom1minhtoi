# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

Yêu cầu Python 3.10 trở lên và trình duyệt trên macOS hoặc Linux. Game dùng thư viện chuẩn Python. Benchmark cần Chromium, Chrome hoặc Edge.

```bash
git clone https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi.git && cd K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi
python3 -m unittest discover -s tests -v                            # smoke test
python3 -m chonoi.live --mode day                                   # mở địa chỉ in ra trên trình duyệt
```

Chơi bằng WASD hoặc phím mũi tên. **E** hái, cập bến, nấu, lấy món hoặc phục vụ tùy vị trí. **Space** bắt cá, **Esc/P** tạm dừng, **R** chơi lại. Điểm bằng tổng tiền thu gồm boa cộng `100 × floor(uy tín)`. Mua nâng cấp chỉ trừ tiền trong ví.

Chạy headless với `--mode gather`, `--mode quan` hoặc `--mode day`. `python3 tools/check_day.py` kiểm một Ngày đầy đủ và so JSONL của hai lượt cùng seed. Xem [kiểm chứng Phase 2](docs/verification/phase-2.md) và [trạng thái Phase 3](docs/verification/phase-3.md).

```bash
python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 22200 --out out.jsonl
python3 -m chonoi.benchmark --seed 42 --duration 30 --out bench.json
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

Bấm **Tương phản cao** ở góc trên để tăng độ tương phản và đọc cảnh báo oxy, thủy quái hoặc khách sắp giận bằng chữ. Benchmark mở trình duyệt headless ở 1280×720, chạy đường bơi cố định và đo nhịp khung hình thực. Có thể đặt `CHONOI_BROWSER` nếu trình duyệt nằm ngoài vị trí cài mặc định. [Kiểm chứng Phase 4](docs/verification/phase-4.md)

Video demo và bản ZIP nằm trong [GitHub Release v1.0.1](https://github.com/NguyenGL03/K5-L3B-LAB-Day12-AI-SDLC-Nhom1minhtoi/releases/tag/v1.0.1). Kịch bản tập và lệnh PowerShell nằm trong [checklist bàn giao](docs/verification/phase-4.md#demo-và-nộp-bài).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

### Sáng tạo của nhóm (`Nhom1minhtoi`)
Các hiệu ứng dưới đây nằm trong `chonoi/web/river.js` và `chonoi/web/index.html`, chỉ chạy trên trình duyệt:
1. **Hiệu ứng thị giác & cảnh báo sinh tồn khi lặn (`gather`):**
   - Hiệu ứng bọt khí nổi lên theo nhịp bơi khi Út Sen lặn dưới mặt nước (`d > surface_depth`).
   - Viền cảnh báo nhịp thở (pulse đỏ quanh màn hình) khi lượng oxy xuống dưới 25% hoặc đang trong trạng thái ngạt (`zero_oxy_ticks > 0`).
2. **Đèn lồng chợ nổi đêm & HUD quản lý quán thông minh (`quan`):**
   - Ánh đèn lồng vàng ấm tỏa sáng quanh từng bàn ăn trên ghe quán buổi tối.
   - Hiển thị tên món tiếng Việt, trạng thái bếp, món đang bưng và mức kiên nhẫn của khách.
   - HUD **Kho khả dụng** loại hàng ươn và phần đã giữ cho khách khỏi số lượng có thể dùng, đồng thời hiển thị số cá thể đã ươn.

Khi chơi `day` hoặc `gather` trên trình duyệt với bản đồ mặc định, sông có **12 đàn cá ban đầu**, thử sinh thêm mỗi **3 giây** đến tối đa 18 đàn. Có thêm hai bụi bông súng gần bến, với bụi mới xuất hiện mỗi **8 giây** đến tối đa 8 bụi. Cá mới có thể bắt, bông súng mới có thể hái và mọc lại. Chế độ headless và lượt chơi với `--scenario` dùng số liệu gốc.


## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
