tôi đã chạy notebooks/bgl_lanobert.ipynb trên kaggle với GPU T4 x2 và được kết quả trong outputs/BGL_lanobert, hãy đọc Plan.md kiểm tra xem pharse-2 cần làm gì nữa không? lưu ý không chạy dataset thunderbird do tôi muốn test TAC-LAnoBert hoàn chỉnh với dataset bgl trước. Sau đó hãy update Plan.md nếu cần để tiếp tục pharse-3

các code change hiện tại là code của pharse-3 trong Plan.md, bạn hãy review nó, có thể đọc thêm MAIN-PLAN.md để hiểu tổng thể vì đây là plan gốc. Cập nhật code và Plan.md nếu cần

source venv/bin/activate

python3 -m tac_lanobert.split_tac --config configs/bgl_tac_full.yaml

python3 -m tac_lanobert.preprocess_tac \
 --config configs/bgl_tac_full.yaml \
 --split train \
 --extract_timestamps

python3 -m tac_lanobert.preprocess_tac \
 --config configs/bgl_tac_full.yaml \
 --split test \
 --extract_timestamps

python3 -m tac_lanobert.tokenizer_tac --config configs/bgl_tac_full.yaml

python3 -m tac_lanobert.train_tac --config configs/bgl_tac_full.yaml

python3 -m tac_lanobert.train_tac --config configs/bgl_tac_local_fast.yaml

---

source venv/bin/activate

python3 -m lanobert.split --config configs/bgl_tac_full.yaml

python3 -m lanobert.preprocess \
 --config configs/bgl_tac_full.yaml \
 --split train \
 --extract_timestamps

python3 -m lanobert.preprocess \
 --config configs/bgl_tac_full.yaml \
 --split test \
 --extract_timestamps

python3 -m tac_lanobert.train_tac --config configs/bgl_tac_full.yaml

python3 -m tac_lanobert.train_tac --config configs/bgl_tac_local_fast.yaml
