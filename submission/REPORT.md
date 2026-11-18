# Báo cáo Day 09 — Trần Anh Văn, 2A202603058

## 1. Kết luận trước
**Hold, chưa phát hành.** Raw có 224 ảnh; intake loại 19/224 (8 trùng byte, 2 gần trùng, 4 rò rỉ val/test, 2 hỏng, 3 nhỏ), giữ và xuất bản nháp **205/224 ảnh**. Sau máy sửa và người duyệt mô phỏng: **0 lỗi bắt buộc**, nhưng còn **38/205 ảnh cảnh báo chưa duyệt = 18,54% ≥ 10%**. Nguồn: `reports/01_intake.csv`, `08_summary.json`, `export/clean_v1/manifest.json`.

## 2. Lỗi và phân việc
Bảng từ `02_error_list_v1.csv`: **issue / ảnh khác nhau**, không cộng cột ảnh vì chồng nhóm. Mẫu số: intake 224 ảnh, QC 205 ảnh. Riêng BAD_CLASS_NAME/CLASS_RARE là file YAML/dataset.

| Mã lỗi | Issue / ảnh hoặc đối tượng | Ai xử lý |
|---|---:|---|
| BAD_CLASS_ID | 6 / 6 | Máy sửa + người xác nhận |
| BAD_CLASS_NAME | 2 / 1 | Máy sửa + người xác nhận |
| BAD_FORMAT | 3 / 3 | Máy sửa + người xác nhận |
| BAD_SIZE | 3 / 3 | Máy loại ảnh |
| BOX_HUGE | 3 / 3 | Người duyệt |
| BOX_OUT_OF_IMAGE | 8 / 8 | Máy sửa + người xác nhận |
| BOX_TINY | 6 / 4 | Người duyệt |
| BOX_ZERO | 4 / 4 | Máy sửa + người xác nhận |
| CLASS_RARE | 4 / 1 | Người duyệt |
| CORRUPT_IMAGE | 2 / 2 | Máy loại ảnh |
| DUP_BOX | 7 / 7 | Máy sửa + người xác nhận |
| DUP_IMAGE_EXACT | 8 / 8 | Máy loại ảnh |
| DUP_IMAGE_NEAR | 2 / 2 | Máy loại ảnh |
| EMPTY_LABEL | 12 / 12 | Người duyệt |
| LEAK_TEST | 4 / 4 | Máy loại ảnh |
| MISSING_LABEL_FILE | 6 / 6 | Người gán |
| POSSIBLE_FALSE_POS | 29 / 27 | Người duyệt |
| POSSIBLE_LOOSE_BOX | 28 / 24 | Người duyệt |
| POSSIBLE_MISSING | 53 / 52 | Người duyệt |
| POSSIBLE_WRONG_CLASS | 18 / 18 | Người duyệt |

Máy bỏ dòng hỏng/ID sai/box rỗng/trùng, cắt box tràn, chuẩn hóa lớp; log trước–sau ở `03_fixes.csv`. Không bịa nhãn cho 6 ảnh thiếu file. QC vòng 1 trên 205 ảnh: 36 lỗi bắt buộc, 153 cảnh báo; 35 thao tác máy, còn 6 lỗi thiếu nhãn.

Hàng đợi 125 ảnh, duyệt 80/125, còn 45 ảnh. `img_0020` đứng đầu: 11,524 điểm do bỏ dòng + nghi thiếu/nhầm lớp; tiếp theo `img_0031/0053/0126/0135`, NEEDS_LABEL 10 điểm/ảnh. Điểm cộng trọng số × confidence; lỗi ngữ nghĩa cần người vì model có thể sai. Đã xem 74 ảnh chứa 94 nghi vấn ngữ nghĩa (51 thiếu, 18 nhầm, 13 thừa, 12 lỏng), không đồng nghĩa 94 lỗi thật (`evidence/review_coverage.json`).

## 3. Calibration hai ngưỡng
Sweep trên 39 ảnh calib, không dùng test để chọn ngưỡng. Các số P/R dưới đây lấy từ `calibration/calibration.json`.

| Tham số | Trước → sau | Precision / Recall trước → sau | Lý do |
|---|---|---|---|
| phash_dist | 2 → 4 | Gần trùng: 1,000/0,500 → 1,000/0,667 | Bắt thêm 1/6 ca, không tăng FP trên calib; chọn đầu vùng plateau 4–14 để hạn chế loại nhầm. |
| conf | 0,25 → 0,60 | Nhầm lớp: 0,556/0,833 → 0,625/0,833; thiếu: 0,500/1,000 → 0,571/1,000 | Giữ recall hai lỗi quan trọng, giảm báo động giả. |

Đánh đổi: recall box lỏng giảm 0,400 → 0,200; FALSE_POS giữ P/R 0,312/1,000 vì dùng fp_conf riêng. Không nâng conf lên 0,8 chỉ để giảm hàng đợi: recall thiếu nhãn sẽ giảm còn 0,750.

**Calib có thể đánh lừa:** pHash 16 có recall gần trùng 0,833 trên calib nhưng gắn cờ 26 ảnh trùng/rò rỉ trên raw, so với 14 ở ngưỡng 4; ngưỡng 20 gắn cờ 134/224 ảnh (chi tiết `evidence/raw_phash_sensitivity.json`), rất dễ loại nhầm. Không có đáp án raw để coi tất cả là đúng. Hai cặp tại ngưỡng 4 đã xem trực tiếp: `img_0076/0042` cùng xe bus ban đêm, `img_0143/0037` cùng cảnh đường phố (ảnh trong `evidence/near_duplicate_pairs.jpg`). Calib thiếu LEAK_TEST và chỉ có 6 ca gần trùng nên không đại diện toàn bộ raw.

