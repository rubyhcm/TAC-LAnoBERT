# PHASE 3 IMPLEMENTATION CHECKLIST
## TAC-LAnoBERT: Time-Aware Continual Improvements

**Start Date**: 2026-08-24  
**Duration**: 4 weeks  
**Goal**: Triển khai 3 module chính (Time2Vec, Memory Queue, Hybrid Scoring)

---

## 📅 Week 1-2: Time2Vec Implementation (Component T)

### 1.1. Core Time2Vec Module
**File**: `tac_lanobert/time2vec.py`

- [ ] **Create module structure**
  ```bash
  mkdir -p tac_lanobert
  touch tac_lanobert/__init__.py
  touch tac_lanobert/time2vec.py
  ```

- [ ] **Implement Time2VecLayer**
  - [ ] Linear component parameters:
    - [ ] `self.omega_linear` (learnable, init: uniform[-1, 1])
    - [ ] `self.phi_linear` (learnable, init: uniform[-π, π])
  - [ ] Periodic component parameters:
    - [ ] `self.omega_periodic` (learnable, shape: [num_periodic])
    - [ ] `self.phi_periodic` (learnable, shape: [num_periodic])
  - [ ] Projection layer:
    - [ ] `self.linear_proj`: nn.Linear(1 + num_periodic, hidden_size)
  
- [ ] **Forward method**
  ```python
  def forward(self, delta_t):
      # delta_t: (batch, seq_len)
      # Output: (batch, seq_len, hidden_size)
      
      # Linear component
      linear = omega_linear * delta_t + phi_linear
      
      # Periodic components
      periodic = torch.sin(omega_periodic * delta_t.unsqueeze(-1) + phi_periodic)
      
      # Concatenate & project
      combined = torch.cat([linear.unsqueeze(-1), periodic], dim=-1)
      return self.linear_proj(combined)
  ```

- [ ] **Docstrings & comments**
  - [ ] Class docstring with paper reference
  - [ ] Method docstrings with shape annotations
  - [ ] Inline comments explaining learnable parameters

**Checkpoint 1.1**: Time2VecLayer forward pass executes, output shape correct

---

### 1.2. Time-Delta Extraction
**File**: `tac_lanobert/time_delta.py`

- [ ] **Create module**
  ```bash
  touch tac_lanobert/time_delta.py
  ```

- [ ] **Implement timestamp extraction**
  - [ ] `extract_timestamp(log_line: str) -> Optional[float]`
    - [ ] BGL regex pattern: `r'^\d{10}'` (Unix timestamp)
    - [ ] Thunderbird regex: `r'^\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d{6}'`
    - [ ] Parse to float (seconds since epoch)
    - [ ] Handle parsing errors (return None)
  
- [ ] **Implement delta computation**
  - [ ] `compute_delta_t(timestamps: List[float]) -> np.ndarray`
    - [ ] Compute consecutive differences: `np.diff(timestamps)`
    - [ ] Convert to milliseconds: `* 1000`
    - [ ] Prepend 0 for first event (no prior context)
    - [ ] Handle negative deltas (warning log, clip to 0)
  
- [ ] **Implement normalization**
  - [ ] `normalize_delta_t(delta_t: np.ndarray) -> np.ndarray`
    - [ ] Log-transform: `np.log(1 + delta_t)`
    - [ ] Rationale: stabilize extreme values (e.g., 1ms vs 3600000ms)
    - [ ] Z-score normalization (optional, track mean/std)

**Checkpoint 1.2**: Extract timestamps from sample BGL logs, compute Δt correctly

---

### 1.3. Modify Preprocessing Pipeline
**File**: `lanobert/preprocess.py`

- [ ] **Add timestamp extraction flag**
  - [ ] Add `extract_timestamps: bool = False` to preprocess function
  - [ ] If True, call `time_delta.extract_timestamp()` per line
  - [ ] Save timestamps to `{output_path}.timestamps.npy`
  
- [ ] **Save delta_t alongside preprocessed logs**
  - [ ] Compute delta_t from timestamps
  - [ ] Normalize delta_t
  - [ ] Save to `{output_path}.delta_t.npy`
  
- [ ] **Update config schema**
  - [ ] Add `preprocess.extract_timestamps: true` to `bgl_tac_full.yaml`

