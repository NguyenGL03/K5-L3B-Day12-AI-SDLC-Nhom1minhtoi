# Hợp đồng tích hợp (`gather` ↔ `quan` ↔ `client/ui`)

Chốt giữa **Chu Quang Linh (`ArsNeonci` — Lead Gather/PO)** và **Khương Hoàng Nguyên (`NguyenGL03` — Lead Quan/Integrator)**.

## 1. Schema file kho (Contract G)
- **Định dạng v1.0 / v1.1 (kho đếm nguyên liệu):**
  ```json
  {"items": {"bong_dien_dien": 1, "ca_linh": 3}}
  ```
  - Chỉ giữ các khóa nguyên liệu thuộc thực đơn (`ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`, và mở rộng `ca_keo`, `keo_neo` ở Phase 2) có số lượng nguyên dương (`> 0`), sắp xếp khóa theo thứ tự từ điển, ghi nguyên tử qua file tạm.
  - File mẫu tĩnh: [`inventory.sample.json`](inventory.sample.json).
  - File kho sinh từ lượt chạy `gather` thực tế: [`../proof/phase-1/gather-kho.json`](../proof/phase-1/gather-kho.json).
- **Quy tắc bàn giao:**
  - `gather` chỉ ghi file `--inventory-out` đúng **một lần** khi phát sự kiện `gather_end` (`docked`, `time`, hoặc `fainted` với `{"items": {}}`). Nếu dừng do `tick_limit` thì không ghi đè file kho đích.
  - `quan` nạp kho qua `--inventory <path>` hoặc `scenario.quan.stock` (nếu truyền cả hai thì thoát mã `2` trước khi ghi output).
- **Mở rộng Phase 3 (`chonoi/sim/quan_stock.py`):**
  - Lớp `QuanStock` quản lý kho cá thể `[{"id": "I1", "kind": "ca_loc", "fresh": 100.0}]` với hao tươi mỗi tick và ngưỡng ươn `spoiled_below`.

## 2. Giao diện giữa `sim/*` và `client/ui` (`chonoi/live.py` & `chonoi/web/index.html`)
- **`GET /state`** (JSON snapshot mỗi tick):
  - Trường chung: `type`, `tick`, `sim_tick`, `mode`, `phase`, `phase_tick`, `state` (`playing`|`finished`), `time_left_ticks`, `money`, `earned`, `reputation`, `score`, `meta`, `events`, `finished`, `reason`, `error`.
  - Riêng `gather`: `player` (`pos: [x, d]`, `vel`, `heading_deg`, `oxygen_ticks`, `oxygen_max_ticks`, `hp`, `hp_max`, `zero_oxy_ticks`, `invuln_ticks`, `catch_cd_ticks`, `at_surface`), `hold` (mảng LIFO), `hold_count`, `hold_capacity`, `nodes` (`id`, `pos`, `kind`, `ready`, `regrow_ticks`), `fish` (`id`, `pos`, `kind`, `heading_deg`).
  - Riêng `quan`: `player` (`pos: [x, z]`, `vel`), `stock`, `hand` (`null` hoặc `{"order_id", "dish_id", "base_price"}`), `stoves` (`id`, `pos`, `state`, `dish`, `cook_ticks_left`, `ready_ticks`), `tables` (`id`, `pos`, `customer_id`), `customers` (`id`, `table_id`, `dish_id`, `order_tick`, `state`, `order_status`, `patience_ticks_left`, `eat_ticks_left`, `reserved`, `base_price`, `tip`).
- **`POST /input`**: `{"move": [dx, dy], "interact": bool, "catch": bool}`.
- **`POST /restart`**: Khởi động lại phiên chơi với cùng `seed` và `scenario`.

## 3. Danh sách sự kiện (`type: "event"`)

