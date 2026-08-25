# Hướng dẫn chạy TAC-LAnoBERT Phase 3 ở Local Terminal

Nếu bạn không muốn chạy trên Jupyter Notebook (`notebooks/phase3_verification.ipynb`) và muốn chạy trực tiếp bằng cửa sổ dòng lệnh (Terminal) của máy tính, tôi đã chuẩn bị sẵn một script tự động làm toàn bộ mọi thứ.

Quá trình này sử dụng một bộ dữ liệu giả (dummy data) siêu nhỏ gồm 250 dòng log để đảm bảo rằng quá trình xác minh chạy cực nhanh (dưới 1 phút) mà vẫn đi qua trọn vẹn toàn bộ các bước:
1. Tạo dummy data
2. Trích xuất timestamps (Preprocess)
3. Huấn luyện Tokenizer
4. Kiểm tra dòng chảy Gradient (Gradient Flow)
5. Huấn luyện TAC-LAnoBERT (Giới hạn 5 steps) và lưu Checkpoint

## Cách chạy

Mở cửa sổ Terminal trong VSCode (hoặc iTerm/Terminal của Mac), trỏ vào thư mục dự án `TAC-LAnoBERT` và chạy lần lượt các lệnh sau:

```bash
# 1. Kích hoạt môi trường ảo (virtual environment)
source venv/bin/activate

# 2. Đặt đường dẫn dự án để Python hiểu được module lanobert
export PYTHONPATH=.

# 3. Cấp quyền thực thi cho script
chmod +x scripts/run_phase3_local.sh

# 4. Chạy toàn bộ quá trình xác minh
./scripts/run_phase3_local.sh
```

## Giải thích chi tiết các thành phần

Nếu bạn muốn chạy tay từng bước một, dưới đây là các lệnh mà file `run_phase3_local.sh` sẽ thực thi:

### 1. Tạo Dummy Data
```bash
python scripts/create_dummy_bgl.py
```
*Tạo ra file `.raw` mẫu trong `data/BGL/`.*

### 2. Preprocess & Trích xuất Timestamps
```bash
python -m lanobert.preprocess --config configs/bgl_tac_full.yaml --split train --extract_timestamps
python -m lanobert.preprocess --config configs/bgl_tac_full.yaml --split test --extract_timestamps
```
*Đọc log thô và xuất ra `.timestamps`.*

### 3. Huấn luyện Tokenizer
```bash
python -m lanobert.tokenizer --config configs/bgl_tac_full.yaml
```

### 4. Kiểm tra Gradient
```bash
python scripts/test_gradients.py
```
*Kiểm tra xem Time2Vec có nhận được gradient ngược từ Loss hay không.*

### 5. Huấn luyện Model (Chạy nhanh)
```bash
python -m tac_lanobert.train_tac \
    --config configs/bgl_tac_full.yaml \
    --train.max_steps 5 \
    --train.eval_steps 5 \
    --train.per_device_train_batch_size 2
```
*Do có cờ `--train.max_steps 5`, mô hình sẽ dừng lại ngay sau 5 steps học, giúp bạn xác minh được quá trình lưu file `model.safetensors` không bị lỗi.*
