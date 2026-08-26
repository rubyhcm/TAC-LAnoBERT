# Phase 4 Checklist

## E1: Baseline Verification ✅

- [x] Load Phase 2 baseline report
- [x] Extract metrics (F1, AUROC, FPR)
- [x] Compare with paper (LAnoBERT ASC 2023)
- [x] Check tolerance: F1/AUROC diff ≤ 2%
- [x] Generate E1 report
- [x] **Result**: F1 diff 0.0026%, AUROC diff 0.0002% → **PASS**

**Artifacts**:
- ✅ `outputs/BGL_lanobert/results/e1_baseline_verification_report.json`

---

## E2: Main Comparison 🔄

### Prerequisites
- [x] Phase 3 complete (TAC modules implemented)
- [x] Config ready: `configs/bgl_tac_full.yaml`
- [x] Model trained (Phase 3): `outputs/BGL_tac/model/final/`

### Tasks

#### Step 1: Data Pipeline
- [ ] Split BGL chronologically (80/20)
- [ ] Preprocess train set (extract timestamps)
- [ ] Preprocess test set (extract timestamps)
- [ ] Train WordPiece tokenizer

#### Step 2: Model Training (⚠️ 3-4 hours on Kaggle T4 x2)
- [ ] Train TAC-LAnoBERT with Time2Vec
- [ ] Verify Time2Vec gradients flow
- [ ] Save model checkpoint
- [ ] Log training metrics

#### Step 3: Inference (TAC Hybrid Scoring)
- [ ] Load trained model
- [ ] Initialize Memory Queue (capacity=128)
- [ ] Process test set sequentially:
  - [ ] Extract [CLS] vector
  - [ ] Push to Memory Queue
  - [ ] Compute MLM Loss
  - [ ] Compute Mahalanobis Distance
  - [ ] Compute Hybrid Score: α·MLM + (1-α)·Mahalanobis
- [ ] Save scores:
  - [ ] `scores_tac_mlm_error.npy`
  - [ ] `scores_tac_mahalanobis.npy`
  - [ ] `scores_tac_hybrid.npy`

#### Step 4: Comparison
- [ ] Load baseline results (E1)
- [ ] Compute TAC metrics (F1, AUROC, FPR, PR-AUC)
- [ ] Find best threshold (F1-optimal)
- [ ] Compute improvements (Δ%)
- [ ] Check H1: FPR reduction ≥15%?
- [ ] Generate E2 report

### Success Criteria
- [ ] FPR ≤ baseline (0.000020)
- [ ] F1 maintained (≥0.98, diff ≤2%)
- [ ] AUROC maintained (≥0.995)
- [ ] **Target H1**: FPR reduction ≥15% → FPR ≤ 0.000017

**Run Command**:
```bash
python -m experiments.run_main --config configs/bgl_tac_full.yaml
```

**Artifacts**:
- [ ] `outputs/BGL_tac/model/final/` (model)
- [ ] `outputs/BGL_tac/tokenizer/` (tokenizer)
- [ ] `outputs/BGL_tac/results/scores_tac_*.npy` (3 files)
- [ ] `outputs/BGL_tac/results/e2_main_comparison_report.json`

---

## E3: Early Detection Test 🔄

### Prerequisites
- [ ] E2 complete (scores generated)
- [ ] Test set with timestamps
- [ ] Failure labels available

### Tasks

#### For Each Score Type: MLM, Mahalanobis, Hybrid

- [ ] Load anomaly scores
- [ ] Load labels (0=normal, 1=anomaly)
- [ ] Load timestamps (from raw logs)
- [ ] Determine threshold (from E2 best_threshold)

#### DLT Computation
- [ ] For each failure:
  - [ ] Get failure timestamp `t_fail`
  - [ ] Search backwards for first alert (score ≥ threshold)
  - [ ] If found: DLT = t_fail - t_alert (seconds)
  - [ ] If not found: DLT = 0 (reactive detection)

