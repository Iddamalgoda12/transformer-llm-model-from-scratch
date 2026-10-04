"""Readable decoder-only Transformer implemented with PyTorch."""

import torch
from torch import nn
from torch.nn import functional as F


class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd: int, n_head: int, dropout: float) -> None:
        super().__init__()
        if n_embd % n_head:
            raise ValueError("n_embd must be divisible by n_head")
        self.attn = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.proj = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        self.n_head = n_head
        self.head_dim = n_embd // n_head

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, length, channels = x.shape
        q, k, v = self.attn(x).split(channels, dim=-1)
        shape = (batch, length, self.n_head, self.head_dim)
        q, k, v = (t.view(shape).transpose(1, 2) for t in (q, k, v))
        y = F.scaled_dot_product_attention(
            q, k, v, is_causal=True, dropout_p=self.attn_dropout.p if self.training else 0.0
        )
        y = y.transpose(1, 2).contiguous().view(batch, length, channels)
        return self.resid_dropout(self.proj(y))


class Block(nn.Module):
    def __init__(self, n_embd: int, n_head: int, dropout: float) -> None:
        super().__init__()
        self.ln_1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, dropout)
        self.ln_2 = nn.LayerNorm(n_embd)
        self.mlp = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd), nn.GELU(), nn.Linear(4 * n_embd, n_embd), nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln_1(x))
        return x + self.mlp(self.ln_2(x))


class TinyGPT(nn.Module):
    def __init__(self, vocab_size=256, block_size=128, n_embd=128, n_head=4, n_layer=4, dropout=0.1):
        super().__init__()
        self.block_size = block_size
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.dropout = nn.Dropout(dropout)
        self.blocks = nn.Sequential(*(Block(n_embd, n_head, dropout) for _ in range(n_layer)))
        self.final_norm = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, idx: torch.Tensor, targets: torch.Tensor | None = None):
        _, length = idx.shape
        if length > self.block_size:
            raise ValueError(f"sequence length {length} exceeds block_size {self.block_size}")
        positions = torch.arange(length, device=idx.device)
        x = self.dropout(self.token_embedding(idx) + self.position_embedding(positions))
        logits = self.lm_head(self.final_norm(self.blocks(x)))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int, temperature: float = 1.0):
        if temperature <= 0:
            raise ValueError("temperature must be positive")
        for _ in range(max_new_tokens):
            logits, _ = self(idx[:, -self.block_size :])
            probs = F.softmax(logits[:, -1, :] / temperature, dim=-1)
            idx = torch.cat((idx, torch.multinomial(probs, num_samples=1)), dim=1)
        return idx
