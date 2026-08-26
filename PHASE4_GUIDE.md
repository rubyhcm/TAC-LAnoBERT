# Phase 4: Main Experiments

## Mục Tiêu

Phase 4 thực hiện 3 experiments chính để đánh giá TAC-LAnoBERT:

- **E1**: Baseline Verification — Xác nhận lại kết quả LAnoBERT từ Phase 2
- **E2**: Main Comparison — Huấn luyện TAC-LAnoBERT và so sánh với baseline
- **E3**: Early Detection Test — Đo DLT (Detection Lead Time) và EWR (Early Warning Rate)

## Exit Criteria

✅ Phase 4 hoàn thành khi:
- DLT > 0 (có khả năng cảnh báo sớm)
- FPR duy trì tiệm cận 0 (không tăng so với baseline)

## Quick Start

### Option 1: Chạy Toàn Bộ Phase 4 (Recommended)

```bash
bash scripts/run_phase4.sh
```

**Lưu ý**: E2 sẽ mất 3-4 giờ trên Kaggle T4 x2 (2 epochs training). Script sẽ hỏi xác nhận trước khi bắt đầu training.

### Option 2: Chạy Từng Experiment Riêng Lẻ

#### E1: Baseline Verification

```bash
python -m experiments.run_baseline --config configs/bgl.yaml
```

**Output**: `outputs/BGL_lanobert/results/e1_baseline_verification_report.json`

**Kiểm tra**:
- F1 diff ≤ 2% so với paper (1.000)
- AUROC diff ≤ 2% so với paper (1.000)

#### E2: Main Comparison

```bash
python -m experiments.run_main --config configs/bgl_tac_full.yaml
```

**Output**: `outputs/BGL_tac/results/e2_main_comparison_report.json`

**Pipeline steps**:
1. Split data (chronological)
2. Preprocess train/test (extract timestamps)
3. Train tokenizer
4. Train TAC-LAnoBERT model (2 epochs, ~3-4h)
5. Run inference (Hybrid Scoring: α·MLM + (1-α)·Mahalanobis)
6. Compare with baseline

**Metrics**:
- F1, AUROC, PR-AUC (classification)
- FPR (false positive rate)
- Mahalanobis distance statistics

**Skip training** (nếu đã train trước đó):
```bash
python -m experiments.run_main --config configs/bgl_tac_full.yaml --skip-training
```

#### E3: Early Detection Test

```bash
# Test với tất cả score types
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type mlm
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type mahalanobis
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type hybrid
```

**Output**: 
- `outputs/BGL_tac/results/e3_early_detection_mlm_report.json`
- `outputs/BGL_tac/results/e3_early_detection_mahalanobis_report.json`
- `outputs/BGL_tac/results/e3_early_detection_hybrid_report.json`

**Metrics**:
- **DLT**: Detection Lead Time (seconds/minutes) — thời gian cảnh báo trước khi sự cố xảy ra
- **EWR**: Early Warning Rate (%) — phần trăm sự cố được cảnh báo sớm ≥5 phút
- DLT distribution (1min, 5min, 10min, 30min, 1h, 6h)

**DLT Computation**:
```
DLT = t_failure - t_first_alert

Ví dụ:
  - Alert at 10:15:00
  - Failure at 10:20:00
  → DLT = 5 minutes (300 seconds)
  
  - Alert at 10:25:00
  - Failure at 10:20:00
  → DLT = 0 (reactive detection, no early warning)
```

## Results Interpretation

### E2: Main Comparison

**Success indicators**:
- ✅ FPR Δ ≤ 0% (không tăng so với baseline)
- ✅ F1/AUROC maintained (không giảm >2%)
- ✅ Mahalanobis distance separates normal vs anomaly

**Target**: FPR reduction ≥15% (H1 hypothesis)

### E3: Early Detection

**Success indicators**:
- ✅ Mean DLT > 0 (có cảnh báo sớm)
- ✅ EWR ≥ 30% (ít nhất 30% sự cố được cảnh báo sớm ≥5 phút)
- ✅ Median DLT > 1 minute