**Checkpoint 1.3**: Run preprocess on BGL train split, verify `.timestamps.npy` and `.delta_t.npy` created

---

### 1.4. Modify Dataset
**File**: `lanobert/dataset.py`

- [ ] **Load delta_t in LogDataset**
  - [ ] Add `delta_t_path: Optional[str]` parameter to `__init__`
  - [ ] Load delta_t array: `self.delta_t = np.load(delta_t_path)` if provided
  - [ ] Default to zeros if not provided (fallback to baseline)
  
- [ ] **Return delta_t in __getitem__**
  - [ ] Modify return tuple:
    ```python
    # Before: return input_ids, attention_mask
    # After: return input_ids, attention_mask, delta_t_window
    ```
  - [ ] Extract delta_t for current window: `self.delta_t[idx:idx+seq_len]`
  - [ ] Pad if necessary (to seq_len)

**Checkpoint 1.4**: DataLoader returns 3-tuple (input_ids, attention_mask, delta_t), shapes match

---

### 1.5. Modify Training Loop
**File**: `lanobert/train.py`

- [ ] **Inject Time2Vec into model**
  - [ ] Add Time2VecLayer to model:
    ```python
    if config.tac.time2vec.enabled:
        self.time2vec = Time2VecLayer(
            hidden_size=config.model.hidden_size,
            num_periodic=config.tac.time2vec.num_periodic
        )
    ```
  
- [ ] **Modify embedding computation**
  - [ ] Original: `embeddings = token_emb + position_emb`
  - [ ] TAC: `embeddings = token_emb + position_emb + time2vec_emb`
  - [ ] Conditional on feature flag:
    ```python
    if hasattr(self, 'time2vec'):
        time_emb = self.time2vec(delta_t)
        embeddings = embeddings + time_emb
    ```
  
- [ ] **Update training loop**
  - [ ] Unpack 3-tuple from DataLoader:
    ```python
    input_ids, attention_mask, delta_t = batch
    delta_t = delta_t.to(device)
    ```
  - [ ] Pass delta_t to model forward

**Checkpoint 1.5**: Training runs without error, Time2Vec parameters updated via backprop

---

### 1.6. Testing Time2Vec
**File**: `tests/test_time2vec.py`

- [ ] **Create test file**
  ```bash
  mkdir -p tests
  touch tests/test_time2vec.py
  ```

- [ ] **Test gradient flow**
  ```python
  def test_gradient_flow():
      layer = Time2VecLayer(hidden_size=768, num_periodic=15)
      delta_t = torch.rand(4, 512) * 1000  # random deltas
      output = layer(delta_t)
      loss = output.sum()
      loss.backward()
      
      # Check gradients exist
      assert layer.omega_linear.grad is not None
      assert layer.phi_linear.grad is not None
      assert layer.omega_periodic.grad is not None
      assert layer.phi_periodic.grad is not None
  ```

- [ ] **Test shape compatibility**
  ```python
  def test_output_shape():
      layer = Time2VecLayer(hidden_size=768, num_periodic=15)
      delta_t = torch.rand(4, 512)
      output = layer(delta_t)
      assert output.shape == (4, 512, 768)
  ```

- [ ] **Test numerical stability**
  ```python
  def test_extreme_values():
      layer = Time2VecLayer(hidden_size=768, num_periodic=15)
      
      # Test extreme deltas
      delta_t = torch.tensor([[0.0, 1e-6, 1e6, 3.6e9]])  # 0ms to 1h
      output = layer(delta_t)
      
      assert not torch.isnan(output).any()
      assert not torch.isinf(output).any()
  ```

- [ ] **Run tests**
  ```bash
  pytest tests/test_time2vec.py -v
  ```

**Checkpoint 1.6**: All Time2Vec tests pass ✅

---

### 🎯 Exit Criteria Week 1-2
- ✅ Time2VecLayer forward pass executes without error
- ✅ Gradients flow to ω, φ parameters
- ✅ Combined embedding (Token + Positional + Time2Vec) has correct shape
- ✅ Preprocessing extracts timestamps and computes Δt
- ✅ DataLoader returns 3-tuple with delta_t
- ✅ Training loop integrates Time2Vec, loss decreases
- ✅ All unit tests pass

---

## 📅 Week 3: Memory Queue Implementation (Component C)

### 3.1. Welford's Online Statistics
**File**: `tac_lanobert/welford.py`

