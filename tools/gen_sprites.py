#!/usr/bin/env python3
"""立ち絵をAPIで並列生成する（OpenAI Images API / edits）。

使い方（Mac のターミナルで）:
  pip3 install openai pillow
  export OPENAI_API_KEY="（自分のキー。チャットには貼らない）"
  python3 gen_sprites.py --list-models
  python3 gen_sprites.py --model <モデル名> --only toki --dry-run
  python3 gen_sprites.py --model <モデル名> --only toki --phase base
  python3 gen_sprites.py --model <モデル名> --only toki --phase faces

段階:
  base  : 各少女の「通常姿・真顔」「魔法少女姿・真顔」を作る（参照：原図の表＋場面画像）
  faces : base を参照にして、微笑・目を伏せる、を作る（顔以外は変えない）
出力: ../out/sprites_raw/<ID>-<romaji>/<pose>_<face>.png （緑背景。透過加工は後工程）
"""
import argparse, base64, io, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
IMG = ROOT / "assets" / "images"
OUT = ROOT / "out" / "sprites_raw"

# id, romaji, 飾り, 原図(表), 場面画像, 場面の姿
GIRLS = {
    "toki":  ("U3C-01",  "時計帽", "u-town-3-magical-girls/views/U3C-01-toki-front.webp",  "sewn-town/01-toki-rocket.webp",   "normal"),
    "rabi":  ("U3V2-03", "うさぎ頭巾", "u-town-3-magical-girls/views/U3V2-03-rabi-front.webp", "sewn-town/02-rabi-playground.webp", "normal"),
    "ruri":  ("U3C-08",  "丸ゴーグル", "u-town-3-magical-girls/views/U3C-08-ruri-front.webp",  "sewn-town/03-ruri-platform.webp", "normal"),
    "hoshi": ("U3V2-01", "星帽子", "u-town-3-magical-girls/views/U3V2-01-hoshi-front.webp", "sewn-town/04-hoshi-green.webp",    "magic"),
    "mio":   ("U3C-03",  "三日月帽", "u-town-3-magical-girls/views/U3C-03-mio-front.webp",   "sewn-town/05-mio-bridge.webp",    "magic"),
    "nui":   ("U3V2-07", "つぎはぎ帽", "u-town-3-magical-girls/views/U3V2-07-nui-front.webp",  "sewn-town/06-nui-alley.webp",     "magic"),
    "kii":   ("F2C-02",  "鍵飾り", "f-town-2-magical-girls/views/F2C-02-kii-front.webp",    "sewn-town/07-kii-saiseikan-v2.webp", "magic"),
    "lila":  ("F2C-14",  "船形帽", "f-town-2-magical-girls/views/F2C-14-lila-front.webp",   "sewn-town/08-lila-bench.webp",    "magic"),
}
POSES = {"normal": "通常姿（持ち物を足さない）", "magic": "魔法少女姿（原図の小さな魔法の道具を保つ）"}
FACES = {"neutral": "真顔", "smile": "控えめな微笑", "downcast": "目を伏せる"}

COMMON = """条件：
- 同じ少女であること。顔立ち、髪、体つき、年齢の見た目、布のざらりとした質感、絵のタッチを参照画像と揃える。
- 飾りは{ornament}。{ornament_note}
- 全身、正面向き、足先まで入れる。縦長（2:3）。
- 背景は単色の緑 #00FF00 のみ。影、床、模様、グラデーション、文字は入れない。
- 少女の輪郭に緑がにじまないよう、服や髪に緑系の色を使わない。
- 全体に静かな雰囲気。笑いすぎず、泣かない。"""

def ornament_note(key):
    if key == "toki":
        return "時計の文字盤は、針を読み取れない曖昧な描き方にする。時刻を示す絵にしない。"
    return "原図どおりの形にする。"

def prompt_base(key, pose, face):
    gid, orn, *_ = GIRLS[key]
    return (f"添付した参照画像の少女「{key}」を、サウンドノベルの立ち絵として描いてください。\n"
            f"【姿】{POSES[pose]}\n【表情】{FACES[face]}\n\n"
            + COMMON.format(ornament=orn, ornament_note=ornament_note(key)))