## 4. Cửa chặn và điểm mù
Chạy `python -m pipeline.run --budget 0 --reports work/rep_nb --export-dir work/exp_nb`: còn **6 lỗi bắt buộc**, kết luận **Rework**, **exit 20**, không có `work/exp_nb/clean_v1/manifest.json`; log nguyên bản tại `evidence/gate_zero.log`. Bản mặc định Hold xuất bản nháp; lỗi bắt buộc ở ảnh đã duyệt vẫn không được bỏ qua. Test e2e kiểm hai lần chạy có cùng danh sách lỗi và quyết định.

Đã mở 10 ảnh raw (9 ảnh vẽ được, `img_0010` hỏng): xe bus ở `img_0020` bị gán truck, người đứng trái `img_0070` bị gán car, box người ở `img_0050` co thành đường thẳng. Hai điểm mù có bằng chứng: (1) hình học hợp lệ vẫn có thể sai nghĩa như bus/truck; second opinion trên calib vẫn bỏ sót 1/6 nhầm lớp. (2) box lỏng nhẹ khó phát hiện: bỏ sót 4/5 ca calib ở conf đã chọn. Ngoài ra pHash ngưỡng 4 bỏ sót 2/6 ảnh gần trùng. Cần duyệt thủ công và thêm ca biến đổi/nhầm lớp xe để đo lại công cụ.

## 5. Train raw vs clean
Chạy **Colab T4**, Ultralytics 8.4.214, YOLO26n; **20 epoch, batch 16, imgsz 640, seed 0/1** mỗi biến thể; cùng gold_val 40 ảnh chọn checkpoint, test 100 ảnh đo cuối. Bốn JSON do `train_compare.py` sinh, hash manifest/config khớp. Bằng chứng: `evidence/colab_comparison.jpg`, `colab_training.log`.

| biến thể | #ảnh train | số seed | map50 (TB ± độ lệch) | map50_95 (TB ± độ lệch) | precision (TB ± độ lệch) | recall (TB ± độ lệch) |
|---|---|---|---|---|---|---|
| raw | 224 | 2 | 0.726 ± 0.000 | 0.512 ± 0.004 | 0.764 ± 0.061 | 0.649 ± 0.028 |
| clean | 205 | 2 | 0.700 ± 0.030 | 0.486 ± 0.013 | 0.715 ± 0.073 | 0.615 ± 0.017 |

Chênh mAP50 (clean − raw) = **-0.025**.

Bảng sao nguyên `results/comparison.md`: raw materialize 224 nhưng loader loại 11 ảnh/nhãn hỏng, **thực train 213**; clean dùng đủ **205**. Chênh lệch không chỉ do nhãn.

mAP50 theo seed: raw 0,7256/0,7259; clean 0,6788/0,7219. Chênh trung bình **−0,0254** (−2,54 điểm %) nhỏ hơn SD clean **0,0305**, trong khi SD raw là 0,0002. **Chưa có bằng chứng clean tốt hơn; cũng chưa đủ seed để khẳng định suy giảm ổn định.** Không dùng test để chọn lại ngưỡng.

Giả thuyết: (1) 4 ảnh raw rò rỉ val/test có thể làm metric lạc quan; kiểm bằng ablation loại rò rỉ trước train + tập đo độc lập, chưa biết mức thổi phồng. (2) clean còn 38/205 ảnh cảnh báo chưa duyệt và ít ảnh hơn; kiểm bằng duyệt nốt, so cùng ảnh chỉ đổi nhãn, ≥5 seed. Test chỉ 100 ảnh: cần tập đo lớn hơn.

AP50 trung bình car tăng khoảng 0,011, person tăng 0,005; truck giảm khoảng 0,090, bus giảm 0,028. Cần ưu tiên xem nhầm car/truck/bus và phân bố box theo lớp; các quan sát này chưa chứng minh nguyên nhân. Bản clean hiện tại chưa phải chặn trên chất lượng dữ liệu.


## 6. Quyết định và ghi chú AI
Giữ **Hold**. Để Release: người cần duyệt/sửa đủ ảnh còn lại để cảnh báo chưa duyệt dưới 10% (với 205 ảnh, tối đa 20 ảnh), không còn lỗi bắt buộc và chạy lại QC; không thay budget/ngưỡng gate để ép Release. Ngân sách 80 giữ nguyên theo đề.

- Prompt chính: hoàn thiện bài theo rubric; dùng docstring và test, đọc YOLO 5 cột, xuất Issue/log theo giao diện, chỉ sửa bản sao và không đọc đáp án trong checker.
- Kiểm AI: 79 test gốc, 4 test check bổ sung; hai sweep, e2e và thử budget=0; xem nhãn và cặp trùng trên raw. Check thưởng tỉ lệ cạnh dùng đơn vị pixel, chỉ WARN, có test ở `evidence/test_aspect_ratio.py`, không thay cấu hình cố định hay file đề.
- Một lần AI sai: ô #1 Colab vẫn giữ URL mẫu dù file local đã sửa; lần clone đầu lỗi 128. Đã đọc output, thay trực tiếp REPO_URL đúng trong ô #1, kiểm lại nội dung rồi chạy lại trên T4. Người nộp cần đọc và giải thích code trước khi nộp.