- [ ] **Create module**
  ```bash
  touch tac_lanobert/welford.py
  ```

- [ ] **Implement WelfordState dataclass**
  ```python
  @dataclass
  class WelfordState:
      count: int = 0
      mean: torch.Tensor = None  # (hidden_dim,)
      M2: torch.Tensor = None    # (hidden_dim, hidden_dim) - sum of squared differences
  ```

- [ ] **Implement update function**
  ```python
  def welford_update(state: WelfordState, new_value: torch.Tensor) -> WelfordState:
      """
      O(1) online update of mean and covariance.
      
      Args:
          state: Current WelfordState
          new_value: New vector (hidden_dim,)
      
      Returns:
          Updated WelfordState
      """
      count = state.count + 1
      delta = new_value - state.mean
      mean = state.mean + delta / count
      delta2 = new_value - mean
      M2 = state.M2 + torch.outer(delta, delta2)
      
      return WelfordState(count=count, mean=mean, M2=M2)
  ```

- [ ] **Implement finalization**
  ```python
  def welford_finalize(state: WelfordState) -> Tuple[torch.Tensor, torch.Tensor]:
      """
      Extract mean and covariance from WelfordState.
      
      Returns:
          mean: (hidden_dim,)
          cov: (hidden_dim, hidden_dim)
      """
      mean = state.mean
      cov = state.M2 / (state.count - 1) if state.count > 1 else torch.zeros_like(state.M2)
      return mean, cov
  ```

**Checkpoint 3.1**: Welford update runs in O(1), matches batch computation

---

### 3.2. Ledoit-Wolf Shrinkage
**File**: `tac_lanobert/shrinkage.py`

- [ ] **Create module**
  ```bash
  touch tac_lanobert/shrinkage.py
  ```

- [ ] **Implement shrinkage coefficient**
  ```python
  def compute_shrinkage_coefficient(sample_cov: torch.Tensor, n_samples: int) -> float:
      """
      Compute Ledoit-Wolf optimal shrinkage intensity.
      
      Formula:
          α* = min(1, (trace(Σ²) / n) / ||Σ - μI||²_F)
      
      Args:
          sample_cov: Sample covariance matrix (d, d)
          n_samples: Number of samples used to compute sample_cov
      
      Returns:
          alpha: Shrinkage coefficient in [0, 1]
      """
      # Target: scaled identity matrix
      d = sample_cov.shape[0]
      mu = torch.trace(sample_cov) / d
      target = mu * torch.eye(d, device=sample_cov.device)
      
      # Frobenius norm squared
      delta = sample_cov - target
      norm_sq = torch.sum(delta ** 2)
      
      # Asymptotic variance (simplified)
      trace_sq = torch.trace(sample_cov @ sample_cov)
      alpha = min(1.0, (trace_sq / n_samples) / (norm_sq + 1e-8))
      
      return alpha
  ```

- [ ] **Implement shrinkage transformation**
  ```python
  def shrink_covariance(sample_cov: torch.Tensor, alpha: float) -> torch.Tensor:
      """
      Apply shrinkage to covariance matrix.
      
      Formula:
          Σ_shrunk = (1 - α)·Σ_sample + α·μ·I
      
      Args:
          sample_cov: Sample covariance (d, d)
          alpha: Shrinkage intensity [0, 1]
      
      Returns:
          Shrunk covariance matrix (d, d)
      """
      d = sample_cov.shape[0]
      mu = torch.trace(sample_cov) / d
      target = mu * torch.eye(d, device=sample_cov.device)
      
      return (1 - alpha) * sample_cov + alpha * target
  ```

**Checkpoint 3.2**: Shrinkage handles singular matrices, alpha in [0, 1]

---

### 3.3. Session Memory Queue
**File**: `tac_lanobert/memory_queue.py`

- [ ] **Create module**
  ```bash
  touch tac_lanobert/memory_queue.py
  ```