### Chế độ `gather` (`chonoi/sim/gather.py`)
| Tên sự kiện | `data` payload | Khi nào phát |
|---|---|---|
| `node_regrown` | `{"node_id": str}` | Bộ đếm `regrow_ticks` của nút hái giảm về `0`. |
| `dive` | `{"pos": [x, d]}` | Vị trí chuyển từ mặt nước (`d <= surface_depth`) xuống dưới nước (`d > surface_depth`). |
| `surface` | `{"pos": [x, d]}` | Vị trí chuyển từ dưới nước lên mặt nước (`d <= surface_depth`). |
| `oxygen_empty` | `{"pos": [x, d]}` | `oxygen_ticks` dưới nước giảm từ `> 0` về `0`. |
| `choke` | `{"hp": int, "pos": [x, d]}` | Đang dưới nước với `oxygen_ticks == 0` đủ `choke_interval_ticks` (trừ 1 Máu). |
| `faint` | `{"pos": [x, d]}` | Máu giảm về `0` sau khi `choke` (xóa sạch giỏ `hold`). |
| `gather` | `{"node_id": str, "kind": str, "count": int, "hold_count": int}` | Bấm `interact` ở mặt nước (ngoài bến) hái nút `ready` gần nhất khi giỏ đủ chỗ. |
| `fish_caught` | `{"fish_id": str, "kind": str, "count": int, "hold_count": int}` | Bấm `catch` dưới nước khi `catch_cd_ticks == 0` bắt đàn cá gần nhất khi giỏ đủ chỗ. |
| `hold_full` | `{"node_id"\|"fish_id": str, "kind": str, "hold_count": int, "hold_capacity": int}` | Hái nút hoặc bắt cá nhưng sức chứa còn lại của giỏ không đủ. |
| `gather_end` | `{"reason": "docked"\|"time"\|"fainted", "inventory": {"items": dict}}` | Kết thúc buổi sáng do cập bến, hết giờ hoặc ngất. |

### Chế độ `quan` (`chonoi/sim/quan.py` & `chonoi/sim/quan_stock.py`)
| Tên sự kiện | `data` payload | Khi nào phát |
|---|---|---|
| `customer_arrived` | `{"order_id": str, "table_id": str, "dish_id": str}` | Khách mới đến theo lịch, có bàn trống và có món đủ nguyên liệu để giữ chỗ. |
| `no_dish` | `{}` | Tới lịch khách đến và có bàn trống nhưng không món nào trong thực đơn đủ nguyên liệu khả dụng. |
| `cook_started` | `{"order_id": str, "stove_id": str, "dish_id": str, "items": list[str], "base_price": int}` | Bấm `interact` tại bếp `idle`, lấy đơn `reserved` ưu tiên `(order_tick, id_key(table_id))` và trừ kho. |
| `dish_ready` | `{"order_id": str, "stove_id": str, "dish_id": str}` | Bếp đang `cooking` giảm `cook_ticks_left` về `0` chuyển sang `ready`. |
| `dish_picked` | `{"order_id": str, "stove_id": str, "dish_id": str}` | Bấm `interact` tại bếp `ready` khi `hand == None` để bưng món lên tay. |
| `served` | `{"order_id": str, "table_id": str, "dish_id": str, "patience_ticks_left": int, "base_price": int, "tip": int}` | Bấm `interact` tại bàn có khách khớp `hand.order_id`, chốt tiền boa theo tỷ lệ kiên nhẫn. |
| `paid` | `{"order_id": str, "table_id": str, "base_price": int, "tip": int, "amount": int, "reason": "finished_eating"\|"closing"}` | Khách ăn xong (`eat_ticks_left == 0`) hoặc đóng ca khi đang ăn; cộng tiền và uy tín (nếu có boa). |
| `customer_left` | `{"order_id": str, "table_id": str, "reason": "patience"\|"closing", "reputation": float}` | Khách đang chờ hết kiên nhẫn (trừ uy tín) hoặc đóng ca (giữ nguyên uy tín); hủy món liên quan. |
| `spoiled` | `{"item_id": str, "kind": str, "location": "stock"}` | Cá thể nguyên liệu trong `QuanStock` (Phase 3) giảm độ tươi xuống dưới `spoiled_below`. |
| `quan_end` | `{"reason": "time", "money": int, "earned": int, "shift_earned": int, "reputation": float}` | Hết giờ ca tối (`time_left_ticks == 0`). |

