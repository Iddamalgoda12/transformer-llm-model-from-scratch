"""Download Tiny Shakespeare and train a small byte-level BPE tokenizer."""

import argparse
import urllib.request
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

DATA_DIR = Path("data")
TEXT_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vocab-size", type=int, default=2048)
    args = parser.parse_args()
    DATA_DIR.mkdir(exist_ok=True)
    text_path = DATA_DIR / "tinyshakespeare.txt"
    tokenizer_path = DATA_DIR / "tokenizer.json"

    if not text_path.exists():
        print(f"Downloading Tiny Shakespeare from {TEXT_URL}")
        request = urllib.request.Request(TEXT_URL, headers={"User-Agent": "tiny-transformer-lab/0.1"})
        with urllib.request.urlopen(request, timeout=30) as response:
            text_path.write_bytes(response.read())
    text = text_path.read_text(encoding="utf-8")
    split = int(len(text) * 0.9)
    train_text, val_text = text[:split], text[split:]

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=args.vocab_size,
        min_frequency=2,
        special_tokens=["<unk>", "<|endoftext|>"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=True,
    )
    chunks = (train_text[i : i + 10000] for i in range(0, len(train_text), 10000))
    tokenizer.train_from_iterator(chunks, trainer)
    tokenizer.save(str(tokenizer_path))
    eos_id = tokenizer.token_to_id("<|endoftext|>")

    for name, part in (("train", train_text), ("val", val_text)):
        ids = tokenizer.encode(part).ids
        ids.append(eos_id)
        np.asarray(ids, dtype=np.uint16).tofile(DATA_DIR / f"{name}.bin")
        print(f"{name}: {len(ids):,} tokens")
    print(f"Tokenizer vocabulary: {tokenizer.get_vocab_size():,}")
    print(f"Prepared files in {DATA_DIR}/")


if __name__ == "__main__":
    main()
