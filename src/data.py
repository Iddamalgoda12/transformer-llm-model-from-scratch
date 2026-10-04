"""Read prepared token data and draw next-token batches."""

from pathlib import Path

import numpy as np
import torch


def load_tokens(path: Path) -> torch.Tensor:
    # Prepared IDs are stored as uint16; convert to the signed type embeddings require.
    return torch.from_numpy(np.fromfile(path, dtype=np.uint16).astype(np.int64))


def get_batch(data: torch.Tensor, batch_size: int, block_size: int, device: torch.device):
    starts = torch.randint(len(data) - block_size - 1, (batch_size,))
    offsets = torch.arange(block_size)
    positions = starts[:, None] + offsets[None, :]
    x = data[positions]
    y = data[positions + 1]
    return x.to(device), y.to(device)
