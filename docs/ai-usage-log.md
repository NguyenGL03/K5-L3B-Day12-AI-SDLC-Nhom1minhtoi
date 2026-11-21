# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | `ArsNeonci` | Antigravity (Gemini) | Đọc tài liệu dự án, phân tích tránh conflict Git, cài đặt Lát 1 & Lát 2 trong `chonoi/sim/gather.py`, viết `tests/test_gather.py` và skill `gather-proof` | ~25k tokens | AI dùng toán tử `&&` trên PowerShell 5.1 làm lệnh gộp báo lỗi cú pháp; phát hiện ngay qua stderr và chuyển sang `; if ($LASTEXITCODE -eq 0)` |

