# 試作プレーヤー（サウンドノベル／絵本）

`player/index.html` をブラウザで開くだけで動く（サーバー不要、`file://` 可）。外部ライブラリなし。

## 台本の読み込み
1. `player/script-data.js`（`script/ch*.json` と `roster.json` をまとめたもの）があればそれを使う。
2. 無ければ `../script/ch*.json` を fetch する（http で配信したときだけ動く）。
3. どちらも読めなければ `player/sample/sample.js` のダミー台本。

**台本を直したら**、次を再実行して `script-data.js` を作り直す：
```
python3 player/build-data.py
```

## 操作
| 操作 | 内容 |
|---|---|
| クリック／タップ／Enter／Space／→ | 次へ（表示中は全文表示） |
| Backspace／← | 戻る |
| L／「ログ」 | ログ表示 |
| B／「絵本」 | 絵本表示（←→で章送り） |
| 「章」 | 章の選択 |
| Esc | 閉じる |

URL：`index.html?ch=4`（または `#ch04`）でその章から、`?book=1` で絵本表示から始める。`?roster=1` で名簿ボタンを出し、終了時に名簿を開く（確認用）。`?debug=1` で左上に BGM／SE 名を出す（既定では出さない）。

## 画面
- 背景全面、立ち絵（`pos`: left／center／right）、下部のテキスト窓、住人は窓内の小アイコン。文字は1文字ずつ表示。
- 素材が無い、または `missing: true` の行・シーンは、仮の枠と文字で出す。
  - 背景：`../assets/images/<bg>.webp`
  - 立ち絵：`../assets/sprites/<ID>-<romaji>/<pose>_<face>.webp`（romaji は `index.html` 内の表。8人分）
  - 住人：`../assets/images/u-town-3-residents/<ID>.gif`（F町住人は未作成のため仮枠）
- 音：`bgm`／`se` の名前を画面左上に出す。`../assets/audio/bgm/<名>.ogg`、`../assets/audio/se/<名>.ogg` があれば鳴らし、無ければ無音。
- スマホ縦持ちでは、絵本表示は縦並びになる。

## 選択肢と「糸」
`choice.enabled: true` のシーン末尾で選択肢を出し、`thread` を加算する。既定の台本は全章 `false`。糸が8本たまると、最後に名簿（`roster.json`）が開く。

## 絵本表示
章ごとに1見開き：左に背景、右に `book: true` の行だけを並べる。

## 確認したこと
- Chromium で `file://` から全10章を最後まで通した（エラーなし）。戻る・ログ・絵本・章選択も確認。
- スマホ幅（390×844）で横スクロールなし。
- 選択肢は、検証用に全章有効にした一時コピーで動作確認（糸9本で名簿34人が開く）。
- スクリーンショット：`player/screens/`
