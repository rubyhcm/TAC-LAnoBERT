# PHASE 3 QUICK START GUIDE
## TAC-LAnoBERT Implementation Roadmap

**Status**: Phase 2 ✅ Complete (BGL Baseline) → Phase 3 🚀 Ready to Start  
**Duration**: 4 weeks  
**Goal**: Implement Time-Aware Continual improvements to LAnoBERT

---

## 🎯 Phase 3 Objectives

Transform LAnoBERT (reactive detection) → TAC-LAnoBERT (proactive early warning) by adding:

1. **Time-Aware (T)**: Time2Vec embedding for temporal dynamics
2. **Continual Memory (C)**: Session Memory Queue with Mahalanobis distance
3. **Hybrid Scoring**: α·MLM + (1-α)·Mahalanobis for early detection

---

## 📅 Timeline Overview

| Week | Focus | Key Deliverables | Exit Criteria |
|---|---|---|---|
| **1-2** | Time2Vec | `time2vec.py`, `time_delta.py`, modify preprocessing | Time2Vec gradients flow, embeddings combine correctly |
| **3** | Memory Queue | `welford.py`, `shrinkage.py`, `memory_queue.py`, `scoring.py` | Mahalanobis computes without errors, Welford accurate |
| **4** | Integration | `model.py`, config files, tests, smoke test | All modes work, anti-leakage verified, 1-epoch training succeeds |

---

## 🚀 Quick Start Commands

### Week 1-2: Time2Vec Setup

```bash
# Create module structure
mkdir -p tac_lanobert tests

# Start with Time2Vec implementation
# See PHASE3_CHECKLIST.md Section 1.1-1.6 for details

# Run tests after implementation
pytest tests/test_time2vec.py -v
```

### Week 3: Memory Queue Setup

```bash
# Implement memory components
# See PHASE3_CHECKLIST.md Section 3.1-3.5 for details

# Run tests
pytest tests/test_welford.py -v
pytest tests/test_memory_queue.py -v
```

### Week 4: Integration & Testing

```bash
# Create configs
cp configs/bgl.yaml configs/bgl_tac_full.yaml
# Edit to add TAC section (see PHASE3_CHECKLIST.md 4.2)

# Run integration tests
pytest tests/test_integration.py -v

# Smoke test (1 epoch)
bash scripts/smoke_test_phase3.sh
```

---

## 📋 Checklist Summary

### Week 1-2: Time2Vec (6 checkpoints)
- [ ] 1.1. Time2VecLayer implementation
- [ ] 1.2. Timestamp extraction & Δt computation
- [ ] 1.3. Modify `lanobert/preprocess.py`
- [ ] 1.4. Modify `lanobert/dataset.py`
- [ ] 1.5. Modify `lanobert/train.py`
- [ ] 1.6. Unit tests pass ✅

### Week 3: Memory Queue (5 checkpoints)
- [ ] 3.1. Welford's Algorithm
- [ ] 3.2. Ledoit-Wolf Shrinkage
- [ ] 3.3. SessionMemoryQueue
- [ ] 3.4. HybridProactiveScorer
- [ ] 3.5. Unit tests pass ✅

### Week 4: Integration (5 checkpoints)
- [ ] 4.1. TACLAnoBERT wrapper
- [ ] 4.2. Config files (full + 3 ablations)
- [ ] 4.3. Integration tests
- [ ] 4.4. Anti-leakage verification
- [ ] 4.5. Smoke test (1 epoch) ✅

---

## 🎯 Success Criteria

**Must Pass Before Phase 4**:
1. ✅ All unit tests pass (time2vec, welford, memory_queue, integration)
2. ✅ Anti-leakage tests pass (7/7)
3. ✅ Smoke test completes (1 epoch training + inference)
4. ✅ No matrix singularity errors (Ledoit-Wolf handles)
5. ✅ Feature flags enable/disable components correctly
6. ✅ Configs load without errors

---

## 📊 Key Metrics to Track

| Metric | Phase 2 Baseline (BGL) | Phase 3 Target |
|---|---|---|
| **F1** | 0.999974 | ≥ 0.9997 (maintain) |
| **FPR** | 0.000020 | ≤ 0.000017 (15% reduction) |
| **DLT** | N/A (reactive) | > 0 (early detection) |
| **Latency** | N/A | < 10ms/window |

---

## 🔧 Implementation Priority

### Critical Path (Must Complete)
1. Time2Vec forward pass (enables temporal awareness)
2. Memory Queue Mahalanobis (enables proactive scoring)
3. TACLAnoBERT wrapper (integrates components)
4. Config files (enables experimentation)

### Nice-to-Have (Can Defer to Phase 4)
- EVT dynamic threshold (can use static threshold first)
- Normalized Hybrid Scorer (can use raw scores first)
- Advanced regularization (can use simple epsilon first)

