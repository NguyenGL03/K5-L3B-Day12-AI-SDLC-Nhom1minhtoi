# Kế hoạch Phase 1 (≤ 1 trang)

- **Mục tiêu:** Hoàn thiện mô phỏng lõi Phase 1 cho hai chế độ `gather` và `quan` theo PRD-0 & Test Contract v1.0, đảm bảo tính tất định byte-for-byte, bàn giao file kho giữa hai chế độ và lưu đầy đủ bằng chứng vào `docs/proof/phase-1/`.
- **Việc / người / phụ thuộc:**
  - **Người 1 — Chu Quang Linh (`ArsNeonci`, PO & Lead Gather):**
    - Lát 1: Lặn/nổi (`dive`/`surface`), oxy mặt nước/dưới nước (`oxygen_empty`), ngạt (`zero_oxy_ticks`), mất Máu (`choke`), ngất (`faint`, xóa giỏ LIFO, `gather_end` reason `fainted`) trong `chonoi/sim/gather.py`.
    - Lát 2: Hái nút ở mặt nước (`gather`/`hold_full`, mọc lại `node_regrown`), bắt cá dưới nước (`catch`, `fish_caught`/`hold_full`, hồi chiêu `catch_cd_ticks`), cập bến xuất kho trong `chonoi/sim/gather.py`.
    - Kiểm thử & Bằng chứng: Viết unit/black-box test riêng trong `tests/test_gather.py`, tạo skill `.agents/skills/gather-proof/` và sinh log JSONL + file kho mẫu vào `docs/proof/phase-1/`.
  - **Người 2 — Khương Hoàng Nguyên (`NguyenGL03`, Integrator & Lead Quan):**
    - Lát 3 & 4: Vòng đời khách, giữ chỗ nguyên liệu, nấu bếp, bưng phục vụ, trả tiền/boa/uy tín, hết ca trong `chonoi/sim/quan.py`.
    - Tích hợp & Kiểm chứng: Giữ `docs/contracts/README.md`, viết `tests/test_quan.py`, kiểm tra nạp kho từ `gather`, tổng hợp `docs/verification/phase-1.md` và gắn tag `phase-1`.
- **Rủi ro & Cách giảm thiểu:**
  - *Xung đột Git khi merge:* Cô lập phạm vi file (`gather.py` + `test_gather.py` vs `quan.py` + `test_quan.py`), không sửa chung một file test.
  - *Sai lệch tất định (determinism):* Mọi thông số đọc từ `game.contract.json`, ngẫu nhiên qua `Streams`, sắp thực thể qua `sort_by_id`.

