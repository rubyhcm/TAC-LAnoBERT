# TAC-LAnoBERT — Kaggle Notebooks

## Notebooks

| File | Purpose | Status |
|------|---------|--------|
| `bgl_lanobert.ipynb` | Phase 2: Baseline LAnoBERT on BGL | ✅ Complete |
| `phase3_verification.ipynb` | Phase 3: TAC runtime verification | ⏳ Run next |

## Phase 2 Results (BGL, T4 x2)

- **F1**: 0.999974 (paper: 1.000, Δ 0.0026%) ✅
- **AUROC**: 0.999998 (paper: 1.000, Δ 0.0002%) ✅
- **Best threshold**: 7.64127 | **FPR baseline**: 0.000020

## Phase 3 Verification Steps

Run `phase3_verification.ipynb` on Kaggle (T4 GPU, internet ON):

1. Clone repo → install deps → verify CUDA
2. Run 8 integration tests
3. Extract `.timestamps` sidecar files from BGL raw logs
4. Gradient flow test (Time2Vec ω, φ params)
5. Train 2 epochs with `configs/bgl_tac_full.yaml`
6. Verify exit criteria → save `outputs/BGL_tac/phase3_verification_report.json`

**Note**: BGL raw split files (`data/BGL/*.raw`) must already exist from Phase 2 run.
