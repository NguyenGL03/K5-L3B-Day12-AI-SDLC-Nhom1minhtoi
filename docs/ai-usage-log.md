# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | `ArsNeonci` | Antigravity (Gemini) | Đọc tài liệu dự án, phân tích tránh conflict Git, cài đặt Lát 1 & Lát 2 trong `chonoi/sim/gather.py`, viết `tests/test_gather.py` và skill `gather-proof` | ~25k tokens | AI dùng toán tử `&&` trên PowerShell 5.1 làm lệnh gộp báo lỗi cú pháp; phát hiện ngay qua stderr và chuyển sang `; if ($LASTEXITCODE -eq 0)` |
| Phase 2 | `NguyenGL03` | Codex | Tích hợp Gather, Quán, Shop, pause, headless và chế độ ngày trên trình duyệt | Chưa đo | Smoke cũ giả định 6 đàn và từ chối mode `day`. Đối chiếu lại với TICKET-02 và cập nhật hai kỳ vọng đã bị thay thế. |
| Phase 3 | `NguyenGL03` | Codex | Kiểm schema, hao tươi và chuyển file giữa Gather và bộ kho cá thể phía Quán | Chưa đo | Thêm ca sát ngưỡng để phát hiện làm tròn độ tươi qua file có thể đưa hàng ươn về đúng 30. |

