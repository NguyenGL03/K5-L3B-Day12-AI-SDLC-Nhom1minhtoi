# Bằng chứng tích hợp End-to-End: `gather` → `gather-kho.json` → `quan`

- **Kho xuất từ `gather` (`docs/proof/phase-1/gather-kho.json`):** `{"bong_dien_dien": 1, "ca_linh": 3}`
- **`stock` tại snapshot tick 0 của `quan`:** `{"bong_dien_dien": 1, "ca_linh": 3}` (khớp 100%)
- **Tính tất định byte-for-byte:** Đạt (chạy 2 lần cùng `--seed 1` khớp từng byte).

## Chuỗi sự kiện ghi nhận trong `docs/proof/phase-1/quan-from-gather.jsonl`

| Tick | Sự kiện | Payload `data` |
|---|---|---|
| `120` | `customer_arrived` | `{"order_id": "C1", "table_id": "T1", "dish_id": "lau_ca_linh_dien_dien"}` |
| `126` | `cook_started` | `{"order_id": "C1", "stove_id": "B1", "dish_id": "lau_ca_linh_dien_dien", "items": ["bong_dien_dien", "ca_linh", "ca_linh", "ca_linh"], "base_price": 120}` |
| `726` | `dish_ready` | `{"order_id": "C1", "stove_id": "B1", "dish_id": "lau_ca_linh_dien_dien"}` |
| `731` | `dish_picked` | `{"order_id": "C1", "stove_id": "B1", "dish_id": "lau_ca_linh_dien_dien"}` |
| `866` | `served` | `{"order_id": "C1", "table_id": "T1", "dish_id": "lau_ca_linh_dien_dien", "patience_ticks_left": 2854, "base_price": 120, "tip": 24}` |
| `1466` | `paid` | `{"order_id": "C1", "table_id": "T1", "base_price": 120, "tip": 24, "amount": 144, "reason": "finished_eating"}` |

## Kết quả cuối lượt (`end` row tại tick `1500`)
- `money`: `144` · `earned`: `144` · `reputation`: `3.2` · `score`: `444`