---

## 🐛 Common Issues & Solutions

| Issue | Solution | Reference |
|---|---|---|
| **Gradient vanishing in Time2Vec** | Reduce num_periodic (15→5), check learning rate | PHASE3_CHECKLIST.md Rollback |
| **Singular covariance matrix** | Ledoit-Wolf shrinkage, add epsilon (1e-6) to diagonal | Section 3.2 |
| **OOM during training** | Reduce queue_capacity (128→64), gradient checkpointing | Rollback Plan |
| **Tests fail on Kaggle** | PyTorch version mismatch, check CUDA availability | Notes |

---

## 📁 File Structure After Phase 3

```
TAC-LAnoBERT/
├── tac_lanobert/              # NEW: TAC-specific modules
│   ├── time2vec.py            # Time2Vec embedding layer
│   ├── time_delta.py          # Timestamp extraction
│   ├── welford.py             # Online statistics O(1)
│   ├── shrinkage.py           # Ledoit-Wolf regularization
│   ├── memory_queue.py        # FIFO + Mahalanobis
│   ├── scoring.py             # Hybrid scorer
│   └── model.py               # TAC-LAnoBERT wrapper
├── lanobert/                  # MODIFIED: Baseline modules
│   ├── preprocess.py          # +timestamp extraction
│   ├── dataset.py             # +delta_t field
│   └── train.py               # +Time2Vec injection
├── tests/                     # NEW: Unit & integration tests
│   ├── test_time2vec.py
│   ├── test_welford.py
│   ├── test_memory_queue.py
│   ├── test_integration.py
│   └── test_data_leakage.py
├── configs/
│   ├── bgl_tac_full.yaml      # NEW: Full TAC config
│   └── ablations/             # NEW: Ablation configs
│       ├── bgl_baseline.yaml
│       ├── bgl_time_only.yaml
│       ├── bgl_memory_only.yaml
│       └── bgl_full_tac.yaml
└── scripts/
    └── smoke_test_phase3.sh   # NEW: Quick verification
```

---

## 🔗 Related Documents

- **Detailed Checklist**: `PHASE3_CHECKLIST.md` (week-by-week tasks)
- **Overall Plan**: `Plan.md` (9-month roadmap)
- **Phase 2 Completion**: `PHASE2_COMPLETION_BGL.md` (baseline results)
- **README**: `README.md` (project overview)

---

## 💡 Tips for Success

1. **Start Small**: Implement Time2Vec first (simpler than Memory Queue)
2. **Test Early**: Run unit tests after each checkpoint
3. **Use Debugger**: Set breakpoints to inspect tensor shapes
4. **Check Gradients**: Use `torch.autograd.gradcheck` for Time2Vec
5. **Log Everything**: Add print statements for debugging (remove later)
6. **Commit Often**: Git commit after each checkpoint
7. **Ask for Help**: Reference papers if stuck (Time2Vec, Ledoit-Wolf)

---

## 🎓 Mathematical Background

### Time2Vec Formula
```
t2v(τ, 0) = ω₀·τ + φ₀           (linear trend)
t2v(τ, i) = sin(ωᵢ·τ + φᵢ)      (periodic, i ≥ 1)
```
- ω: learnable frequency parameters
- φ: learnable phase parameters
- τ: normalized time delta (log(1 + Δt))

### Mahalanobis Distance
```
D_M(x) = sqrt((x - μ)ᵀ · Σ⁻¹ · (x - μ))
```
- μ: mean of historical [CLS] vectors
- Σ: covariance matrix (shrunk via Ledoit-Wolf)
- Measures deviation from normal trajectory

### Ledoit-Wolf Shrinkage
```
Σ_shrunk = (1 - α)·Σ_sample + α·μ·I
```
- α: optimal shrinkage intensity (computed from data)
- Prevents singular matrix issues

### Hybrid Score
```
Score = α·MLM_loss + (1-α)·Mahalanobis_dist
```
- MLM_loss: reactive (current anomaly)
- Mahalanobis: proactive (trajectory deviation)
- α: tunable weight (default: 0.5)

---

## 📞 Next Steps

1. **Review PHASE3_CHECKLIST.md** for detailed task breakdown
2. **Create tac_lanobert/ directory** and start with Time2Vec
3. **Set up unit tests** early (TDD approach)
4. **Run smoke test** after Week 4 to verify integration
5. **Update this document** as you encounter issues/solutions

---

**Questions?** Check Plan.md or PHASE3_CHECKLIST.md for detailed explanations.

**Ready to start?** Begin with PHASE3_CHECKLIST.md Section 1.1 (Time2Vec Module).

🚀 **Good luck with Phase 3!** 🚀
