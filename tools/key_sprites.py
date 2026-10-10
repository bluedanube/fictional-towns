#!/usr/bin/env python3
"""緑背景(#00FF00)の立ち絵PNGを、透過WebPにする。

使い方:  python3 key_sprites.py <入力フォルダ(out)> <出力フォルダ(assets/sprites)> [--width 768]
  入力: <入力>/<ID>-<name>/<pose>_<face>.png  →  出力: <出力>/<ID>-<name>/<pose>_<face>.webp
処理: 緑の度合いからアルファを作り、縁の緑のにじみを取り除く（despill＋色の復元）。
"""
import sys, argparse
from pathlib import Path
import numpy as np
from PIL import Image

def key(im, lo=30.0, hi=190.0):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = g - np.maximum(r, b)                      # 背景ほど大きい
    alpha = 1.0 - np.clip((green - lo) / (hi - lo), 0.0, 1.0)
    # 背景色(0,255,0)との混色を戻す: c = a*fg + (1-a)*bg
    bg = np.array([0.0, 255.0, 0.0], dtype=np.float32)
    al = np.maximum(alpha, 1e-3)[..., None]
    fg = (a - (1.0 - alpha)[..., None] * bg) / al
    fg = np.clip(fg, 0, 255)
    # despill: 緑が赤・青より突出している分を抑える
    fg[..., 1] = np.minimum(fg[..., 1], np.maximum(fg[..., 0], fg[..., 2]) + 6)
    alpha[alpha < 0.02] = 0.0
    out = np.dstack([fg, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--quality", type=int, default=90)
    args = ap.parse_args()
    n = 0
    for p in sorted(Path(args.src).glob("*/*.png")):
        im = key(Image.open(p))
        if args.width and im.width != args.width:
            h = round(im.height * args.width / im.width)
            im = im.resize((args.width, h), Image.LANCZOS)
        d = Path(args.dst) / p.parent.name / (p.stem + ".webp")
        d.parent.mkdir(parents=True, exist_ok=True)
        im.save(d, "WEBP", quality=args.quality, alpha_quality=100, method=6)
        n += 1
        print(f"{d}  {d.stat().st_size//1024}KB")
    print(f"{n} files")

if __name__ == "__main__":
    main()
