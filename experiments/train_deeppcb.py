"""Train and evaluate a reproducible DeepPCB YOLO11 experiment."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from ultralytics import YOLO


NAMES = ["open", "short", "mousebite", "spur", "copper", "pin-hole"]


def make_data_yaml(root: Path) -> Path:
    p = root / "deeppcb.yaml"
    p.write_text("\n".join([
        f"path: {root.resolve()}", "train: train/images", "val: val/images", "test: test/images",
        "names:", *[f"  {i}: {name}" for i, name in enumerate(NAMES)], ""
    ]))
    return p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--model", choices=("baseline", "p2"), default="baseline")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--imgsz", type=int, default=320)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--project", type=Path, default=Path("runs/deeppcb"))
    args = ap.parse_args()
    data = make_data_yaml(args.data)
    if args.model == "p2":
        model = YOLO(str(Path(__file__).parent / "yolo11n-p2.yaml"))
        # Transfer matching backbone and three standard head tensors; the new
        # P2 path remains randomly initialized and is reported as such.
        model.load("yolo11n.pt")
    else:
        model = YOLO("yolo11n.pt")
    run_name = f"{args.model}_e{args.epochs}_s{args.seed}"
    result = model.train(data=str(data), epochs=args.epochs, imgsz=args.imgsz, batch=args.batch,
                         workers=args.workers, seed=args.seed, deterministic=True, device="cpu",
                         project=str(args.project), name=run_name, cache=False,
                         plots=True, verbose=True, pretrained=False)
    best = Path(result.save_dir) / "weights" / "best.pt"
    test = YOLO(str(best)).val(data=str(data), split="test", imgsz=args.imgsz, batch=args.batch,
                               device="cpu", workers=args.workers, plots=True,
                               project=str(args.project), name=run_name + "_test")
    summary = {
        "model": args.model, "epochs": args.epochs, "imgsz": args.imgsz,
        "seed": args.seed, "best": str(best), "results_dir": str(result.save_dir),
        "metrics": {"mAP50": float(test.box.map50), "mAP50_95": float(test.box.map),
                    "precision": float(test.box.mp), "recall": float(test.box.mr),
                    "per_class_ap50": [float(x) for x in test.box.ap50]},
    }
    out = Path(result.save_dir) / "test_metrics.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
