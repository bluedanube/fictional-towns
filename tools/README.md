# 立ち絵のAPI並列生成

`gen_sprites.py` は、OpenAI Images API で8人分の立ち絵（通常姿・魔法少女姿 × 真顔・微笑・目を伏せる）を並列に作る。

## 準備（初回のみ）
1. OpenAI のAPIキーを用意する（ChatGPTの契約とは別の課金）。組織の確認（Organization Verification）が必要な場合がある。ダッシュボードで月の上限額を先に決めておく。
2. ターミナルで:
   ```
   pip3 install openai pillow
   export OPENAI_API_KEY="（自分のキー）"   # チャットやファイルには貼らない
   cd ~/Desktop/soundnovel-test/tools
   python3 gen_sprites.py --list-models     # 使える画像モデル名を確認
   ```

## 試作（トキ1人）
```
python3 gen_sprites.py --model <モデル名> --only toki --dry-run     # 内容の確認（課金なし）
python3 gen_sprites.py --model <モデル名> --only toki --phase base  # 基準2枚（通常姿/魔法少女姿）
python3 gen_sprites.py --model <モデル名> --only toki --phase faces # 表情差分4枚（基準を参照）
```
出力は `../out/sprites_raw/U3C-01-toki/`。仕上がりを見てから全員へ:
```
python3 gen_sprites.py --model <モデル名> --phase base
python3 gen_sprites.py --model <モデル名> --phase faces
```
- `--quality low|medium|high`（既定 medium）、`--workers 4`（並列数。429が出たら減らす）、`--force`（作り直し）。
- 既にあるファイルは飛ばすので、途中で止まっても再実行できる。

## 後工程
緑背景の透過加工、WebP化、`assets/sprites/` への配置は、出力フォルダを教えてもらえれば Claude 側で行う。