- [ ] **Implement SessionMemoryQueue class**
  ```python
  class SessionMemoryQueue:
      def __init__(self, capacity: int = 128, hidden_dim: int = 768):
          self.capacity = capacity
          self.hidden_dim = hidden_dim
          self.queue = deque(maxlen=capacity)  # FIFO
          self.welford_state = WelfordState(
              count=0,
              mean=torch.zeros(hidden_dim),
              M2=torch.zeros(hidden_dim, hidden_dim)
          )
      
      def push(self, cls_vector: torch.Tensor):
          """
          Add new [CLS] vector to queue, update statistics.
          
          Args:
              cls_vector: (hidden_dim,) tensor
          """
          self.queue.append(cls_vector.detach().cpu())
          self.welford_state = welford_update(self.welford_state, cls_vector)
      
      def mahalanobis_distance(self, cls_vector: torch.Tensor) -> float:
          """
          Compute Mahalanobis distance of cls_vector from queue distribution.
          
          Formula:
              D_M(x) = sqrt((x - μ)ᵀ · Σ⁻¹ · (x - μ))
          
          Args:
              cls_vector: (hidden_dim,) tensor
          
          Returns:
              Mahalanobis distance (scalar)
          """
          if self.welford_state.count < 2:
              return 0.0  # Not enough samples
          
          mean, cov = welford_finalize(self.welford_state)
          
          # Apply Ledoit-Wolf shrinkage
          alpha = compute_shrinkage_coefficient(cov, self.welford_state.count)
          cov_shrunk = shrink_covariance(cov, alpha)
          
          # Compute Mahalanobis distance
          delta = cls_vector - mean
          try:
              cov_inv = torch.linalg.inv(cov_shrunk + 1e-6 * torch.eye(self.hidden_dim))
              distance = torch.sqrt(delta @ cov_inv @ delta)
              return distance.item()
          except RuntimeError:  # Singular matrix despite shrinkage
              # Fallback to Euclidean distance
              return torch.norm(delta).item()
      
      def reset(self):
          """Clear queue and statistics (for new session)."""
          self.queue.clear()
          self.welford_state = WelfordState(
              count=0,
              mean=torch.zeros(self.hidden_dim),
              M2=torch.zeros(self.hidden_dim, self.hidden_dim)
          )
  ```

**Checkpoint 3.3**: Memory Queue push/pop works, Mahalanobis computes without errors

---

### 3.4. Hybrid Proactive Scorer
**File**: `tac_lanobert/scoring.py`

- [ ] **Create module**
  ```bash
  touch tac_lanobert/scoring.py
  ```

- [ ] **Implement HybridProactiveScorer**
  ```python
  class HybridProactiveScorer:
      def __init__(self, alpha: float = 0.5):
          """
          Args:
              alpha: Weight for MLM loss (1-alpha for Mahalanobis)
          """
          assert 0 <= alpha <= 1, "alpha must be in [0, 1]"
          self.alpha = alpha
      
      def score(self, mlm_loss: float, mahalanobis_dist: float) -> float:
          """
          Compute hybrid anomaly score.
          
          Formula:
              score = α·mlm_loss + (1-α)·mahalanobis_dist
          
          Args:
              mlm_loss: Cross-entropy loss (reactive component)
              mahalanobis_dist: Distance from normal trajectory (proactive)
          
          Returns:
              Hybrid anomaly score
          """
          return self.alpha * mlm_loss + (1 - self.alpha) * mahalanobis_dist
  ```

- [ ] **Implement normalization strategy**
  ```python
  class NormalizedHybridScorer:
      def __init__(self, alpha: float = 0.5):
          self.alpha = alpha
          self.mlm_stats = {"mean": 0, "std": 1}  # Update from validation set
          self.mahal_stats = {"mean": 0, "std": 1}
      
      def update_stats(self, mlm_losses: List[float], mahal_dists: List[float]):
          """Update normalization statistics from validation set."""
          self.mlm_stats = {"mean": np.mean(mlm_losses), "std": np.std(mlm_losses)}
          self.mahal_stats = {"mean": np.mean(mahal_dists), "std": np.std(mahal_dists)}
      
      def score(self, mlm_loss: float, mahalanobis_dist: float) -> float:
          """Z-score normalize before combining."""
          mlm_z = (mlm_loss - self.mlm_stats["mean"]) / (self.mlm_stats["std"] + 1e-8)
          mahal_z = (mahalanobis_dist - self.mahal_stats["mean"]) / (self.mahal_stats["std"] + 1e-8)
          return self.alpha * mlm_z + (1 - self.alpha) * mahal_z
  ```

**Checkpoint 3.4**: Scorer combines two signals, normalization stabilizes scales

---

### 3.5. Testing Memory Queue
**File**: `tests/test_memory_queue.py`

