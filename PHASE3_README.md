# Phase 3 Documentation Index

Chào mừng đến Phase 3 của TAC-LAnoBERT! Dưới đây là hướng dẫn sử dụng các tài liệu:

---

## 📚 Document Structure

```
TAC-LAnoBERT/
├── Plan.md                      # 📋 Master plan (9 tháng, tất cả phases)
├── PHASE2_COMPLETION_BGL.md     # ✅ Phase 2 results (baseline achieved)
├── PHASE3_QUICKSTART.md         # 🚀 START HERE - Quick overview & commands
├── PHASE3_CHECKLIST.md          # 📝 Detailed week-by-week task breakdown
├── PHASE3_PROGRESS.md           # 📊 Daily progress tracker (update as you go)
└── README.md                    # 📖 Project overview (general)
```

---

## 🎯 How to Use These Documents

### 1️⃣ **First Time?** → Read `PHASE3_QUICKSTART.md`
- **Purpose**: Get high-level overview in 5 minutes
- **Contains**: Timeline, key objectives, quick commands, math formulas
- **When to use**: Starting Phase 3, need quick reference

### 2️⃣ **Working on Tasks?** → Follow `PHASE3_CHECKLIST.md`
- **Purpose**: Step-by-step implementation guide
- **Contains**: Detailed code templates, test cases, exit criteria per checkpoint
- **When to use**: Daily coding work, implementing each module

### 3️⃣ **Tracking Progress?** → Update `PHASE3_PROGRESS.md`
- **Purpose**: Visual progress tracking
- **Contains**: Checkboxes, daily log, blocker tracking, metrics comparison
- **When to use**: After completing each checkpoint, daily standups

### 4️⃣ **Need Context?** → Refer to `Plan.md`
- **Purpose**: Understand overall research strategy
- **Contains**: 9-month roadmap, research questions, experimental design
- **When to use**: Planning, writing thesis, understanding "why"

### 5️⃣ **Baseline Reference?** → Check `PHASE2_COMPLETION_BGL.md`
- **Purpose**: Understand baseline performance
- **Contains**: F1=0.999974, FPR=0.000020, comparison with paper
- **When to use**: Setting targets, comparing Phase 3 results

---

## 🛠️ Recommended Workflow

### Daily Routine:
1. **Morning**: Check `PHASE3_PROGRESS.md` → identify current checkpoint
2. **Coding**: Follow `PHASE3_CHECKLIST.md` → implement current task
3. **Testing**: Run tests described in checklist
4. **Evening**: Update `PHASE3_PROGRESS.md` → mark completed tasks, log issues

### Weekly Review:
1. Count checkpoints completed this week
2. Update `PHASE3_PROGRESS.md` progress bars
3. Review blockers/risks
4. Plan next week's focus

### Stuck on Something?
1. Check `PHASE3_QUICKSTART.md` → "Common Issues & Solutions" section
2. Check `PHASE3_CHECKLIST.md` → "Rollback Plan" section
3. Check `Plan.md` → Section 11 "Rủi Ro & Giảm Thiểu"

---

## 📖 Document Cheat Sheet

| Question | Document | Section |
|---|---|---|
| "What should I do today?" | `PHASE3_PROGRESS.md` | Current Week tracker |
| "How do I implement Time2Vec?" | `PHASE3_CHECKLIST.md` | Section 1.1-1.6 |
| "What's the formula for Mahalanobis?" | `PHASE3_QUICKSTART.md` | Mathematical Background |
| "Why are we doing this?" | `Plan.md` | Section 3 (Cải Tiến Mục Tiêu) |
| "What's the baseline FPR?" | `PHASE2_COMPLETION_BGL.md` | Metrics Summary |
| "What tests should I write?" | `PHASE3_CHECKLIST.md` | Each checkpoint's Testing section |
| "Am I behind schedule?" | `PHASE3_PROGRESS.md` | Week-by-Week Tracker |
| "What are the exit criteria?" | `PHASE3_PROGRESS.md` | Exit Criteria section |

---

## 🎯 Phase 3 Quick Facts

| Attribute | Value |
|---|---|
| **Duration** | 4 weeks (28 days) |
| **Start Date** | 2026-08-24 |
| **Components** | Time2Vec, Memory Queue, Hybrid Scoring |
| **Files to Create** | 19 files (8 modules, 5 tests, 5 configs, 1 script) |
| **Exit Criteria** | 7 requirements (see PHASE3_PROGRESS.md) |
| **Success Metric** | FPR ≤ 0.000017 (15% reduction), DLT > 0 |

