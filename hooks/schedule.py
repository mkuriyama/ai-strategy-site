"""回の予定（`extra.schedule`）を正本にして、日程まわりの値と表示をビルド時に作る hook。

## 正本（mkdocs.yml の `extra.schedule`）

1回＝1要素。開始日時は日本時間の ISO 形式で書く。**曜日は書かない**（日付から計算する）。

    - round: 7
      theme: "AI駆動開発と企業戦略"     # 任意。決まっていなければ省く（「決まりしだい」と出る）
      question: "システムを作る…"       # 任意。テーマの問い（1文）
      a: "2026-11-17T20:00:00+09:00"   # A日程の開始
      b: "2026-11-30T20:00:00+09:00"   # B日程の開始（同じ内容）

テーマを省いた回は、`extra.history` の同じ回の `title`（「 ── 」より前）を使う。

## ここで作るもの（**手で書かない**）

- `extra.sessions` … これから開催される日程（近い順）。構造化データ（Event）・llms.txt が読む
- `extra.next_session_short` / `next_session_label` … 直近の日程（お知らせバー・ページ末尾の導線）
- `extra.history[].dates`（と `dates_html`）… 開催履歴の日付。まだの日程には「開催予定」
- `extra.schedule_client` … ブラウザ用の日程の一覧（`overrides/main.html` がページに埋め、
  `docs/javascripts/schedule.js` が読む）

## 表示の部品（テンプレートからも、Markdown のマクロからも同じものを呼ぶ）

- `upcoming_html(extra, n)` … 「これからの開催」。回・テーマ・問い・A/B の日時・同じ内容・開催済み
- `schedule_list_html(extra)` … 全回の一覧（/sessions/ の「開催予定」）
- `payment_table_html(extra)` … お申し込みの時期ごとの、初回のお支払い日と、無料で参加できる回
  （申込用 GAS の COHORT_SCHEDULE と同じ決まり。`payment_windows()` の説明を参照）
- `participation_html(extra, title)` … 参加の前に（`extra.participation`）

テンプレートでは `on_env` が登録する同名の関数（`schedule_upcoming(2)` など）、Markdown では
`main.py` のマクロ（`{{ upcoming_rounds() }}` など）から呼ぶ。

## 「開催済み」の決まり

**開始から3時間**で開催済み。ビルドの時点で判定して出し、ブラウザでは schedule.js が同じ
決まりで付け直す ―― ビルドとビルドの間に開催日が過ぎても、終わった日程が「次回」や参加できる
候補として残らないようにするため。試すときは `SCHEDULE_NOW=2026-11-07T00:00:00+09:00` で
ビルドの「いま」を差し替えられる。
"""

from __future__ import annotations

import datetime as dt
import html
import os

from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority

JST = dt.timezone(dt.timedelta(hours=9))
WEEKDAY = "月火水木金土日"
HELD_AFTER = dt.timedelta(hours=3)
DAY_NAME = {"a": "A日程", "b": "B日程"}
SAME = "A日程とB日程は同じ内容です。都合のよい日程にご参加ください。"
NO_THEME = "テーマは決まりしだいお知らせします"


# ---------------------------------------------------------------------------
# 読み込みと検査
# ---------------------------------------------------------------------------
def now() -> dt.datetime:
    v = os.environ.get("SCHEDULE_NOW", "").strip()
    return _parse(v, "SCHEDULE_NOW") if v else dt.datetime.now(JST)


def _parse(value, where: str) -> dt.datetime:
    try:
        d = dt.datetime.fromisoformat(str(value))
    except ValueError:
        raise PluginError(f"{where}: 日時として読めません: {value!r}（例 2026-11-17T20:00:00+09:00）")
    if d.tzinfo is None:
        raise PluginError(f"{where}: 時差（+09:00）を付けてください: {value!r}")
    return d.astimezone(JST)


def _short_title(title: str) -> str:
    return str(title or "").split(" ── ")[0].strip()