def prompt_face(key, pose, face):
    gid, orn, *_ = GIRLS[key]
    return ("1枚目の画像（基準）と、まったく同じ少女・同じ服・同じ姿勢・同じ腕の位置・同じ画面内の位置と大きさで、"
            f"表情だけを「{FACES[face]}」に変えてください。顔の表情以外は1ピクセルも変えないつもりで描く。\n\n"
            + COMMON.format(ornament=orn, ornament_note=ornament_note(key)))

def load_png(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    buf = io.BytesIO(); bg.convert("RGB").save(buf, "PNG")
    return ("ref.png", buf.getvalue(), "image/png")

def out_path(key, pose, face):
    return OUT / f"{GIRLS[key][0]}-{key}" / f"{pose}_{face}.png"

def build_jobs(keys, phase):
    jobs = []
    for k in keys:
        gid, orn, front, scene, scene_pose = GIRLS[k]
        for pose in POSES:
            if phase in ("base", "all"):
                refs = [IMG / front, IMG / scene]
                jobs.append((k, pose, "neutral", refs, prompt_base(k, pose, "neutral")))
            if phase in ("faces", "all"):
                for face in ("smile", "downcast"):
                    refs = [out_path(k, pose, "neutral"), IMG / front]
                    jobs.append((k, pose, face, refs, prompt_face(k, pose, face)))
    return jobs

def run_job(client, args, job):
    k, pose, face, refs, prompt = job
    dst = out_path(k, pose, face)
    if dst.exists() and not args.force:
        return dst, "skip"
    for r in refs:
        if not Path(r).exists():
            return dst, f"missing ref: {r}"
    files = [load_png(r) for r in refs]
    delay = 5
    for attempt in range(5):
        try:
            kw = dict(model=args.model, image=files, prompt=prompt, size=args.size, n=1)
            if args.quality:
                kw["quality"] = args.quality
            res = client.images.edit(**kw)
            b = base64.b64decode(res.data[0].b64_json)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(b)
            return dst, "ok"
        except Exception as e:  # 429 / 接続エラーは待って再試行。それ以外は即座に報告
            name = type(e).__name__
            if name in ("RateLimitError", "APIConnectionError", "APITimeoutError", "InternalServerError") and attempt < 4:
                time.sleep(delay); delay *= 2; continue
            return dst, f"error {name}: {str(e)[:300]}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--only", help="カンマ区切り（例 toki,rabi）。省略で8人全員")
    ap.add_argument("--phase", choices=["base", "faces", "all"], default="base")
    ap.add_argument("--size", default="1024x1536")
    ap.add_argument("--quality", default="medium", help="low/medium/high（モデルが対応していれば）")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list-models", action="store_true")
    args = ap.parse_args()

    if args.list_models:
        from openai import OpenAI
        for m in sorted(x.id for x in OpenAI().models.list() if "image" in x.id):
            print(m)
        return
    if not args.model:
        sys.exit("--model が必要です。先に --list-models で使えるモデル名を確認してください。")
    keys = args.only.split(",") if args.only else list(GIRLS)
    bad = [k for k in keys if k not in GIRLS]
    if bad: sys.exit(f"不明な名前: {bad}。使えるのは {list(GIRLS)}")
    jobs = build_jobs(keys, args.phase)
    print(f"{len(jobs)} 枚（model={args.model}, size={args.size}, quality={args.quality}, workers={args.workers}）")
    if args.dry_run:
        for k, pose, face, refs, p in jobs:
            print(f"- {out_path(k,pose,face).relative_to(ROOT)}  refs={[Path(r).name for r in refs]}")
        print("\n--- 1枚目のプロンプト ---\n" + jobs[0][4]); return
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("環境変数 OPENAI_API_KEY がありません。")
    from openai import OpenAI
    client = OpenAI(timeout=300)
    t0 = time.time(); done = 0; lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_job, client, args, j): j for j in jobs}
        for f in as_completed(futs):
            dst, st = f.result()
            with lock:
                done += 1
                print(f"[{done}/{len(jobs)}] {dst.relative_to(ROOT)}  {st}  ({time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
