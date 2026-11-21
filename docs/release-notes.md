# v1.0.1 — Bản sửa Phase 4 của Quán Ăn Chợ Nổi

Game chạy một vòng ngày gồm Lặn & Hái, Mở Quán và Shop. Bản này bổ sung kho cá thể có độ tươi, giá món tính lúc nấu, ba cảnh báo bằng chữ và nút tương phản cao. Manifest Test Contract v1.3 có lệnh benchmark và soak 10 ngày.

## Cách chạy bản ZIP

Giải nén ZIP, mở terminal trong thư mục giải nén, chạy `python3 -m chonoi.live --mode day`, rồi mở địa chỉ in ra. Cần Python 3.10 trở lên và trình duyệt. Dùng WASD hoặc mũi tên để di chuyển, E để tương tác, Space để bắt cá và Esc/P để tạm dừng.

Chạy test bằng `python3 -m unittest discover -s tests -v`. Lệnh headless, benchmark và soak nằm trong [README](../README.md). Kết quả đã đo nằm trong [ma trận Phase 4](verification/phase-4.md).

## Giới hạn đã biết

- Kho đếm của bản cũ cần chuyển sang mảng cá thể trước khi nạp ở v1.3. [Hợp đồng kho](contracts/README.md)
- Số FPS và thời gian tải được đo trên Edge headless ở Windows. Máy chấm và phiên trình duyệt hiển thị có thể cho số khác.
- Nhóm có hai thành viên thực tế. Quy mô nhóm đã ghi để đối chiếu với yêu cầu lớp. [Clarify](clarify.md)