- [ ] **Create test file**
  ```bash
  touch tests/test_memory_queue.py
  ```

- [ ] **Test FIFO overflow**
  ```python
  def test_fifo_overflow():
      queue = SessionMemoryQueue(capacity=3, hidden_dim=4)
      
      for i in range(5):
          queue.push(torch.randn(4))
      
      assert len(queue.queue) == 3  # Only last 3 retained
      assert queue.welford_state.count == 5  # Statistics track all
  ```

- [ ] **Test Welford accuracy**
  ```python
  def test_welford_accuracy():
      queue = SessionMemoryQueue(capacity=100, hidden_dim=4)
      vectors = [torch.randn(4) for _ in range(50)]
      
      # Push to queue
      for v in vectors:
          queue.push(v)
      
      # Compare Welford mean with NumPy
      mean_welford, _ = welford_finalize(queue.welford_state)
      mean_numpy = torch.stack(vectors).mean(dim=0)
      
      assert torch.allclose(mean_welford, mean_numpy, atol=1e-5)
  ```

- [ ] **Test Mahalanobis stability**
  ```python
  def test_mahalanobis_stability():
      queue = SessionMemoryQueue(capacity=10, hidden_dim=4)
      
      # Normal vectors (mean=0, std=1)
      for _ in range(10):
          queue.push(torch.randn(4))
      
      # Anomalous vector (mean=10, std=1)
      anomaly = torch.randn(4) + 10
      dist_anomaly = queue.mahalanobis_distance(anomaly)
      
      # Normal vector
      normal = torch.randn(4)
      dist_normal = queue.mahalanobis_distance(normal)
      
      # Anomaly should have higher distance
      assert dist_anomaly > dist_normal
      assert not np.isnan(dist_anomaly)
      assert not np.isinf(dist_anomaly)
  ```

- [ ] **Run tests**
  ```bash
  pytest tests/test_memory_queue.py -v
  ```

**Checkpoint 3.5**: All Memory Queue tests pass ✅

---

### 🎯 Exit Criteria Week 3
- ✅ Memory Queue executes without matrix inversion errors
- ✅ Welford mean/cov matches batch computation (tol=1e-5)
- ✅ Mahalanobis distance bounded, no Inf values
- ✅ Hybrid Scorer combines MLM + Mahalanobis correctly
- ✅ All unit tests pass

---

## 📅 Week 4: Integration & Configuration

### 4.1. TAC-LAnoBERT Model Wrapper
**File**: `tac_lanobert/model.py`

- [ ] **Create module**
  ```bash
  touch tac_lanobert/model.py
  ```

- [ ] **Implement TACLAnoBERT wrapper**
  ```python
  class TACLAnoBERT(nn.Module):
      def __init__(self, config):
          super().__init__()
          self.config = config
          
          # Load base LAnoBERT
          self.bert = AutoModelForMaskedLM.from_pretrained(
              config.model.pretrained_model_name_or_path
          )
          
          # Feature flags
          self.time2vec_enabled = config.tac.time2vec.enabled
          self.memory_enabled = config.tac.memory.enabled
          self.scoring_mode = config.tac.scoring.mode  # mlm_only | mahalanobis_only | hybrid
          
          # Time2Vec module
          if self.time2vec_enabled:
              self.time2vec = Time2VecLayer(
                  hidden_size=config.model.hidden_size,
                  num_periodic=config.tac.time2vec.num_periodic
              )
          
          # Memory Queue (initialized at inference time)
          if self.memory_enabled:
              self.memory_queue = SessionMemoryQueue(
                  capacity=config.tac.memory.queue_capacity,
                  hidden_dim=config.model.hidden_size
              )
          
          # Hybrid Scorer
          self.scorer = HybridProactiveScorer(alpha=config.tac.scoring.alpha)
      
      def forward(self, input_ids, attention_mask, delta_t=None):
          """
          Forward pass with optional Time2Vec injection.
          
          Args:
              input_ids: (batch, seq_len)
              attention_mask: (batch, seq_len)
              delta_t: (batch, seq_len), optional if time2vec_enabled=False
          
          Returns:
              outputs: BERT outputs (logits, hidden_states, etc.)
          """
          # Get token embeddings
          embeddings = self.bert.get_input_embeddings()(input_ids)
          
          # Add Time2Vec if enabled
          if self.time2vec_enabled:
              if delta_t is None:
                  raise ValueError("delta_t required when time2vec_enabled=True")
              time_emb = self.time2vec(delta_t)
              embeddings = embeddings + time_emb
          
          # Forward through BERT with modified embeddings
          outputs = self.bert(
              inputs_embeds=embeddings,
              attention_mask=attention_mask,
              output_hidden_states=True
          )
          
          return outputs
      
      def compute_anomaly_score(self, outputs, labels):
          """
          Compute hybrid anomaly score.
          
          Args:
              outputs: BERT outputs
              labels: Ground truth token IDs (for MLM loss)
          
          Returns:
              score: Hybrid anomaly score
          """
          # MLM loss (reactive)
          mlm_loss = F.cross_entropy(
              outputs.logits.view(-1, outputs.logits.size(-1)),
              labels.view(-1),
              reduction='mean'
          )
          
          # Mahalanobis distance (proactive)
          if self.memory_enabled:
              cls_vector = outputs.hidden_states[-1][:, 0, :]  # [CLS] from last layer
              self.memory_queue.push(cls_vector.squeeze(0))  # Assuming batch=1 for streaming
              mahal_dist = self.memory_queue.mahalanobis_distance(cls_vector.squeeze(0))
          else:
              mahal_dist = 0.0
          
          # Combine based on scoring mode
          if self.scoring_mode == 'mlm_only':
              return mlm_loss.item()
          elif self.scoring_mode == 'mahalanobis_only':
              return mahal_dist
          else:  # hybrid
              return self.scorer.score(mlm_loss.item(), mahal_dist)
  ```

