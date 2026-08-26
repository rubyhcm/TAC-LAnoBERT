# Phase 4 Implementation Status

**Date**: 2026-08-26  
**Status**: 🟡 **IN PROGRESS** (E1 ✅ COMPLETE)

---

## Overview

Phase 4 thực hiện 3 experiments chính để đánh giá TAC-LAnoBERT:

- **E1**: Baseline Verification ✅ **COMPLETE**
- **E2**: Main Comparison 🔄 **READY TO RUN**
- **E3**: Early Detection Test 🔄 **READY TO RUN**

---

## ✅ E1: Baseline Verification - COMPLETE

### Status
**✅ PASS** - Baseline reproduction verified within ±2% tolerance

### Results

| Metric | Paper | Reproduced | Diff (%) | Status |
|--------|-------|------------|----------|--------|
| F1-score | 1.000000 | 0.999974 | 0.0026% | ✅ PASS |
| AUROC | 1.000000 | 0.999998 | 0.0002% | ✅ PASS |
| Precision | - | 0.999900 | - | - |
| Recall | - | 1.000000 | - | - |
| FPR | - | 0.000020 | - | Baseline |
| Best Threshold | - | 7.64127 | - | - |

### Artifacts Created
- ✅ `outputs/BGL_lanobert/results/e1_baseline_verification_report.json`

### Exit Criteria
- ✅ F1 diff ≤ 2%: **0.0026%**
- ✅ AUROC diff ≤ 2%: **0.0002%**

**E1 Exit Criteria: MET** ✅

---

## 🔄 E2: Main Comparison - READY TO RUN

### Objective
Huấn luyện TAC-LAnoBERT với full configuration (Time2Vec + Memory Queue + Hybrid Scoring) và so sánh với baseline LAnoBERT.

### Prerequisites
- ✅ Phase 2 baseline complete
- ✅ Phase 3 TAC modules implemented (50/50 unit tests + 8/8 integration tests PASS)
- ✅ Config ready: `configs/bgl_tac_full.yaml`
- ✅ Training scripts ready: `tac_lanobert/train_tac.py`

### Pipeline Steps

1. **Data Split** (Chronological)
   - Train: 80% (chronologically first)
   - Test: 20% (chronologically last)
   
2. **Preprocessing**
   - Extract timestamps from raw logs
   - Compute delta_t (time gaps between consecutive events)
   - Normalize log templates
   
3. **Tokenizer Training**
   - WordPiece tokenizer (vocab_size=1000)
   - Parser-free approach
   
4. **Model Training** (⚠️ ~3-4 hours on Kaggle T4 x2)
   - BERT Base (12 layers, 768 hidden, 12 heads)
   - Time2Vec embedding (15 periodic components)
   - MLM objective (20% masking)
   - 2 epochs, batch_size=32, gradient_accumulation=2
   
5. **Inference** (TAC Hybrid Scoring)
   - Extract [CLS] vector for each window
   - Update Memory Queue (FIFO, capacity=128)
   - Compute MLM Loss (per-token cross-entropy)
   - Compute Mahalanobis Distance (Ledoit-Wolf shrinkage)
   - Hybrid Score: α·MLM + (1-α)·Mahalanobis (α=0.5)
   
6. **Comparison**
   - Compare TAC vs Baseline
   - Metrics: F1, AUROC, FPR, PR-AUC
   - Hypothesis H1: FPR reduction ≥15%

### Expected Outputs
- `outputs/BGL_tac/model/final/` (model checkpoint)
- `outputs/BGL_tac/tokenizer/` (tokenizer)
- `outputs/BGL_tac/results/scores_tac_mlm_error.npy`
- `outputs/BGL_tac/results/scores_tac_mahalanobis.npy`
- `outputs/BGL_tac/results/scores_tac_hybrid.npy`
- `outputs/BGL_tac/results/e2_main_comparison_report.json`

### How to Run

**Option 1: Full pipeline (recommended)**
```bash
python -m experiments.run_main --config configs/bgl_tac_full.yaml
```

**Option 2: Skip training** (if model already trained from Phase 3)
```bash
python -m experiments.run_main --config configs/bgl_tac_full.yaml --skip-training
```

**Note**: Model was trained in Phase 3, but inference scores were not generated. Need to run inference step.

### Success Criteria (H1)
- ✅ FPR Δ ≤ 0% (không tăng so với baseline: 0.000020)
- 🎯 **Target**: FPR reduction ≥15% → FPR ≤ 0.000017
- ✅ F1/AUROC maintained (không giảm >2%)

---

## 🔄 E3: Early Detection Test - READY TO RUN

### Objective
Đo **Detection Lead Time (DLT)** và **Early Warning Rate (EWR)** để đánh giá khả năng cảnh báo sớm.

### Prerequisites
- ✅ E2 complete (scores generated)
- ✅ Test set with timestamps
- ✅ Failure labels

### Metrics

