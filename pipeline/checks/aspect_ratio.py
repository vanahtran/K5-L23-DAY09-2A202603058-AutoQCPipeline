"""Check bổ sung: box có tỉ lệ cạnh bất thường, chỉ cảnh báo để người xem."""
from ..common import WARN, Issue, parse_yolo_line


def run(ds, cfg):
    limit = cfg["aspect_ratio"]["max_ratio"]
    if limit <= 1:
        raise ValueError("max_ratio phải lớn hơn 1")
    issues = []
    for image in ds.image_files():
        stem = image.stem
        size = ds.image_size(stem)
        if size is None:
            continue
        for line, text in ds.read_label_lines(stem) or []:
            try:
                cls, _, _, w, h = parse_yolo_line(text)
            except (ValueError, OverflowError):
                continue
            if not 0 <= cls < len(ds.classes) or w <= 0 or h <= 0:
                continue
            width, height = w * size[0], h * size[1]
            ratio = max(width / height, height / width)
            if ratio > limit:
                issues.append(Issue("aspect_ratio", WARN, "BOX_ASPECT_EXTREME", stem,
                                    f"Tỉ lệ cạnh {ratio:.2f} > {limit}; cần người kiểm", line,
                                    {"ratio": ratio, "threshold": limit}))
    return issues
