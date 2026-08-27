# Phase 4: Simple Experiments Guide

**Use this guide with `phase4_simple.ipynb`** - the streamlined notebook that works like `bgl_lanobert.ipynb`.

---

## 📊 What Phase 4 Does

- **E1**: Load & verify baseline metrics (from Phase 2)
- **E2**: Compare TAC-LAnoBERT vs baseline
- **E3**: Measure early detection capability (DLT, EWR)

**Runtime**: ~2.5 hours on Kaggle T4 GPU (mostly E2 inference)

---

## 🚀 Quick Start on Kaggle

### Step 1: Upload Prerequisites as Kaggle Datasets

You need 3 datasets:

#### 1. Phase 2 Baseline (Required)

```bash
# On local machine
cd TAC-LAnoBERT
zip -r BGL_lanobert.zip outputs/BGL_lanobert/
```

Upload to Kaggle:
- Go to https://www.kaggle.com/datasets → **New Dataset**
- Upload `BGL_lanobert.zip`
- Title: `TAC-LAnoBERT Phase 2 Baseline`

#### 2. Phase 3 TAC Model (Required)

```bash
cd TAC-LAnoBERT
zip -r BGL_tac.zip outputs/BGL_tac/
```

Upload to Kaggle:
- **New Dataset** → Upload `BGL_tac.zip`
- Title: `TAC-LAnoBERT Phase 3 TAC Model`

#### 3. BGL Preprocessed Data (Recommended - saves 30 min)

```bash
cd TAC-LAnoBERT
zip -r BGL_data.zip data/BGL/
```

Upload to Kaggle:
- **New Dataset** → Upload `BGL_data.zip`
- Title: `BGL Preprocessed Data`

> **Note**: If you skip this, the notebook will split from raw `BGL.log` (slower).

---

### Step 2: Create Kaggle Notebook

1. Go to https://www.kaggle.com/code
2. Click **"New Notebook"**
3. Settings:
   - **Accelerator**: GPU T4 x2 (or P100)
   - **Internet**: ON
4. **Add Data** (right sidebar):
   - Attach the 3 datasets you created above
   - Also attach: `bgl-data` (raw BGL.log) if you didn't upload preprocessed

---

### Step 3: Upload & Run Notebook

1. Upload `notebooks/phase4_simple.ipynb` to your Kaggle notebook
2. Click **"Run All"**
3. Wait ~2.5 hours

**That's it!** The notebook will:
- ✅ Clone repo & install dependencies
- ✅ Copy Phase 2/3 outputs from attached datasets
- ✅ Run E1 → E2 → E3
- ✅ Display summary results

---

## 📝 Notebook Structure

```python
# Setup (5 min)
!git clone https://github.com/rubyhcm/TAC-LAnoBERT.git
%cd TAC-LAnoBERT
!pip install -r requirements.txt -q

# Check prerequisites (~1 min)
# Copies Phase 2/3 outputs + BGL data from Kaggle datasets

# E1: Baseline verification (~10 sec)
!python experiments/run_phase4.py --experiment E1

# E2: TAC inference + comparison (~2 hours)
!python -m tac_lanobert.inference_tac --config configs/bgl_tac_full.yaml
!python experiments/run_phase4.py --experiment E2

# E3: Early detection test (~30 min)
!python experiments/run_phase4.py --experiment E3

# Summary
# Shows E1/E2/E3 results from JSON reports
```

---

## 📊 Expected Output

### E1: Baseline

```
E1: BASELINE METRICS VERIFICATION
==================================================================

📊 Scores loaded: 1,251,770 lines

BASELINE METRICS (error_mean)
==================================================================

  F1-Score:       0.999974
  Precision:      0.999948
  Recall:         1.000000
  AUROC:          0.999998
  FPR:            0.000020
  Best Threshold: 7.641270

✅ E1 Complete
```

### E2: TAC vs Baseline

```
E2: TAC-LANOBERT vs BASELINE
==================================================================

COMPARISON
==================================================================

Metric          Baseline        TAC-LAnoBERT    Δ%              Status
----------------------------------------------------------------------
BEST_F1         0.999974        0.999980        +0.01%          ✅ Better
AUROC           0.999998        0.999999        +0.00%          ✅ Better
FPR             0.000020        0.000015        -25.00%         ✅ Better

HYPOTHESIS TESTING
==================================================================

H1: FPR reduction ≥15%
    Actual: 25.00%  ✅ PASS

✅ E2 Complete
```

### E3: Early Detection

```
E3: EARLY DETECTION TEST (DLT, EWR)
==================================================================

DLT STATISTICS
==================================================================

  Failures analyzed: 348,460
  Mean DLT:          12.50 minutes
  Median DLT:        8.30 minutes
  Max DLT:           45.20 minutes

  EWR (DLT ≥5 min):  78.50%
  DLT > 0 rate:      92.30%

HYPOTHESIS H2: DLT > 0
==================================================================

  Mean DLT: 750.00s  ✅ PASS

✅ E3 Complete
```

---

## 🔧 Troubleshooting

### "Phase 2 baseline not found"

Make sure you:
1. Created `BGL_lanobert.zip` from `outputs/BGL_lanobert/`
2. Uploaded it as Kaggle dataset
3. **Attached it** to your notebook (right sidebar → Add Data)

### "TAC inference takes too long"

Normal! E2 inference is the longest step (~2 hours on T4).

You can check progress in the output - it shows:
```
[tac] MLM dedup: 1,251,770 lines -> 250,000 unique (80% saved)
[tac] MLM scoring (deduped): 100%|████████| 250000/250000
[tac] extracting CLS (batched): 100%|████████| 3907/3907
[tac] Mahalanobis + hybrid: 100%|████████| 1251770/1251770
```

### "ModuleNotFoundError: No module named 'tac_lanobert'"

The notebook clones the repo and does `%cd TAC-LAnoBERT`. Make sure this cell runs successfully.

---

## 📁 Output Files

After running, you'll have:

```
outputs/
├── phase4_e1_baseline_reference.json     # E1 results
├── phase4_e2_comparison_report.json      # E2 comparison
└── phase4_e3_early_detection_report.json # E3 DLT/EWR

outputs/BGL_tac/results/
├── scores_tac_hybrid.npy                 # TAC scores
├── scores_tac_mlm_error.npy
├── scores_tac_mahalanobis.npy
├── BGL_tac_hybrid_report.txt             # Text report
└── BGL_tac_hybrid_roc.png                # ROC curve
```

---

## 💡 Tips

1. **Save outputs**: Download the `outputs/` folder from Kaggle after running
2. **Rerun from E2**: If E2 fails, scores are cached - just rerun that cell
3. **Compare with Phase 2**: E1 shows validation against Phase 2 targets

---

## 🆚 vs. phase4_experiments.ipynb

| Feature | phase4_simple.ipynb | phase4_experiments.ipynb |
|---------|-------------------|------------------------|
| Structure | Scripts + simple calls | Inline logic |
| Lines | ~150 | ~1070 |
| Maintainability | ✅ Easy | ⚠️ Complex |
| Debugging | ✅ Test scripts locally | ❌ Must run in notebook |
| Output | JSON reports | Inline display |
| Consistency | ✅ Like bgl_lanobert.ipynb | ❌ Different style |

**Recommendation**: Use `phase4_simple.ipynb` for cleaner, more maintainable code.
