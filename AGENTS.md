# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Kiểm vòng ngày: `python3 tools/check_day.py`
- Headless: `python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 22200 --out out.jsonl`
- Chơi thử: `python3 -m chonoi.live --mode day` (WASD, E, Space, Esc/P)
- Phase 4: dùng `bench_cmd` và `soak_cmd` từ manifest. Xem tham số trong [README](README.md).

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi trong `chonoi/sim/`. Khi sửa kho, xem [quy tắc giá và giữ chỗ](docs/verification/phase-3.md).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- `gather-proof` (`.agents/skills/gather-proof/SKILL.md`): Chạy kiểm chứng tính tất định byte-for-byte cho chế độ `gather` và sinh bộ bằng chứng headless (`gather-docked.jsonl`, `gather-fainted.jsonl`, `gather-kho.json`) vào `docs/proof/phase-<n>/`. Lệnh: `python3 .agents/skills/gather-proof/scripts/run_gather_proof.py --phase 1`.
- `tools/check_day.py`: Chạy hai lượt headless cùng seed, kiểm thứ tự ba pha, `days_completed` và tính tất định của JSONL.
- `verify-transfer` (`.agents/skills/verify-transfer/SKILL.md`): Kiểm chứng luồng bàn giao kho End-to-End từ `gather` sang `quan` (`gather-kho.json` → `quan-from-gather.jsonl`), đối chiếu `stock` tick 0, xác minh đầy đủ chuỗi sự kiện nấu–bưng–phục vụ–thanh toán và tính tất định byte-for-byte của `quan`. Lệnh: `python3 .agents/skills/verify-transfer/scripts/run_verify_transfer.py`.
- Hai skill dùng bản Phase 1 có đàn cá đứng yên. Đặt `CHONOI_CONTRACT=tests/fixtures/contract_v10.json` trước khi chạy lại.

