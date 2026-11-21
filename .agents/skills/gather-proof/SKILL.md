---
name: gather-proof
description: Chạy kiểm thử chế độ gather, xác minh tính tất định byte-for-byte và sinh bộ bằng chứng headless (JSONL + file kho mẫu) vào docs/proof/phase-<n>/.
---

# Skill: Gather Proof & Determinism Verifier (`gather-proof`)

Dùng skill này khi hoàn thành hoặc chỉnh sửa luật chơi buổi sáng (`chonoi/sim/gather.py`) ở mỗi phase để:
1. Chạy toàn bộ unit test và black-box test của `gather` (`tests/test_gather.py`).
2. Chạy kịch bản chơi `gather` thực tế ở chế độ headless (hái bông điên điển `N1`, lặn bắt đàn cá linh `F1`, nổi lên bơi về bến cập bến) hai lần với cùng `--seed` và đối chiếu từng byte.
3. Sinh file bằng chứng chuẩn vào `docs/proof/phase-<n>/`:
   - `gather-inputs.json`: kịch bản phím bấm mẫu.
   - `gather-docked.jsonl`: log lượt chơi hoàn chỉnh kết thúc tại bến (`reason: "docked"`).
   - `gather-kho.json`: file kho thực tế xuất ra từ lượt chơi để bàn giao cho chế độ `quan`.
   - `gather-fainted.jsonl`: log kiểm chứng trường hợp cạn oxy dẫn tới ngạt và ngất (`reason: "fainted"`, kho rỗng).

## Lệnh chạy

```bash
python3 .agents/skills/gather-proof/scripts/run_gather_proof.py --phase 1
```
