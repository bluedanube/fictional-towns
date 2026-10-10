# 台本データ形式（サウンドノベル／絵本 共通）

状態：提案（骨子案の決定事項に基づく。細部は試作で調整）

## ファイル配置
```
script/
  ch00.json  (序)  ch01.json … ch08.json  ch99.json (終)
  roster.json      (名簿：残り34人。魔法の文は notes/magical-girls.md のまま)
assets/
  images/sewn-town/        背景（既存8枚＋新規2枚）
  images/u-town-3-residents/ , f-town-2-residents/   住人アイコン（小窓用）
  sprites/<ID>-<name>/<pose>_<face>.webp   立ち絵（緑背景で作り、透過に加工）
    例 sprites/U3C-01-toki/normal_neutral.webp
```
- pose：`normal`（通常姿） / `magic`（魔法少女姿）
- face：`neutral`（真顔） / `smile`（控えめな微笑） / `downcast`（目を伏せる）

## 章ファイル
```json
{
  "id": "ch01",
  "title": "夜を待つロケット",
  "girl": "U3C-01",
  "status": "draft",
  "scenes": [
    {
      "bg": "sewn-town/01-toki-rocket",
      "time": "dusk",
      "bgm": null,
      "se": ["water-low"],
      "lines": [
        { "who": "narr", "text": "…", "book": true },
        { "who": "U3C-01", "sprite": {"pose": "normal", "face": "neutral", "pos": "center"}, "text": "…" },
        { "who": "U3-01", "icon": "U3-01", "text": "…" }
      ],
      "choice": { "enabled": false, "prompt": "", "options": [] }
    }
  ]
}
```
- `who`：`narr`（語り＝「わたし」）、少女は魔法少女ID、住人は住人ID。
- `time`：`dusk` / `night`。背景の昼夜差分の切り替えに使う。
- `bgm` / `se`：名前だけ書く（音源は後から）。未定は `null`。
- `book: true`：絵本にする場合に見開きへ載せる行。1章あたり3〜5行。
- `choice.enabled`：最初は `false`。有効にする場合、`options` に `label`、`thread`（糸の数）、`lines` を書く。
- 欠けた素材（未作成の画像）は、`"missing": true` を付けてよい。プレーヤーは仮の枠を出す。背景そのものが未作成のときは、シーンに `"bg_missing": true` を付ける（`missing` には統一しない）。

## 禁止事項（点検の対象）
- 約束の相手の姿・名前・年齢・性別、声。
- 留保6点の決定（`notes/soundnovel-outline.md` 6を参照）。
- 実在の地名。少女の名前・飾り・魔法の変更。
- 悲劇・恐怖・責任追及の描写。
