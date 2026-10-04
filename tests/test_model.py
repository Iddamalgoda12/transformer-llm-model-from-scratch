import torch

from src.model import TinyGPT


def test_forward_shapes_and_loss():
    model = TinyGPT(vocab_size=32, block_size=8, n_embd=16, n_head=4, n_layer=2)
    x = torch.randint(0, 32, (2, 8))
    logits, loss = model(x, x)
    assert logits.shape == (2, 8, 32)
    assert loss is not None and torch.isfinite(loss)


def test_rejects_overlong_input():
    model = TinyGPT(vocab_size=32, block_size=8, n_embd=16, n_head=4, n_layer=2)
    try:
        model(torch.zeros((1, 9), dtype=torch.long))
    except ValueError as exc:
        assert "exceeds block_size" in str(exc)
    else:
        raise AssertionError("expected overlong input to fail")
