// 同梱のダミー台本。script/ が読めないときだけ使う。
window.SAMPLE = { chapters: [{
  id: "sample", title: "ダミー台本", girl: "U3C-01", status: "draft",
  scenes: [{
    bg: "sewn-town/01-toki-rocket", time: "dusk", bgm: null, se: ["water-low"],
    lines: [
      { who: "narr", text: "これはダミーの台本です。script/ のファイルが読めなかったときに表示されます。", book: true },
      { who: "U3C-01", sprite: { pose: "normal", face: "smile", pos: "center" }, text: "「立ち絵が無いときは、仮の枠が出るよ」", missing: true, book: true },
      { who: "U3-01", icon: "U3-01", text: "「住人は小窓で出ます」", book: true },
      { who: "narr", text: "「また、あした。」" }
    ],
    choice: { enabled: false, prompt: "", options: [] }
  }]
}], roster: [] };