def rounds(extra) -> list[dict]:
    """`extra.schedule` を回の順に読み、各回に日程（days）を付けて返す。"""
    raw = extra.get("schedule") or []
    history = {h.get("round"): h for h in (extra.get("history") or []) if isinstance(h, dict)}
    out, seen = [], set()
    for i, r in enumerate(raw):
        where = f"extra.schedule[{i}]"
        if not isinstance(r, dict) or not isinstance(r.get("round"), int):
            raise PluginError(f"{where}: round（回の番号・整数）がありません")
        no = r["round"]
        if no in seen:
            raise PluginError(f"{where}: 第{no}回が2回出てきます")
        seen.add(no)
        if not r.get("a"):
            raise PluginError(f"{where}: 第{no}回の a（A日程の開始）がありません")
        days = []
        for key in ("a", "b"):
            if r.get(key):
                at = _parse(r[key], f"{where}.{key}")
                days.append({"round": no, "day": key, "at": at,
                             "label": f"第{no}回 {DAY_NAME[key]}"})
        if len(days) == 2 and days[1]["at"] <= days[0]["at"]:
            raise PluginError(f"{where}: 第{no}回の B日程が A日程より前になっています")
        theme = str(r.get("theme") or "").strip() or _short_title(history.get(no, {}).get("title", ""))
        out.append({"round": no, "theme": theme, "question": str(r.get("question") or "").strip(),
                    "days": days, "end": days[-1]["at"]})
    if [r["round"] for r in out] != sorted(r["round"] for r in out):
        raise PluginError("extra.schedule: 回は番号の小さい順に並べてください")
    return out


def held(at: dt.datetime, when: dt.datetime) -> bool:
    return when >= at + HELD_AFTER


# ---------------------------------------------------------------------------
# 日付の書き方
# ---------------------------------------------------------------------------
def md(d: dt.datetime, ref: dt.datetime | None = None) -> str:
    """11/6(金)。年が「いま」と違うときは 2027/1/6(水)。"""
    y = f"{d.year}/" if ref is not None and d.year != ref.year else ""
    return f"{y}{d.month}/{d.day}({WEEKDAY[d.weekday()]})"


def full(d: dt.datetime, ref: dt.datetime | None = None) -> str:
    return f"{md(d, ref)} {d:%H:%M}〜"


def _iso(d: dt.datetime) -> str:
    return d.isoformat(timespec="seconds")


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


# ---------------------------------------------------------------------------
# config に入れる値（on_config）
# ---------------------------------------------------------------------------
@event_priority(100)   # macros・ほかの hook より先に（`extra.sessions` を読む側がある）
def on_config(config):
    extra = config["extra"]
    if not extra.get("schedule"):
        return config
    when = now()
    rs = rounds(extra)
    by_round = {r["round"]: r for r in rs}
    days = [d for r in rs for d in r["days"]]
    upcoming = [d for d in days if not held(d["at"], when)]

    sessions = []
    for d in upcoming:
        r = by_round[d["round"]]
        note = f"第{r['round']}回" + (f"「{r['theme']}」" if r["theme"] else "") + "。"
        if len(r["days"]) == 2:
            note += "A日程・B日程は同じ内容（どちらか一方に参加）。"
        note += "オンライン（Zoom）。各回は独立したテーマで、途中の回から参加できます。"
        sessions.append({"label": d["label"], "kind": "main" if d["day"] == "a" else "sub",
                         "date": full(d["at"], when), "start": _iso(d["at"]),
                         "theme": r["theme"], "note": note})
    extra["sessions"] = sessions
    extra["next_session_short"] = sessions[0]["date"] if sessions else ""
    extra["next_session_label"] = sessions[0]["label"] if sessions else ""

    # 開催履歴の日付（「開催予定」はブラウザ側でも外れるように、日程ごとに data-at を付ける）
    for h in extra.get("history") or []:
        r = by_round.get(h.get("round")) if isinstance(h, dict) else None
        if not r:
            continue
        texts, spans = [], []
        for d in r["days"]:
            base = md(d["at"])
            if held(d["at"], when):
                texts.append(base)
                spans.append(f'<span data-at="{_iso(d["at"])}">{_e(base)}</span>')
            else:
                texts.append(base[:-1] + "・開催予定)")
                spans.append(f'<span data-at="{_iso(d["at"])}">{_e(base[:-1])}'
                             f'<span data-when-planned>・開催予定</span>)</span>')
        h["dates"] = "・".join(texts)
        h["dates_html"] = "・".join(spans)

    extra["schedule_client"] = [
        {"at": _iso(d["at"]), "label": d["label"], "md": md(d["at"]), "full": full(d["at"])}
        for d in days
    ]
    return config