---

## 🚀 Quick Start (3 Steps)

```bash
# 1. Read the quickstart guide
cat PHASE3_QUICKSTART.md

# 2. Open the detailed checklist
cat PHASE3_CHECKLIST.md | less

# 3. Start with first checkpoint
mkdir -p tac_lanobert tests
touch tac_lanobert/__init__.py
touch tac_lanobert/time2vec.py
# Now implement Time2VecLayer following PHASE3_CHECKLIST.md Section 1.1
```

---

## 📞 Need Help?

### For Implementation Questions:
- **Time2Vec**: See `PHASE3_CHECKLIST.md` Section 1.1-1.6
- **Memory Queue**: See `PHASE3_CHECKLIST.md` Section 3.1-3.5
- **Integration**: See `PHASE3_CHECKLIST.md` Section 4.1-4.5

### For Research Questions:
- **Motivation**: See `Plan.md` Section 1-2 (Tổng Quan, Baseline)
- **Experimental Design**: See `Plan.md` Section 7 (Thiết Kế Thực Nghiệm)
- **Metrics**: See `Plan.md` Section 8 (Metrics Đánh Giá)

### For Tracking Questions:
- **Am I on track?**: See `PHASE3_PROGRESS.md` Week-by-Week Tracker
- **What's blocking me?**: Update `PHASE3_PROGRESS.md` Blockers section
- **What's next?**: See `PHASE3_PROGRESS.md` Next Action

---

## ✅ Pre-Phase 3 Checklist

Before starting Phase 3, verify Phase 2 completion:

- [x] BGL dataset split (train/val/test)
- [x] LAnoBERT baseline trained (10 epochs)
- [x] F1 ≈ 0.999974 (matches paper: 1.000)
- [x] FPR baseline tracked: 0.000020
- [x] Tokenizer & model artifacts saved
- [x] Anti-leakage tests passed (7/7)
- [x] Baseline reports created

**Status**: ✅ All prerequisites met (see `PHASE2_COMPLETION_BGL.md`)

---

## 🎓 Learning Path

### Week 1 Focus: Temporal Modeling
**Read before coding**:
- Time2Vec paper (Kazemi et al.)
- Understand learnable frequency ω and phase φ
- Why log-transform Δt? (stabilize extreme values)

### Week 3 Focus: Statistical Methods
**Read before coding**:
- Welford's online algorithm (Wikipedia)
- Ledoit-Wolf shrinkage (handle singular matrices)
- Mahalanobis distance (deviation from distribution)

### Week 4 Focus: Integration
**Prepare for**:
- Feature flags pattern (enable/disable components)
- Config-driven experimentation
- Anti-leakage verification (temporal ordering)

---

## 💡 Pro Tips

1. **Don't skip tests**: They catch issues early
2. **Commit often**: After each checkpoint (e.g., "Checkpoint 1.1: Time2Vec forward pass")
3. **Log everything**: Add DEBUG logging during development
4. **Use debugger**: Inspect tensor shapes when stuck
5. **Check shapes**: Most bugs are shape mismatches
6. **Reference baseline**: When in doubt, check how LAnoBERT does it

---

## 📊 Document Maintenance

**Update frequency**:
- `PHASE3_PROGRESS.md`: Daily (after each coding session)
- `PHASE3_CHECKLIST.md`: Rarely (only if approach changes)
- `PHASE3_QUICKSTART.md`: Rarely (reference only)
- `Plan.md`: Weekly (update status, risks)

**Version control**:
- Git commit after marking checkpoints complete
- Keep daily log in `PHASE3_PROGRESS.md` for retrospective

---

## 🎉 Success Signals

You're ready for Phase 4 when:
- ✅ All checkboxes in `PHASE3_PROGRESS.md` marked complete
- ✅ Smoke test passes (1 epoch training runs without errors)
- ✅ All unit tests green (pytest shows 100% pass)
- ✅ Anti-leakage verified (7/7 tests pass)
- ✅ No "TODO" comments in critical code paths

---

**Current Status**: Phase 3 Day 0 (Planning Complete)  
**Next Action**: Read `PHASE3_QUICKSTART.md`, then start Checkpoint 1.1  
**Questions?**: Check the "Document Cheat Sheet" above

🚀 **Let's build TAC-LAnoBERT!** 🚀