#### Statistics
- [ ] Compute Mean DLT (seconds/minutes)
- [ ] Compute Median DLT
- [ ] Compute EWR: % failures with DLT ≥ 5 minutes
- [ ] DLT distribution:
  - [ ] ≥1 minute: count, %
  - [ ] ≥5 minutes: count, %
  - [ ] ≥10 minutes: count, %
  - [ ] ≥30 minutes: count, %
  - [ ] ≥1 hour: count, %
  - [ ] ≥6 hours: count, %

#### Report Generation
- [ ] Save E3 report for MLM score
- [ ] Save E3 report for Mahalanobis score
- [ ] Save E3 report for Hybrid score

### Success Criteria
- [ ] Mean DLT > 0 (có cảnh báo sớm)
- [ ] **Target**: EWR ≥ 30% (at least 30% failures warned ≥5 min early)
- [ ] **Target H2**: Effect size Cohen's d ≥ 0.5

**Run Commands**:
```bash
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type mlm
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type mahalanobis
python -m experiments.run_early_detection --config configs/bgl_tac_full.yaml --score-type hybrid
```

**Artifacts**:
- [ ] `outputs/BGL_tac/results/e3_early_detection_mlm_report.json`
- [ ] `outputs/BGL_tac/results/e3_early_detection_mahalanobis_report.json`
- [ ] `outputs/BGL_tac/results/e3_early_detection_hybrid_report.json`

---

## Phase 4 Exit Criteria

| Criterion | Status | Value |
|-----------|--------|-------|
| E1: Baseline verified (F1 diff ≤2%) | ✅ PASS | 0.0026% |
| E1: Baseline verified (AUROC diff ≤2%) | ✅ PASS | 0.0002% |
| E2: TAC trained | ⏳ PENDING | - |
| E2: FPR ≈ baseline | ⏳ PENDING | Target: ≤0.000020 |
| E2: F1 maintained | ⏳ PENDING | Target: ≥0.98 |
| E3: DLT > 0 | ⏳ PENDING | Target: >0 |
| E3: EWR ≥ 30% | ⏳ PENDING | Target: ≥30% |
| H1: FPR reduction ≥15% | ⏳ PENDING | Target: ≤0.000017 |
| H2: DLT effect size d ≥ 0.5 | ⏳ PENDING | Target: Cohen's d ≥0.5 |

---

## Quick Commands

```bash
# Check current status
python scripts/check_phase4_status.py

# Run all experiments (interactive)
bash scripts/run_phase4.sh

# Or step by step:
python -m experiments.run_baseline      # E1 ✅
python -m experiments.run_main          # E2 🔄
python -m experiments.run_early_detection --score-type hybrid  # E3 🔄
```

---

## Estimated Time

- **E1**: ~5 seconds (just verification)
- **E2**: ~3-4 hours (2 epochs training on BGL with Kaggle T4 x2)
- **E3**: ~5 minutes (DLT computation on test set)

**Total**: ~3-4 hours (dominated by E2 training)

---

## Notes

### Model Training Optimization
- Use `fp16=true` (not bf16) for T4 GPU
- `gradient_accumulation_steps=2` → effective batch = 64
- `attn_implementation: sdpa` (Scaled Dot-Product Attention, faster)
- Save checkpoint every 5000 steps

### Memory Queue Optimization
- Welford's algorithm: O(1) update, no full recomputation
- Ledoit-Wolf shrinkage: prevents singular covariance matrix
- FIFO queue: automatic old sample eviction

### Anti-Leakage Verification
- Chronological split enforced
- No shuffle on test set
- Timestamps monotonically increasing
- Memory Queue only uses past samples (t ≤ t_current)

---

**Last Updated**: 2026-08-26 12:15 ICT  
**Progress**: [██████████░░░░░░░░░░] 33% (E1 complete, E2/E3 ready)
