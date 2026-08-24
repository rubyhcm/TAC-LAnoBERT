"""MLM-only dataset for LAnoBERT.

The original implementation reused HuggingFace's
`TextDatasetForNextSentencePrediction`, which builds NSP pairs. LAnoBERT does
**not** use next-sentence prediction -- each log line is an independent example
and the only objective is masked-language-modeling. This module therefore
treats one normalized log line as one example, which is simpler, faster, and
matches the paper.

TAC-LAnoBERT Extension:
- Optionally loads timestamps and computes delta_t for Time2Vec embedding
"""
from __future__ import annotations

import os
from typing import List, Optional
import numpy as np

import torch
from torch.utils.data import Dataset


class LogLineDataset(Dataset):
    """One normalized log line -> one tokenized example (no NSP).

    Args:
        tokenizer: a fast BERT tokenizer.
        file_path: path to a newline-delimited normalized corpus.
        max_len: max sequence length (longer lines are truncated).
        skip_empty: drop blank lines.
        use_time2vec: if True, load timestamps and compute delta_t
        log_format: log format for timestamp extraction ('bgl', 'thunderbird', 'hdfs')
    """

    def __init__(
        self, 
        tokenizer, 
        file_path: str, 
        max_len: int = 512, 
        skip_empty: bool = True,
        use_time2vec: bool = False,
        log_format: str = "bgl",
    ):
        assert os.path.isfile(file_path), f"Input file not found: {file_path}"
        self.max_len = max_len
        self.use_time2vec = use_time2vec

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f]
        if skip_empty:
            lines = [ln for ln in lines if ln]

        # Pre-tokenize all lines once so __getitem__ is just an index lookup.
        print(f"[dataset] pre-tokenizing {len(lines):,} lines...")
        batch_enc = tokenizer(
            lines,
            truncation=True,
            max_length=max_len,
            return_special_tokens_mask=True,
        )
        self.input_ids: List[List[int]] = batch_enc["input_ids"]
        self.attention_mask: List[List[int]] = batch_enc["attention_mask"]
        self.special_tokens_mask: List[List[int]] = batch_enc["special_tokens_mask"]
        print(f"[dataset] pre-tokenization done.")

        # Load timestamps if Time2Vec is enabled
        self.delta_t: Optional[List[float]] = None
        if use_time2vec:
            self._load_timestamps(file_path, log_format)

    def _load_timestamps(self, file_path: str, log_format: str):
        """Load timestamps and compute delta_t."""
        # Try to load from .timestamps sidecar file (strip any extension, add .timestamps)
        base_path = os.path.splitext(file_path)[0]
        timestamp_path = base_path + ".timestamps"
        
        if os.path.isfile(timestamp_path):
            print(f"[dataset] loading timestamps from {timestamp_path}")
            with open(timestamp_path, "r", encoding="utf-8") as f:
                timestamps = [float(line.strip()) for line in f if line.strip()]
            
            if len(timestamps) != len(self.input_ids):
                print(f"[dataset] WARNING: timestamp count mismatch: "
                      f"{len(timestamps)} vs {len(self.input_ids)} lines")
                # Pad or truncate
                if len(timestamps) < len(self.input_ids):
                    timestamps.extend([0.0] * (len(self.input_ids) - len(timestamps)))
                else:
                    timestamps = timestamps[:len(self.input_ids)]
        else:
            # Extract timestamps on-the-fly from raw file
            print(f"[dataset] .timestamps file not found, extracting on-the-fly...")
            # Find corresponding raw file
            raw_path = file_path.replace("_normal.txt", "_raw.txt").replace("_log.txt", "_raw.txt")
            
            if not os.path.isfile(raw_path):
                print(f"[dataset] WARNING: raw file not found at {raw_path}, using zero delta_t")
                timestamps = [0.0] * len(self.input_ids)
            else:
                from tac_lanobert.time_delta import extract_timestamps_from_file
                timestamps, _ = extract_timestamps_from_file(raw_path, log_format=log_format)
                
                # Match length
                if len(timestamps) != len(self.input_ids):
                    if len(timestamps) < len(self.input_ids):
                        timestamps.extend([0.0] * (len(self.input_ids) - len(timestamps)))
                    else:
                        timestamps = timestamps[:len(self.input_ids)]
        
        # Compute delta_t (normalized)
        from tac_lanobert.time_delta import TimestampExtractor
        extractor = TimestampExtractor(log_format=log_format)
        
        delta_t_list = []
        for ts in timestamps:
            delta_ms = extractor.compute_delta_t(ts if ts > 0 else None)
            delta_norm = TimestampExtractor.normalize_delta_t(delta_ms)
            delta_t_list.append(delta_norm)
        
        self.delta_t = delta_t_list
        print(f"[dataset] computed {len(self.delta_t)} delta_t values (range: "
              f"{min(self.delta_t):.4f} to {max(self.delta_t):.4f})")

    def __len__(self) -> int:
        return len(self.input_ids)

    def __getitem__(self, idx: int):
        # Return plain lists so DataCollatorForLanguageModeling can
        # dynamically pad each batch to its longest sequence instead of
        # always padding to max_len.
        item = {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "special_tokens_mask": self.special_tokens_mask[idx],
        }
        
        # Add delta_t for Time2Vec if enabled
        if self.use_time2vec and self.delta_t is not None:
            # Replicate delta_t for each token in the sequence
            seq_len = len(self.input_ids[idx])
            item["delta_t"] = [self.delta_t[idx]] * seq_len  # Same delta_t for all tokens in line
        
        return item


def read_lines(file_path: str, limit: int | None = None) -> List[str]:
    """Utility: read normalized lines from a corpus, optionally capped at `limit`."""
    out: List[str] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(ln)
            if limit is not None and len(out) >= limit:
                break
    return out