def on_env(env, config, files):
    """テーマのテンプレート（overrides/*.html）から部品を呼べるようにする。"""
    extra = config["extra"]
    env.globals.update(
        schedule_upcoming=lambda n=2, variant="": upcoming_html(extra, n, variant),
        schedule_list=lambda: schedule_list_html(extra),
        payment_table=lambda: payment_table_html(extra),
        participation=lambda title="有償メンバーとして参加する前に": participation_html(extra, title),
    )
    return env


# ---------------------------------------------------------------------------
# 表示の部品
# ---------------------------------------------------------------------------
def _day_li(d: dt.datetime, name: str, when: dt.datetime, with_time: bool = True) -> str:
    h = held(d, when)
    when_txt = full(d, when) if with_time and not h else md(d, when)
    return (f'<li class="sch-day{" is-held" if h else ""}" data-at="{_iso(d)}">'
            f'<span class="sch-day__k">{_e(name)}</span>'
            f'<span class="sch-day__d">{_e(when_txt)}</span>'
            f'<span class="sch-day__held" data-when-held{"" if h else " hidden"}>開催済み</span></li>')


def _theme(r: dict) -> str:
    if r["theme"]:
        return f'<span class="sch-round__theme">{_e(r["theme"])}</span>'
    return f'<span class="sch-round__theme sch-round__theme--tbd">{NO_THEME}</span>'


def upcoming_html(extra, n: int = 2, variant: str = "") -> str:
    """これからの開催（全日程が済んでいない回を近い順に n 回）。

    n 回より後ろの回も `hidden` で入れておく ―― ブラウザで先頭の回が済んだとき、
    schedule.js が繰り上げて出す。
    """
    when = now()
    rs = [r for r in rounds(extra) if not held(r["end"], when)][: n + 2]
    cls = "sch-up" + (f" sch-up--{variant}" if variant else "")
    out = [f'<div class="{cls}" data-sch-up data-max="{n}">']
    for i, r in enumerate(rs):
        out.append(f'<div class="sch-round" data-round-end="{_iso(r["end"])}"{" hidden" if i >= n else ""}>')
        out.append(f'<p class="sch-round__head"><span class="sch-round__no">第{r["round"]}回</span>{_theme(r)}</p>')
        if r["question"]:
            out.append(f'<p class="sch-round__q">{_e(r["question"])}</p>')
        out.append('<ul class="sch-days">' + "".join(
            _day_li(d["at"], DAY_NAME[d["day"]], when) for d in r["days"]) + "</ul>")
        if len(r["days"]) == 2:
            out.append(f'<p class="sch-round__same">{SAME}</p>')
        out.append("</div>")
    out.append(f'<p class="sch-up__empty" data-sch-empty{" hidden" if rs else ""}>'
               "次の開催日は、決まりしだいお知らせします。</p>")
    out.append("</div>")
    return "\n".join(out)


