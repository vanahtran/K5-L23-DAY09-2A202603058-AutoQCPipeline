"""BƯỚC 4 — Cửa chặn: quyết định Release / Hold / Rework.   ★

Test:  pytest tests/test_gate.py -q

Cây quyết định Day 07 (slide Day 09: "Lỗi bắt buộc chặn pipeline; lỗi cảnh báo chuyển người xem"):

  còn ≥ 1 lỗi bắt buộc (severity ERROR)                          -> "Rework"
  không còn lỗi bắt buộc, nhưng tỉ lệ ẢNH còn cảnh báo
      >= cfg["gate"]["warn_ratio_hold"]                          -> "Hold"
  còn lại                                                        -> "Release"

Tỉ lệ cảnh báo = (số ẢNH khác nhau có ≥ 1 cảnh báo) / (tổng số ảnh).  Chú ý:
- chỉ đếm issue có `image` nằm trong `image_stems` (bỏ "<dataset>", "data.yaml");
- bỏ qua ảnh nằm trong `reviewed` (người đã xem, cảnh báo của ảnh đó coi như đã xử lý) — nhưng LỖI BẮT BUỘC thì không bao giờ được bỏ qua;
- mẫu số là số ảnh, không phải số issue.

Trả về dict: decision, n_errors, n_warn_images, n_images, warn_ratio (làm tròn 4 chữ số), reasons (list[str], giải thích bằng tiếng Việt, có số liệu).
"""
from ..common import ERROR, WARN  # noqa: F401


def decide(issues, image_stems, cfg, reviewed=frozenset()):
    """Lỗi bắt buộc luôn chặn; cảnh báo đếm theo ảnh chưa được duyệt."""
    stems = set(image_stems)
    errors = sum(i.severity == ERROR for i in issues)
    warnings = {i.image for i in issues if i.severity == WARN and i.image in stems and i.image not in reviewed}
    ratio = len(warnings) / len(stems) if stems else 0.0
    limit = cfg["gate"]["warn_ratio_hold"]
    if errors:
        decision, reason = "Rework", f"Còn {errors} lỗi bắt buộc; cần sửa trước khi xuất."
    elif ratio >= limit:
        decision, reason = "Hold", f"Còn {len(warnings)}/{len(stems)} ảnh cảnh báo chưa duyệt ({ratio:.2%}), đạt ngưỡng {limit:.2%}."
    else:
        decision, reason = "Release", f"Không còn lỗi bắt buộc; {len(warnings)}/{len(stems)} ảnh cảnh báo chưa duyệt ({ratio:.2%}), dưới ngưỡng {limit:.2%}."
    return dict(decision=decision, n_errors=errors, n_warn_images=len(warnings), n_images=len(stems), warn_ratio=round(ratio, 4), reasons=[reason])
