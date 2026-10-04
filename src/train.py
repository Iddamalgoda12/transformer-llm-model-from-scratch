"""Train the model on the included toy corpus."""

import argparse
import tomllib
from pathlib import Path

import torch
from tqdm import trange
from tokenizers import Tokenizer

from src.data import get_batch, load_tokens
from src.model import TinyGPT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/tiny.toml"))
    parser.add_argument("--steps", type=int, default=None)
    args = parser.parse_args()
    config = tomllib.loads(args.config.read_text())
    model_cfg, train_cfg = config["model"], config["training"]
    steps = args.steps or train_cfg["steps"]
    torch.manual_seed(train_cfg["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}; CUDA available: {torch.cuda.is_available()}")
    model = TinyGPT(**model_cfg).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=train_cfg["learning_rate"], weight_decay=train_cfg["weight_decay"]
    )
    train_data = load_tokens(Path("data/train.bin"))
    val_data = load_tokens(Path("data/val.bin"))
    tokenizer = Tokenizer.from_file("data/tokenizer.json")

    @torch.no_grad()
    def estimate_loss():
        model.eval()
        results = {}
        for name, split_data in (("train", train_data), ("val", val_data)):
            losses = torch.empty(train_cfg["eval_batches"])
            for index in range(len(losses)):
                x, y = get_batch(split_data, train_cfg["batch_size"], model.block_size, device)
                _, loss = model(x, y)
                losses[index] = loss.item()
            results[name] = losses.mean().item()
        model.train()
        return results

    model.train()
    for step in trange(steps, desc="training"):
        x, y = get_batch(train_data, train_cfg["batch_size"], model.block_size, device)
        _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if (step + 1) % train_cfg["eval_interval"] == 0 or step == 0:
            losses = estimate_loss()
            print(
                f"step {step + 1}: batch {loss.item():.4f}, "
                f"train {losses['train']:.4f}, val {losses['val']:.4f}"
            )
    Path("checkpoints").mkdir(exist_ok=True)
    torch.save({"model": model.state_dict(), "config": model_cfg}, "checkpoints/tiny.pt")
    model.eval()
    prompt = tokenizer.encode("ROMEO:").ids
    sample = model.generate(torch.tensor([prompt], dtype=torch.long, device=device), 160)
    print("Sample:\n" + tokenizer.decode(sample[0].tolist()))
    print("Checkpoint saved to checkpoints/tiny.pt")


if __name__ == "__main__":
    main()