**Checkpoint 4.1**: TACLAnoBERT wrapper loads, forward pass succeeds

---

### 4.2. Configuration Files
**Files**: `configs/bgl_tac_*.yaml`

- [ ] **Create full TAC config**
  ```bash
  cp configs/bgl.yaml configs/bgl_tac_full.yaml
  ```
  
  Add TAC section:
  ```yaml
  # BGL TAC-LAnoBERT Full Configuration
  
  tac:
    mode: improved  # baseline | ablation_time | ablation_memory | improved
    
    time2vec:
      enabled: true
      num_periodic: 15  # Number of sin components
    
    memory:
      enabled: true
      queue_capacity: 128  # FIFO queue size
    
    scoring:
      mode: hybrid  # mlm_only | mahalanobis_only | hybrid
      alpha: 0.5  # Weight for MLM (1-alpha for Mahalanobis)
      threshold: evt  # static | evt (Extreme Value Theory)
  
  preprocess:
    extract_timestamps: true  # NEW: Enable timestamp extraction
  ```

- [ ] **Create ablation configs**
  ```bash
  mkdir -p configs/ablations
  ```
  
  - [ ] **Time-only ablation** (`bgl_time_only.yaml`):
    ```yaml
    tac:
      mode: ablation_time
      time2vec:
        enabled: true
        num_periodic: 15
      memory:
        enabled: false
      scoring:
        mode: mlm_only
    ```
  
  - [ ] **Memory-only ablation** (`bgl_memory_only.yaml`):
    ```yaml
    tac:
      mode: ablation_memory
      time2vec:
        enabled: false
      memory:
        enabled: true
        queue_capacity: 128
      scoring:
        mode: hybrid
        alpha: 0.5
    ```
  
  - [ ] **Baseline config** (for comparison):
    ```yaml
    tac:
      mode: baseline
      time2vec:
        enabled: false
      memory:
        enabled: false
      scoring:
        mode: mlm_only
    ```

**Checkpoint 4.2**: All config files parse correctly, YAML valid

---

### 4.3. Integration Testing
**File**: `tests/test_integration.py`

- [ ] **Create test file**
  ```bash
  touch tests/test_integration.py
  ```

- [ ] **Test all modes**
  ```python
  @pytest.mark.parametrize("mode,time2vec,memory", [
      ("baseline", False, False),
      ("ablation_time", True, False),
      ("ablation_memory", False, True),
      ("improved", True, True),
  ])
  def test_forward_pass_all_modes(mode, time2vec, memory):
      config = load_config(f"configs/ablations/bgl_{mode}.yaml")
      model = TACLAnoBERT(config)
      
      batch_size, seq_len = 2, 512
      input_ids = torch.randint(0, 30000, (batch_size, seq_len))
      attention_mask = torch.ones(batch_size, seq_len)
      delta_t = torch.rand(batch_size, seq_len) * 1000 if time2vec else None
      
      outputs = model(input_ids, attention_mask, delta_t)
      
      assert outputs.logits.shape == (batch_size, seq_len, config.model.vocab_size)
      assert not torch.isnan(outputs.logits).any()
  ```

