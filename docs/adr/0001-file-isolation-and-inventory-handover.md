# ADR-0001: Cô lập phạm vi file theo module và tách `QuanStock` cho Change Request độ tươi

- **Trạng thái:** Chấp nhận
- **Ngày, người quyết:** 2026-11-21 · Chu Quang Linh (`ArsNeonci`) & Khương Hoàng Nguyên (`NguyenGL03`)

## Bối cảnh
1. Nhóm có 2 thành viên làm việc song song với tốc độ cao cùng AI coding agent trên 2 chế độ `gather` và `quan`. Nếu cả hai cùng sửa chung một file test (`tests/test_python_starter_units.py`) hoặc sửa chung `chonoi/scenario.py` sẽ dẫn tới xung đột Git liên tục khi merge.
2. Ở Phase 3, yêu cầu mới chuyển kho từ dạng đếm số lượng (`{"ca_loc": 1}`) sang dạng danh sách cá thể có độ tươi (`[{"id": "I1", "kind": "ca_loc", "fresh": 100}]`) và hao tươi mỗi tick. Tuy nhiên, bộ test tự động vẫn kiểm tra hồi quy các ca Phase 1 (`test_smoke_p1.py`) vốn dùng schema kho đếm v1.0.

## Các lựa chọn đã cân nhắc
- **Lựa chọn A:** Sửa trực tiếp vào các file test sẵn có và thay thế hoàn toàn kho đếm trong `QuanSim` bằng kho cá thể.
  - *Nhược điểm:* Gây merge conflict giữa 2 thành viên và làm gãy các bài test hồi quy Phase 1/Phase 2 dùng schema kho đếm.
- **Lựa chọn B:**
  1. Cô lập tuyệt đối phạm vi file giữa 2 thành viên (`gather.py` + `test_gather.py` cho Người 1; `quan.py` + `quan_stock.py` + `test_quan_phase*.py` cho Người 2).
  2. Đặt kiểm tra mâu thuẫn scenario mức luật ngay trong `QuanSim.__init__` / `GatherSim.__init__` thay vì sửa chung `chonoi/scenario.py`.
  3. Tách logic kho cá thể có độ tươi ra lớp riêng `chonoi/sim/quan_stock.py` sử dụng `fractions.Fraction` để tính hao tươi chính xác.

## Quyết định
Chọn **Lựa chọn B**.

## Hệ quả (bảng tác động module, file, test)

| Module / File | Tác động | Người phụ trách | Test kiểm chứng |
|---|---|---|---|
| `chonoi/sim/gather.py` | Chỉ Người 1 sửa (Lát 1 & Lát 2) | `ArsNeonci` | `tests/test_gather.py`, `tests/test_smoke_p1.py` |
| `chonoi/sim/quan.py` | Chỉ Người 2 sửa (Phase 1 & Phase 2 `day_plan`, `money`, `earned`) | `NguyenGL03` | `tests/test_quan_phase1.py`, `tests/test_quan_phase2.py` |
| `chonoi/sim/quan_stock.py` | Tạo mới cho Phase 3 (độ tươi bằng `Fraction`, sự kiện `spoiled`, giữ chỗ ưu tiên `-fresh`) | `NguyenGL03` | `tests/test_quan_stock_phase3.py` |
| `chonoi/web/index.html` | Hỗ trợ hiển thị cả `stove.dish` dạng chuỗi lẫn object `{"dish_id", "order_id"}` và kho khả dụng | Cả nhóm | `tests/test_live.py` |
| Kết quả Merge `develop` ↔ `ars` | **0 conflict**, toàn bộ 52+ tests của cả 3 phase cùng PASS | Cả nhóm | `python3 -m unittest discover -s tests -v` |