#### 1. Detection Lead Time (DLT)
```
DLT = t_failure - t_first_alert (seconds/minutes)

Example:
  - Alert at 10:15:00
  - Failure at 10:20:00
  → DLT = 5 minutes (300 seconds) ✅ Early warning

  - Alert at 10:25:00
  - Failure at 10:20:00
  → DLT = 0 ⚠️ Reactive detection (no early warning)
```

**Statistics**:
- Mean DLT
- Median DLT
- Distribution: 1min, 5min, 10min, 30min, 1h, 6h

#### 2. Early Warning Rate (EWR)
```
EWR = (# failures with DLT ≥ 5 minutes) / (# total failures) × 100%
```

**Target**: EWR ≥ 30%

### How to Run

Run for all score types:
```bash
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type mlm
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type mahalanobis
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type hybrid
```

### Expected Outputs
- `outputs/BGL_tac/results/e3_early_detection_mlm_report.json`
- `outputs/BGL_tac/results/e3_early_detection_mahalanobis_report.json`
- `outputs/BGL_tac/results/e3_early_detection_hybrid_report.json`

### Success Criteria (H2)
- ✅ Mean DLT > 0 (có khả năng cảnh báo sớm)
- 🎯 **Target**: EWR ≥ 30% (ít nhất 30% sự cố được cảnh báo sớm ≥5 phút)
- 🎯 **Target**: Effect size Cohen's d ≥ 0.5 (significant improvement)

---

## Phase 4 Exit Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| E1: Baseline verified | ✅ PASS | F1 diff: 0.0026%, AUROC diff: 0.0002% |
| E2: TAC trained | ⏳ READY | Model trained in Phase 3, need inference |
| E2: FPR ≈ baseline | ⏳ PENDING | Need E2 results |
| E3: DLT > 0 | ⏳ PENDING | Need E3 results |
| E3: EWR measured | ⏳ PENDING | Need E3 results |

**Phase 4 Status**: 🟡 **E1 COMPLETE, E2/E3 READY TO RUN**

---

## Quick Start: Run All Experiments

```bash
# Option 1: Interactive (recommended for first run)
bash scripts/run_phase4.sh

# Option 2: Manual step-by-step
python -m experiments.run_baseline      # E1 (already complete)
python -m experiments.run_main          # E2 (~3-4h on Kaggle T4 x2)
python -m experiments.run_early_detection --score-type hybrid  # E3

# Check status
python scripts/check_phase4_status.py
```

---

## Troubleshooting

### E2: Out of Memory (OOM)

**Giải pháp 1**: Giảm batch size
```yaml
# configs/bgl_tac_full.yaml
train:
  per_device_train_batch_size: 16  # Giảm từ 32
  gradient_accumulation_steps: 4    # Tăng từ 2 (giữ effective batch = 64)
```

**Giải pháp 2**: Giảm queue capacity
```yaml
tac:
  memory:
    queue_capacity: 64  # Giảm từ 128
```

### E3: DLT = 0 (No Early Warning)

**Nguyên nhân**:
1. Threshold quá cao → giảm threshold
2. Model chưa học pattern cảnh báo sớm → cần train lâu hơn
3. Timestamps không hợp lệ → verify chronological split

**Debug**:
```python
import numpy as np
scores = np.load("outputs/BGL_tac/results/scores_tac_hybrid.npy")
print(f"Mean: {scores.mean():.4f}, Std: {scores.std():.4f}")
print(f"95th: {np.percentile(scores, 95):.4f}")
print(f"99th: {np.percentile(scores, 99):.4f}")
```

---

## Current Status Summary

```
Phase 4 Progress: [██████████░░░░░░░░░░] 33% (1/3 complete)

✅ E1: Baseline Verification     COMPLETE
🔄 E2: Main Comparison           READY (model trained, need inference)
🔄 E3: Early Detection Test      READY (waiting for E2)
```

### Next Steps

1. **Run E2 Inference** (if model already trained in Phase 3):
   ```bash
   python -m tac_lanobert.inference_tac --config configs/bgl_tac_full.yaml
   ```

2. **Or Run Full E2 Pipeline** (if starting fresh):
   ```bash
   python -m experiments.run_main --config configs/bgl_tac_full.yaml
   ```

3. **Run E3** (after E2 complete):
   ```bash
   for score in mlm mahalanobis hybrid; do
       python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type $score
   done
   ```

4. **Check Status**:
   ```bash
   python scripts/check_phase4_status.py
   ```

---

## References

- **Plan.md**: Full Phase 1-9 roadmap
- **PHASE2_COMPLETION_BGL.md**: Baseline results (F1: 0.999974, FPR: 0.000020)
- **PHASE3_COMPLETION.md**: TAC modules implementation (50/50 tests PASS)
- **PHASE4_GUIDE.md**: Detailed E1/E2/E3 usage guide

---

**Last Updated**: 2026-08-26 12:10 ICT  
**Next Milestone**: Complete E2 (Main Comparison) → E3 (Early Detection)