- [ ] **Test feature flags**
  ```python
  def test_feature_flags():
      config_full = load_config("configs/bgl_tac_full.yaml")
      model = TACLAnoBERT(config_full)
      
      assert model.time2vec_enabled == True
      assert model.memory_enabled == True
      assert hasattr(model, 'time2vec')
      assert hasattr(model, 'memory_queue')
  ```

- [ ] **Test scoring modes**
  ```python
  def test_scoring_modes():
      config = load_config("configs/bgl_tac_full.yaml")
      
      # MLM only
      config.tac.scoring.mode = 'mlm_only'
      model = TACLAnoBERT(config)
      score = model.compute_anomaly_score(mock_outputs, mock_labels)
      assert isinstance(score, float)
      
      # Hybrid
      config.tac.scoring.mode = 'hybrid'
      model = TACLAnoBERT(config)
      score = model.compute_anomaly_score(mock_outputs, mock_labels)
      assert isinstance(score, float)
  ```

- [ ] **Run integration tests**
  ```bash
  pytest tests/test_integration.py -v
  ```

**Checkpoint 4.3**: All integration tests pass ✅

---

### 4.4. Anti-Leakage Verification
**File**: `tests/test_data_leakage.py`

- [ ] **Memory Queue temporal ordering**
  ```python
  def test_memory_queue_no_future_leak():
      queue = SessionMemoryQueue(capacity=10, hidden_dim=4)
      
      # Simulate streaming inference with timestamps
      events = [(t, torch.randn(4)) for t in range(20)]
      
      for t, vector in events:
          # Queue should only contain vectors from t' <= t
          queue.push(vector)
          
          # Verify queue contains max(0, t - capacity + 1) to t
          expected_count = min(t + 1, queue.capacity)
          assert len(queue.queue) == expected_count
  ```

- [ ] **DataLoader shuffle disabled on test**
  ```python
  def test_test_dataloader_no_shuffle():
      config = load_config("configs/bgl_tac_full.yaml")
      test_dataset = load_test_dataset(config)
      test_loader = DataLoader(test_dataset, shuffle=False)  # MUST be False
      
      # Verify chronological order maintained
      timestamps = []
      for batch in test_loader:
          timestamps.extend(batch['timestamp'].tolist())
      
      assert timestamps == sorted(timestamps)  # Monotonic increasing
  ```

- [ ] **Run anti-leakage tests**
  ```bash
  pytest tests/test_data_leakage.py -v
  ```

**Checkpoint 4.4**: Anti-leakage tests pass (7/7) ✅

---

### 4.5. Smoke Test: Train 1 Epoch
**Goal**: Verify end-to-end pipeline works before full Phase 4 experiments

- [ ] **Create smoke test script**
  ```bash
  touch scripts/smoke_test_phase3.sh
  ```
  
  ```bash
  #!/bin/bash
  # Smoke test: Train TAC-LAnoBERT for 1 epoch on BGL
  
  echo "=== Phase 3 Smoke Test ==="
  
  # 1. Preprocess with timestamps
  python -m lanobert.preprocess \
      --config configs/bgl_tac_full.yaml \
      --split train \
      --extract_timestamps
  
  # 2. Train 1 epoch
  python -m lanobert.train \
      --config configs/bgl_tac_full.yaml \
      --num_epochs 1 \
      --output_dir outputs/BGL_tac_smoke
  
  # 3. Inference on small test subset
  python -m lanobert.inference \
      --config configs/bgl_tac_full.yaml \
      --checkpoint outputs/BGL_tac_smoke/model/epoch_1 \
      --max_samples 1000
  
  echo "=== Smoke Test Complete ==="
  echo "Check outputs/BGL_tac_smoke/results/ for scores"
  ```

- [ ] **Run smoke test**
  ```bash
  bash scripts/smoke_test_phase3.sh
  ```

