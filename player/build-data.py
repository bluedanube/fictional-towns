#!/usr/bin/env python3
"""script/*.json を player/script-data.js にまとめる。file:// で開くための埋め込み用。
台本を直したら、このスクリプトを再実行する: python3 player/build-data.py"""
import glob, json, os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
chapters = []
for f in sorted(glob.glob(os.path.join(root, "script", "ch*.json"))):
    with open(f, encoding="utf-8") as fh:
        chapters.append(json.load(fh))
roster = []
rp = os.path.join(root, "script", "roster.json")
if os.path.exists(rp):
    with open(rp, encoding="utf-8") as fh:
        roster = json.load(fh).get("girls", [])
out = os.path.join(root, "player", "script-data.js")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("window.NOVEL = " + json.dumps({"chapters": chapters, "roster": roster}, ensure_ascii=False) + ";\n")
print("wrote", out, len(chapters), "chapters")
