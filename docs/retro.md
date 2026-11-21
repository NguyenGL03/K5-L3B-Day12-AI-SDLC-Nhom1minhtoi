# Retro nhóm

## Phase 2 (nhanh)
- **Điều tốt:**
  - Phân tách rõ ranh giới file ngay từ đầu (`gather.py` + `test_gather.py` tách biệt với `quan.py` + `test_quan_phase1.py` / `test_quan_phase2.py`) nên khi merge nhánh `ars` và `develop` không phát sinh bất kỳ xung đột Git nào.
  - Cả hai mô phỏng `gather` và `quan` đều vượt qua 100% bài kiểm thử tất định byte-for-byte ngay từ lần tích hợp đầu tiên.
- **Điều tệ:**
  - Payload `stove.dish` trong `QuanSim` chuyển sang object `{"order_id", "dish_id", "base_price"}` nhưng giao diện `chonoi/web/index.html` ban đầu vẽ trực tiếp `st.dish` khiến HUD hiện `[object Object]`.
  - Các file tài liệu tổng hợp (`docs/verification/phase-1.md`, `docs/contracts/README.md`) chưa được điền ngay tại thời điểm code xong Phase 1.
- **1 hành động cho Phase 3:**
  - Bổ sung skill tự động hóa thứ 2 (`verify-transfer`) để kiểm tra xuyên suốt luồng `gather` → `kho.json` → `quan`, đồng thời sửa `chonoi/web/index.html` để đọc đúng `st.dish.dish_id` và cập nhật ma trận kiểm chứng ngay sau mỗi lần chạy test.

## Phase 4 (cuối)
- **Rà lại hành động Phase 2: đã làm chưa? vì sao?**
  - **Đã làm đầy đủ:** Nhóm đã xây dựng skill `.agents/skills/verify-transfer/` tự động chạy nối 2 tiến trình `gather` → `gather-kho.json` → `quan`, sửa lỗi hiển thị `st.dish.dish_id` cùng kho khả dụng trên HUD `chonoi/web/index.html`, và hoàn thiện toàn bộ ma trận `docs/verification/phase-1..4.md`.
- **Điều tốt / điều tệ:**
  - *Điều tốt:* Quy trình AI SDLC với 2 skills tự tạo (`gather-proof` và `verify-transfer`), ADR cô lập file và dùng `Fraction` trong `QuanStock` giúp bộ 52+ bài test (bao gồm cả hồi quy Phase 1, Phase 2, Phase 3) luôn xanh 100%.
  - *Điều tệ:* Nhóm chỉ có 2 thành viên nên khối lượng tài liệu & kiểm chứng mỗi người phải gánh gấp đôi so với nhóm 4–6 người tiêu chuẩn.
- **Số liệu: số commit theo người, cách đọc code của nhau, token theo người:**
  - **Số commit theo người:**
    - `ArsNeonci` (Chu Quang Linh): **≥ 6 commits** (`fe3052a`, `0d26d73`, `4c0f6b7`, `f095664`, `2ca7983` + commit hoàn thiện tích hợp/verification/skills).
    - `NguyenGL03` (Khương Hoàng Nguyên): **4 commits** (`40c42aa`, `7936b69`, `b8ec20b`, `3691aeb`).
  - **Cách đọc code của nhau:** Đọc chéo trực tiếp trên diff từng commit trước khi merge nhánh `develop` và `ars`; `ArsNeonci` review logic `QuanSim` & `QuanStock` (phát hiện điểm cần đồng bộ `st.dish.dish_id` với `index.html`), `NguyenGL03` đối chiếu schema `gather-kho.json` với `QuanSim.stock`.
  - **Token ước tính theo người:** `ArsNeonci` ~65k tokens · `NguyenGL03` ~60k tokens (tổng toàn nhóm ~125k tokens).
- **Một lần AI sai và cách nhóm phát hiện:**
  - *Tình huống 1 (Harness/Script):* Khi viết script `.agents/skills/gather-proof/scripts/run_gather_proof.py`, AI tính thiếu 1 bậc `os.path.dirname` cho biến `ROOT`, dẫn đến chạy `python -m chonoi.headless` từ thư mục `.agents/` và báo `ModuleNotFoundError: No module named 'chonoi'`. Nhóm phát hiện ngay khi chạy thử skill lần đầu và sửa lại đường dẫn tương đối `os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")`.
  - *Tình huống 2 (Luật mô phỏng):* Trong phép trừ độ tươi mỗi tick (`0.25 / 60`), dùng `float` thông thường có nguy cơ sai số dấu phẩy động ở biên ngưỡng `spoiled_below = 30`. Nhóm phát hiện khi thiết kế test biên `30.0125` (3 tick về đúng `30`, tick thứ 4 mới `< 30`) và chuyển sang dùng `fractions.Fraction` trong `chonoi/sim/quan_stock.py` cùng `decimal.Decimal` cho tiền boa/uy tín trong `chonoi/sim/quan.py`.
- **Nếu làm lại, đổi gì:**
  - Chốt và điền luôn `docs/contracts/README.md` cùng `docs/verification/phase-1.md` ngay trong 15 phút đầu thay vì đợi sau khi code xong cả hai module mới gom lại.
  - Với lần phát hành sau, Integrator chạy lại test trên bản hợp nhất trước khi gắn tag. Bản sửa v1.0.1 phát hiện ca bàn giao của Phase 1 phụ thuộc cá đứng yên. Ca hồi quy nay dựng đàn cá cố định, còn soak chạy theo manifest hiện tại.