- [ ] **Verify outputs**
  - [ ] Training completes without errors
  - [ ] Loss decreases (not NaN/Inf)
  - [ ] Inference produces scores (not all zeros)
  - [ ] Hybrid scores in reasonable range

**Checkpoint 4.5**: Smoke test passes, pipeline functional ✅

---

### 🎯 Exit Criteria Week 4 (Phase 3 Complete)
- ✅ Forward pass succeeds through all 4 modes (baseline, time_only, memory_only, full)
- ✅ No matrix singularity issues (Ledoit-Wolf handles edge cases)
- ✅ Config files load correctly, feature flags work as expected
- ✅ Anti-leakage tests pass (7/7)
- ✅ Smoke test (1 epoch train + inference) completes successfully
- ✅ Ready for Phase 4 full experiments

---

## 📊 Artifacts Created in Phase 3

```
TAC-LAnoBERT/
├── tac_lanobert/
│   ├── __init__.py                 ✅
│   ├── time2vec.py                 ✅ Time2Vec layer
│   ├── time_delta.py               ✅ Timestamp extraction
│   ├── welford.py                  ✅ Online statistics
│   ├── shrinkage.py                ✅ Ledoit-Wolf regularization
│   ├── memory_queue.py             ✅ FIFO + Mahalanobis
│   ├── scoring.py                  ✅ Hybrid scorer
│   └── model.py                    ✅ TAC-LAnoBERT wrapper
├── tests/
│   ├── test_time2vec.py            ✅ Time2Vec unit tests
│   ├── test_welford.py             ✅ Welford accuracy tests
│   ├── test_memory_queue.py        ✅ Memory Queue tests
│   ├── test_integration.py         ✅ End-to-end tests
│   └── test_data_leakage.py        ✅ Anti-leakage verification
├── configs/
│   ├── bgl_tac_full.yaml           ✅ Full TAC config
│   └── ablations/
│       ├── bgl_baseline.yaml       ✅ Baseline (no TAC)
│       ├── bgl_time_only.yaml      ✅ Time2Vec only
│       ├── bgl_memory_only.yaml    ✅ Memory only
│       └── bgl_full_tac.yaml       ✅ Full TAC (same as bgl_tac_full)
├── scripts/
│   └── smoke_test_phase3.sh        ✅ 1-epoch smoke test
└── outputs/
    └── BGL_tac_smoke/              ✅ Smoke test results
        ├── model/epoch_1/
        └── results/
```

---

## 🔄 Rollback Plan

| Issue | Symptom | Fallback |
|---|---|---|
| **Time2Vec gradient vanishing** | ∇ω, ∇φ → 0 | Reduce num_periodic (15 → 5), increase learning rate |
| **Singular covariance** | RuntimeError: singular matrix | Increase LW shrinkage (epsilon regularization) |
| **OOM (VRAM)** | CUDA out of memory | Reduce queue_capacity (128 → 64), gradient checkpointing |
| **Latency > 10ms** | Profiling shows bottleneck | Project [CLS] to lower dim (768 → 256) before Mahalanobis |
| **MLM loss explosion** | Loss → NaN | Clip gradients, reduce Time2Vec contribution (weighted sum) |

---

## 📝 Notes & Reminders

1. **Deterministic Seeds**: Set `PYTHONHASHSEED=0`, `torch.manual_seed(42)` in all scripts
2. **VRAM Monitoring**: Use `nvidia-smi dmon` during smoke test to track memory
3. **Logging**: Add comprehensive logging (DEBUG level) to trace issues
4. **Git Commits**: Commit after each checkpoint (e.g., "Checkpoint 1.1: Time2Vec forward pass")
5. **Documentation**: Update docstrings with paper references (Time2Vec, Ledoit-Wolf)
6. **Kaggle Compatibility**: Test on Kaggle Notebooks after local dev (different PyTorch version)

---

## 🎉 Success Metrics Phase 3

- **Code Quality**: All modules have docstrings, type hints, unit tests
- **Correctness**: Tests verify mathematical correctness (Welford, Mahalanobis)
- **Integration**: Smoke test completes, no runtime errors
- **Flexibility**: Feature flags allow easy ablation study setup
- **Performance**: No obvious latency red flags (detailed profiling in Phase 6)

---

**Next Phase**: Phase 4 — Full Experiments (E1-E3)  
**Duration**: 4 weeks  
**Start Date**: TBD after Phase 3 completion