def schedule_list_html(extra) -> str:
    """全回の一覧（回・テーマ・A日程・B日程・開催済み）。"""
    when = now()
    out = ['<div class="sch-all">']
    for r in rounds(extra):
        h = held(r["end"], when)
        out.append(f'<div class="sch-all__row{" is-held" if h else ""}" data-round-end="{_iso(r["end"])}">')
        out.append(f'<p class="sch-round__head"><span class="sch-round__no">第{r["round"]}回</span>{_theme(r)}</p>')
        out.append('<ul class="sch-days">' + "".join(
            _day_li(d["at"], DAY_NAME[d["day"]], when) for d in r["days"]) + "</ul>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)


def _month_start(y: int, m: int) -> dt.datetime:
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return dt.datetime(y, m, 1, tzinfo=JST)


def _day_start(d: dt.datetime) -> dt.datetime:
    return dt.datetime(d.year, d.month, d.day, tzinfo=JST)


def payment_windows(extra) -> list[dict]:
    """お申し込みの時期ごとの、初回のお支払い日と、無料で参加できる回。

    **申込用 GAS（Stripe Checkout を作る `doGet`）の COHORT_SCHEDULE と同じ決まり。**

    - 申込の受付は回ごとに切り替わる：前の回の B日程の**翌日 0時（日本時間）**から、
      その回の B日程の日の終わりまで（GAS の `advertiseFrom`）
    - その期間のお申し込みは、**その回（A日程・B日程）に無料で参加**できる
    - 初回のお支払い（Stripe の `trial_end`）は、その回の **A日程の翌月15日 0時（日本時間）**
      （例：第7回 11/17・11/30 → 11/7〜11/30 のお申し込み → 12/15）

    「申込月の翌月15日」ではない。たとえば 11/1〜11/6 のお申し込みは第6回B（11/6）が無料で、
    初回のお支払いは 11/15。GAS の COHORT_SCHEDULE を変えたら、ここも合わせる。
    """
    rs = rounds(extra)
    out = []
    for i, r in enumerate(rs):
        a = r["days"][0]["at"]
        last = r["days"][-1]["at"]
        start = _day_start(rs[i - 1]["days"][-1]["at"]) + dt.timedelta(days=1) if i else None
        end = _day_start(last) + dt.timedelta(days=1)          # この時刻から次の回の受付
        pay = _month_start(a.year, a.month + 1).replace(day=15)
        out.append({"round": r, "start": start, "end": end, "pay": pay})
    return out


def payment_table_html(extra, rows: int = 3) -> str:
    """お申し込みの時期ごとの表（いまの受付から rows 行）。終わった行は schedule.js が隠す
    （行に `data-window-end`）。済んだ日程は CSS で隠す（`.pay-month .sch-day.is-held`）。"""
    when = now()
    ws = [w for w in payment_windows(extra) if when < w["end"]][: rows + 1]
    if not ws:
        return ""
    out = ['<div class="pay-months">',
           '<div class="pay-months__head" aria-hidden="true"><span>お申し込み</span>'
           '<span>初回のお支払い</span><span>無料で参加できる回</span></div>']
    for i, w in enumerate(ws):
        r = w["round"]
        last_day = w["end"] - dt.timedelta(days=1)
        span = (f"{md(w['start'], when)}〜{md(last_day, when)}" if w["start"]
                else f"{md(last_day, when)}まで")
        free = [d for d in r["days"] if not held(d["at"], when)]
        items = "".join(_day_li(d["at"], d["label"], when, with_time=False) for d in r["days"])
        out.append(f'<div class="pay-month" data-window-end="{_iso(w["end"])}"{" hidden" if i >= rows else ""}>')
        out.append(f'<p class="pay-month__when"><b>{_e(span)}</b>'
                   '<span class="pay-month__sfx">のお申し込み</span></p>')
        out.append(f'<p class="pay-month__pay"><span class="pay-month__k">初回のお支払い</span>'
                   f'<b>{_e(md(w["pay"], when))}</b>'
                   f'<span class="pay-month__dl">無料のまま解約するなら '
                   f'{_e(md(w["pay"] - dt.timedelta(days=1), when))} まで</span></p>')
        out.append(f'<div><ul class="sch-days pay-month__free">{items}</ul>'
                   f'<p class="pay-month__none" data-pay-none{" hidden" if free else ""}>'
                   "この期間に参加できる回は終わりました（明日のお申し込みからは、次の回に無料で参加できます）"
                   "</p></div>")
        out.append("</div>")
    out.append('<p class="pay-months__none" data-pay-empty hidden>次の回の日程は、決まりしだいお知らせします。</p>')
    out.append('<p class="pay-months__note">お申し込みの時期は、前の回の B日程の翌日で切り替わります。'
               "日付は日本時間で数えます。</p>")
    out.append("</div>")
    return "\n".join(out)


def participation_html(extra, title: str = "有償メンバーとして参加する前に") -> str:
    items = extra.get("participation") or []
    if not items:
        return ""
    out = ['<div class="prep">']
    if title:
        out.append(f'<p class="prep__title">{_e(title)}</p>')
    out.append('<ul class="prep__list">')
    for it in items:
        out.append(f'<li><strong>{_e(it.get("title"))}</strong>{_e(it.get("text"))}</li>')
    out.append("</ul></div>")
    return "\n".join(out)
