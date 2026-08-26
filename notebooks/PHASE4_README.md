# Phase 4 Experiments Notebook — Kaggle Setup Guide

## 📋 Prerequisites

Before running the notebook, ensure you have:

1. ✅ **Phase 2 Baseline** trained → `outputs/BGL_lanobert/`
2. ✅ **Phase 3 TAC Model** trained → `outputs/BGL_tac/`
3. ✅ **BGL Dataset** (raw log file)

---

## 🚀 Kaggle Setup Instructions

### Step 1: Upload Phase 2 & Phase 3 Outputs as Kaggle Datasets

Since Kaggle notebooks can't access local files, you need to upload your trained models:

#### 1.1. Create Phase 2 Dataset

```bash
# On your local machine
cd TAC-LAnoBERT
zip -r BGL_lanobert.zip outputs/BGL_lanobert/
```

Then:
1. Go to https://www.kaggle.com/datasets
2. Click **"New Dataset"**
3. Upload `BGL_lanobert.zip`
4. Title: `TAC-LAnoBERT Phase 2 Baseline`
5. Click **"Create"**

#### 1.2. Create Phase 3 Dataset

```bash
# On your local machine
cd TAC-LAnoBERT
zip -r BGL_tac.zip outputs/BGL_tac/
```

Then:
1. Go to https://www.kaggle.com/datasets
2. Click **"New Dataset"**
3. Upload `BGL_tac.zip`
4. Title: `TAC-LAnoBERT Phase 3 TAC Model`
5. Click **"Create"**

> **Note**: You can combine both into one dataset if preferred.

---

### Step 2: Upload Notebook to Kaggle

1. Go to https://www.kaggle.com/code
2. Click **"New Notebook"**
3. Click **"File" → "Upload Notebook"**
4. Select `notebooks/phase4_experiments.ipynb`

---

### Step 3: Attach Datasets

In your Kaggle notebook:

1. Click **"Add Data"** (right sidebar)
2. Search and add:
   - Your uploaded Phase 2 dataset (`BGL_lanobert`)
   - Your uploaded Phase 3 dataset (`BGL_tac`)
   - BGL raw log dataset (search "BGL log" in Kaggle datasets)

---

### Step 4: Enable GPU & Internet

1. **GPU**: Settings → Accelerator → **GPU T4 x2** (or P100)
2. **Internet**: Settings → Internet → **ON** (to clone repo)

---

### Step 5: Run Notebook

Click **"Run All"** or run cells sequentially.

The notebook will:
1. ✅ Clone TAC-LAnoBERT repo
2. ✅ Copy Phase 2/3 outputs from `/kaggle/input/` to `outputs/`
3. ✅ Verify all artifacts
4. ✅ Run TAC inference (Memory Queue + Hybrid Scoring)
5. ✅ Compare metrics (E1, E2)
6. ✅ Calculate DLT & EWR (E3)
7. ✅ Generate JSON reports

---

## ⏱️ Expected Runtime

- **Total**: ~3 hours on T4 GPU
  - E1 (Baseline verification): ~5 min
  - E2 (TAC inference): ~2h
  - E3 (DLT analysis): ~1h

---

## 📊 Outputs Generated

After running, you'll find these reports in `outputs/`:

```
outputs/
├── phase4_e1_baseline_reference.json      # E1: Baseline metrics
├── phase4_e2_comparison_report.json       # E2: TAC vs Baseline
├── phase4_e3_early_detection_report.json  # E3: DLT, EWR
└── phase4_completion_report.json          # Final summary
```

### Download Results

1. Click **"Output"** tab (right sidebar)
2. Click **"Download All"** to get all reports

---

## 🐛 Troubleshooting

### Error: "Phase 2 baseline not found"

**Solution**: Make sure you:
1. Created the Phase 2 dataset (Step 1.1)
2. Attached it to the notebook (Step 3)
3. The dataset contains `BGL_lanobert/model/final/` directory

### Error: "Phase 3 TAC model not found"

**Solution**: Same as above, but for Phase 3 dataset (`BGL_tac`)

### Error: "BGL.log not found"

**Solution**: 
1. Search "BGL log" in Kaggle datasets
2. Add the BGL dataset to your notebook

### Error: Out of Memory (OOM)

**Solution**:
- Reduce `queue_capacity` in `configs/bgl_tac_full.yaml` (128 → 64)
- Use smaller batch size for inference

### Slow Inference

TAC inference is slower than baseline due to:
- Memory Queue operations (Welford updates)
- Mahalanobis distance calculation
- Expected: ~2h for BGL test set (~1.1M lines)

---

## 📈 Expected Results

### E1: Baseline (Phase 2)

| Metric | Value       |
|--------|-------------|
| F1     | 0.999974    |
| AUROC  | 0.999998    |
| FPR    | 0.000020    |

### E2: TAC vs Baseline

**Hypothesis H1**: FPR reduction ≥ 15%

### E3: Early Detection

**Hypothesis H2**: DLT > 0 (early warning capability)

- Mean DLT: ? minutes (to be measured)
- EWR (≥5 min): ?%
- DLT > 0 rate: ?%

---

## 🔄 Next Steps After Phase 4

Once Phase 4 completes:

1. **Analyze Results**:
   - Check if H1 passed (FPR reduction ≥15%)
   - Check if H2 passed (DLT > 0)

2. **Phase 5**: Ablation Study
   - Run `configs/ablations/bgl_time_only.yaml`
   - Run `configs/ablations/bgl_memory_only.yaml`
   - Compare contributions

3. **Phase 6**: Statistical Analysis
   - Run 5 times with different seeds
   - Wilcoxon Signed-Rank Test
   - Cohen's d effect size

---

## 📧 Support

If you encounter issues not covered here:

1. Check notebook cell outputs for detailed error messages
2. Verify all prerequisites are met
3. Check `Plan.md` Section 11 (Rủi ro & Giảm Thiểu)

---

**Last Updated**: 2026-08-26  
**Phase**: 4 (Main Experiments)  
**Status**: Ready to run on Kaggle
