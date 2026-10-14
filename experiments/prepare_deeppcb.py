"""Prepare the official DeepPCB lists for Ultralytics YOLO detection.

The official repository stores each inspected image as ``*_test.jpg`` and its
annotation in the matching ``*_not/*.txt`` path.  This script splits the
official 1,000 trainval pairs before augmentation and leaves all 500 official
test pairs untouched.
"""
from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path


def resolve_image(root: Path, listed: str) -> Path:
    rel = Path(listed.split()[0])
    # The manifest names are the pre-registration base name.
    candidate = root / rel
    if candidate.exists():
        return candidate
    candidate = candidate.with_name(candidate.stem + "_test.jpg")
    if candidate.exists():
        return candidate
    raise FileNotFoundError(candidate)


def resolve_label(root: Path, listed: str, image: Path) -> Path:
    fields = listed.split()
    if len(fields) > 1:
        p = root / fields[1]
        if p.exists():
            return p
    p = image.parent.parent / (image.parent.name + "_not") / (image.stem.removesuffix("_test") + ".txt")
    if p.exists():
        return p
    raise FileNotFoundError(p)


def write_item(root: Path, out: Path, listed: str) -> None:
    image = resolve_image(root, listed)
    label = resolve_label(root, listed, image)
    dst_image = out / "images" / (image.stem + ".jpg")
    dst_label = out / "labels" / (image.stem + ".txt")
    dst_image.parent.mkdir(parents=True, exist_ok=True)
    dst_label.parent.mkdir(parents=True, exist_ok=True)
    # Symlinks keep the preparation small and retain the official pixels.
    if not dst_image.exists():
        dst_image.symlink_to(image.resolve())
    if not dst_label.exists():
        lines = []
        for row in label.read_text().splitlines():
            x1, y1, x2, y2, cls = map(int, row.split()[:5])
            w, h = 640.0, 640.0
            lines.append(f"{cls-1} {(x1+x2)/(2*w):.8f} {(y1+y2)/(2*h):.8f} {(x2-x1)/w:.8f} {(y2-y1)/h:.8f}")
        dst_label.write_text("\n".join(lines) + ("\n" if lines else ""))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True, help="DeepPCB/PCBData directory")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--val-count", type=int, default=200)
    args = ap.parse_args()
    root = args.source
    trainval = (root / "trainval.txt").read_text().splitlines()
    test = (root / "test.txt").read_text().splitlines()
    if len(trainval) != 1000 or len(test) != 500:
        raise ValueError(f"unexpected official list sizes: trainval={len(trainval)} test={len(test)}")
    rng = random.Random(args.seed)
    order = list(range(len(trainval)))
    rng.shuffle(order)
    val_idx = set(order[: args.val_count])
    splits = {"train": [x for i, x in enumerate(trainval) if i not in val_idx],
              "val": [x for i, x in enumerate(trainval) if i in val_idx],
              "test": test}
    if args.out.exists():
        shutil.rmtree(args.out)
    for name, rows in splits.items():
        for row in rows:
            write_item(root, args.out / name, row)
        (args.out / f"{name}.txt").write_text("\n".join(rows) + "\n")
    print({k: len(v) for k, v in splits.items()})


if __name__ == "__main__":
    main()