**Baseline**: LAnoBERT là reactive (DLT ≈ 0 vì chỉ phát hiện khi log bất thường xuất hiện)

## Troubleshooting

### E1 Failed: Baseline not found

**Giải pháp**:
```bash
bash scripts/run_pipeline.sh configs/bgl.yaml
```

Hoặc xem hướng dẫn trong `PHASE2_COMPLETION_BGL.md`.

### E2 OOM (Out of Memory)

**Giải pháp**:
1. Giảm batch size trong `configs/bgl_tac_full.yaml`:
   ```yaml
   train:
     per_device_train_batch_size: 16  # Giảm từ 32
     gradient_accumulation_steps: 4    # Tăng từ 2
   ```

2. Hoặc giảm queue capacity:
   ```yaml
   tac:
     memory:
       queue_capacity: 64  # Giảm từ 128
   ```

### E2 Training Too Slow

**Thời gian ước tính** (BGL, 2 epochs):
- Kaggle T4 x2 (16GB): ~3-4 giờ
- Kaggle P100 (16GB): ~2-3 giờ
- Local CPU: không khả thi (>24h)

**Tối ưu**:
1. Sử dụng Kaggle GPU (2 GPUs)
2. Đảm bảo `fp16: true` trong config
3. Kiểm tra GPU utilization: `nvidia-smi`

### E3 Negative DLT

**Nguyên nhân**: Timestamps không monotonic (vi phạm chronological split)

**Kiểm tra**:
```bash
python -m tests.test_data_leakage
```

### E3 DLT = 0

**Nguyên nhân**: 
- Threshold quá cao → không có alert trước failure
- Model chưa học được pattern cảnh báo sớm

**Kiểm tra**:
1. Xem distribution của scores:
   ```python
   import numpy as np
   scores = np.load("outputs/BGL_tac/results/scores_tac_hybrid.npy")
   print(f"Mean: {scores.mean()}, Std: {scores.std()}")
   print(f"99th percentile: {np.percentile(scores, 99)}")
   ```

2. Thử giảm threshold:
   ```bash
   python -m experiments.run_early_detection \
       --config configs/bgl_tac_full.yaml \
       --score-type hybrid
   # Sau đó edit report để thử threshold khác
   ```

## Next Steps

Sau khi Phase 4 hoàn thành:

1. **Review E2 results**: So sánh FPR, F1 với baseline
2. **Review E3 results**: Kiểm tra DLT distribution, EWR
3. **Verify exit criteria**:
   - ✅ DLT > 0?
   - ✅ FPR ≈ baseline?

4. **Proceed to Phase 5**: Ablation Study (E4-E7)
   ```bash
   bash scripts/run_phase5.sh
   ```

## File Structure

```
experiments/
├── run_baseline.py           # E1: Baseline verification
├── run_main.py               # E2: Main comparison (train + compare)
└── run_early_detection.py    # E3: DLT & EWR analysis

scripts/
└── run_phase4.sh             # Master runner (E1 → E2 → E3)

outputs/
├── BGL_lanobert/
│   └── results/
│       └── e1_baseline_verification_report.json
└── BGL_tac/
    └── results/
        ├── e2_main_comparison_report.json
        ├── e3_early_detection_mlm_report.json
        ├── e3_early_detection_mahalanobis_report.json
        ├── e3_early_detection_hybrid_report.json
        ├── scores_tac_mlm_error.npy
        ├── scores_tac_mahalanobis.npy
        └── scores_tac_hybrid.npy
```

## References

- **Plan.md**: Toàn bộ kế hoạch Phase 1-9
- **PHASE2_COMPLETION_BGL.md**: Baseline results (F1: 0.999974, FPR: 0.000020)
- **PHASE3_COMPLETION.md**: TAC modules (Time2Vec, Memory Queue, Hybrid Scoring)
