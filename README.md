# Tiny Transformer Lab

A compact, from-scratch decoder-only Transformer project. Prepare the small
Tiny Shakespeare corpus and train a byte-level BPE tokenizer locally, then train
the model on next-token prediction. The current NVIDIA driver did not respond,
so training will use CPU unless `torch.cuda.is_available()` is true.

The default install uses the CPU-only PyTorch wheel to keep setup small. After
installing a working Fedora NVIDIA driver, remove the `torch` source/index
override from `pyproject.toml` and run `uv sync` to let PyTorch select a platform
wheel that matches the available GPU setup.

## Quick start (Fedora)

```bash
uv sync
uv run python -m src.prepare_data
uv run python -m src.train --steps 100
```

## Layout

- `src/model.py`: causal attention, MLP, residual blocks, and language model.
- `src/prepare_data.py`: corpus download, train/validation split, and BPE training.
- `src/data.py`: token data loading and next-token batches.
- `src/train.py`: training loop and checkpoint saving.
- `configs/tiny.toml`: model and optimizer defaults.
- `tests/`: model shape checks.

The implementation uses pre-normalization, GELU, learned token/position
embeddings, AdamW, gradient clipping, and PyTorch scaled dot-product attention.
It is a teaching baseline; production training adds substantial data, evaluation,
precision, and distributed systems work.
