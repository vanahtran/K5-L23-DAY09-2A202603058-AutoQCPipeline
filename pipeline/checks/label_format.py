"""CHECK 2 — Dòng nhãn YOLO: sai định dạng, ID lớp lạ, box tràn ảnh, box rỗng, box lặp.   (Script 2 trong slide)   ★★

Test:  pytest tests/test_label_format.py -q

Mỗi dòng nhãn: `id cx cy w h` (5 số, toạ độ 0–1). Trả về list[Issue]; `Issue.line` = số dòng (đếm từ 1).

| code             | severity | khi nào                                                                  |
|------------------|----------|--------------------------------------------------------------------------|
| BAD_FORMAT       | ERROR    | không đúng 5 cột số (dùng `parse_yolo_line`, bắt `ValueError`)           |
| BAD_CLASS_ID     | ERROR    | id lớp ngoài 0..len(ds.classes)-1                                        |
| BOX_ZERO         | ERROR    | w <= 0 hoặc h <= 0                                                       |
| BOX_OUT_OF_IMAGE | ERROR    | mép box vượt [0,1] quá `cfg["label_format"]["overflow_tol"]`; extra={"overflow": mức tràn} |
| DUP_BOX          | ERROR    | cùng lớp với một dòng TRƯỚC ĐÓ và IoU > `dup_box_iou`; báo ở dòng SAU    |
| BOX_TINY         | WARN     | cạnh ngắn của box (px) < `min_box_px`  (cần `ds.image_size(stem)`)       |
| BOX_HUGE         | WARN     | w*h > `max_box_frac`                                                     |

Gợi ý
- Mép trái = x - w/2, mép phải = x + w/2 (xem câu hỏi "dòng YOLO nào lỗi?" trong slide).
- Một dòng hỏng (BAD_FORMAT, BAD_CLASS_ID, BOX_ZERO) thì `continue`, đừng kiểm tiếp hình học của dòng đó.
- Dòng thiếu cột làm script của slide dừng giữa chừng: đây là lý do phải `try/except`.
- `iou_xywh(a, b)` có sẵn trong common.py.
- Ngưỡng nằm trong `cfg["label_format"]` — đừng viết cứng số vào code.
"""
from ..common import ERROR, WARN, Issue, iou_xywh, parse_yolo_line  # noqa: F401


def run(ds, cfg):
    """Kiểm từng dòng độc lập, giữ số dòng gốc và lấy ngưỡng từ cấu hình."""
    opts = cfg["label_format"]
    issues = []
    for path in ds.label_files():
        stem = path.stem
        previous = []
        size = ds.image_size(stem)
        for line, text in ds.read_label_lines(stem) or []:
            def emit(code, severity, message, **extra):
                issues.append(Issue("label_format", severity, code, stem, message, line, extra))
            try:
                box = parse_yolo_line(text)
            except (ValueError, OverflowError) as exc:
                emit("BAD_FORMAT", ERROR, str(exc))
                continue
            cls, x, y, w, h = box
            if not 0 <= cls < len(ds.classes):
                emit("BAD_CLASS_ID", ERROR, f"ID lớp {cls} ngoài danh sách lớp")
                continue
            if w <= 0 or h <= 0:
                emit("BOX_ZERO", ERROR, "Chiều rộng hoặc cao không dương")
                continue
            overflow = max(0, w / 2 - x, h / 2 - y, x + w / 2 - 1, y + h / 2 - 1)
            if overflow > opts["overflow_tol"]:
                emit("BOX_OUT_OF_IMAGE", ERROR, f"Box tràn {overflow:.6f}", overflow=overflow)
            if any(cls == old[0] and iou_xywh(box[1:], old[1:]) > opts["dup_box_iou"] for old in previous):
                emit("DUP_BOX", ERROR, "Box trùng với dòng trước cùng lớp")
            previous.append(box)
            if size and min(w * size[0], h * size[1]) < opts["min_box_px"]:
                emit("BOX_TINY", WARN, "Cạnh ngắn của box dưới ngưỡng pixel")
            if w * h > opts["max_box_frac"]:
                emit("BOX_HUGE", WARN, "Box phủ gần hết ảnh")
    return issues
