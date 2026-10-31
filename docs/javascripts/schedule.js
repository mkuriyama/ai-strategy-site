/*
 * 回の予定の表示を、いまの時刻に合わせて付け直す。
 *
 * サイトは main へのマージでしか作り直されない。開催日が過ぎても次のビルドまで「次回 11/6」が
 * 残り、終わった日程が参加できる候補のように見えてしまうので、ブラウザ側で直す。
 * 決まりは hooks/schedule.py と同じ：**開始から3時間で「開催済み」**。
 *
 * 付け直すもの（印はすべて hooks/schedule.py とテンプレートが付ける）
 * - [data-at]           … 1つの日程。済んだら .is-held、[data-when-held] を出し、[data-when-planned] を隠す
 * - [data-round-end]    … 1つの回（最後の日程の開始）。済んだら .is-held
 * - [data-sch-up]       … これからの開催。済んだ回を隠し、先頭から data-max 回だけ出す（繰り上げ）
 * - [data-window-end]   … 申込の時期ごとの表の行。受付が終わったら隠し、次の行を繰り上げる。
 *                         残りの日程が無ければ [data-pay-none] を出す
 * - [data-next-session] … 直近の日程の表記（"md" なら 11/6(金)、無指定なら 11/6(金) 20:00〜）
 * - [data-next-label]   … 直近の日程の回（第6回 B日程）
 * - [data-next-wrap]    … 直近の日程が無くなったら隠す
 * 日程の一覧はページに埋めた JSON（#aisia-schedule。overrides/main.html）から読む。
 */
(function () {
  "use strict";

  var HELD_MS = 3 * 60 * 60 * 1000;

  function time(s) {
    var v = Date.parse(s || "");
    return isNaN(v) ? null : v;
  }
  function isHeld(at, now) { return at !== null && now >= at + HELD_MS; }
  function each(sel, fn, root) {
    Array.prototype.forEach.call((root || document).querySelectorAll(sel), fn);
  }
  function days() {
    var el = document.getElementById("aisia-schedule");
    try { return (el && JSON.parse(el.textContent)) || []; } catch (e) { return []; }
  }

  function apply() {
    var now = Date.now();

    each("[data-at]", function (el) {
      var held = isHeld(time(el.getAttribute("data-at")), now);
      el.classList.toggle("is-held", held);
      each("[data-when-held]", function (x) { x.hidden = !held; }, el);
      each("[data-when-planned]", function (x) { x.hidden = held; }, el);
    });

    each("[data-round-end]", function (el) {
      el.classList.toggle("is-held", isHeld(time(el.getAttribute("data-round-end")), now));
    });

    each("[data-sch-up]", function (box) {
      var max = parseInt(box.getAttribute("data-max"), 10) || 2;
      var shown = 0;
      each("[data-round-end]", function (r) {
        var show = !r.classList.contains("is-held") && shown < max;
        r.hidden = !show;
        if (show) shown++;
      }, box);
      each("[data-sch-empty]", function (x) { x.hidden = shown > 0; }, box);
    });

    // 申込の時期ごとの表：受付が終わった行を隠し、先頭から3行だけ出す（4行目は繰り上げ用）
    var rows = 0;
    each("[data-window-end]", function (row) {
      var end = time(row.getAttribute("data-window-end"));
      var show = !(end !== null && now >= end) && rows < 3;
      row.hidden = !show;
      if (show) rows++;
      var left = row.querySelectorAll("[data-at]:not(.is-held)").length;
      each("[data-pay-none]", function (x) { x.hidden = left > 0; }, row);
    });
    each("[data-pay-empty]", function (x) { x.hidden = rows > 0; });

    var next = null;
    days().some(function (d) {
      if (!isHeld(time(d.at), now)) { next = d; return true; }
      return false;
    });
    each("[data-next-session]", function (el) {
      if (next) el.textContent = el.getAttribute("data-next-session") === "md" ? next.md : next.full;
    });
    each("[data-next-label]", function (el) { if (next) el.textContent = next.label; });
    each("[data-next-wrap]", function (el) { el.hidden = !next; });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(apply);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", apply);
  } else {
    apply();
  }
})();
