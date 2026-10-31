"""mkdocs-macros module.

変動情報（回の予定・参加費・登録URL）の単一ソースは mkdocs.yml の `extra:` に置き、
ここではそれを各ページへ流し込むためのマクロだけを定義する。
本文に日付・価格をハードコードしないこと（§3 単一ソース原則）。

日程の部品（これからの開催・全回の一覧・申込の時期ごとの表・参加の前に）は hooks/schedule.py に
あり、テーマのテンプレートと同じものをここから呼ぶ（表示を1か所で作るため）。
"""

import importlib.util
import pathlib
import sys


def _schedule():
    """hooks/schedule.py（MkDocs が hook として読み込んだもの）。無ければパスから読む。"""
    mod = sys.modules.get("hooks/schedule.py")
    if mod is None:
        path = pathlib.Path(__file__).with_name("hooks") / "schedule.py"
        spec = importlib.util.spec_from_file_location("aisia_schedule", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


def define_env(env):
    extra = env.conf.get("extra", {}) or {}
    sched = _schedule()

    @env.macro
    def upcoming_rounds(n=2):
        """これからの開催（回・テーマ・問い・A/B の日時・同じ内容・開催済み）。"""
        return sched.upcoming_html(extra, n)

    @env.macro
    def schedule_list():
        """全回の一覧（/sessions/ の開催予定）。"""
        return sched.schedule_list_html(extra)

    @env.macro
    def payment_table():
        """お申し込みの時期ごとの初回のお支払い日と、無料で参加できる回（join）。
        申込用 GAS の COHORT_SCHEDULE と同じ決まり（hooks/schedule.py の payment_windows）。"""
        return sched.payment_table_html(extra)

    @env.macro
    def participation_notes(title="有償メンバーとして参加する前に"):
        """参加の前に（`extra.participation`）。/subscribe/ のカードと同じ内容。"""
        return sched.participation_html(extra, title)

    def _link(url, classes):
        """Markdown のリンク。外部URLだけ新しいタブで開く（サイト内は相対パスに直す）。"""
        if url.startswith("http"):
            return f"({url}){{ {classes} target=_blank rel=noopener }}"
        return f"({_rel(url)}){{ {classes} }}"

    @env.macro
    def register_button(label="案内メールを受け取る（無料のメール登録）"):
        """メール登録ボタン。行き先は単一ソース（`extra.register_url`＝サイト内の /subscribe/）。

        色は金（gold）で固定。サイト全体で「金＝メール登録／ティール＝申込」を守り、
        2つの入口がひと目で区別できるようにする（ホームの btn-gold と同じ役割）。
        """
        url = extra.get("register_url", "#")
        return f"[{label}]" + _link(url, ".md-button .md-button--gold")

    @env.macro
    def join_button(label="有償メンバーに申し込む（初月無料）"):
        """申込（Stripe）への直リンクボタン。URL は単一ソースから。色はティール。"""
        url = extra.get("join_url", "#")
        return (
            f"[{label}]({url})"
            "{ .md-button .md-button--primary target=_blank rel=noopener }"
        )

    def _rel(target):
        """サイトルート基準のパスを、描画中のページから見た相対パスへ変換する。

        use_directory_urls 前提。page.url は "" / "join/" / "about/profile/" の形。
        """
        page = getattr(env, "page", None)
        depth = page.url.count("/") if page is not None and page.url else 0
        return "../" * depth + target

    @env.macro
    def history_cards():
        """開催履歴（sessions/history.md）。`extra.history` を新しい順にカードで描画する。

        各回：回番号・開催日・テーマ・扱った領域・2〜3行の要約・図1点・ダイジェストへのリンク。
        「実績のある取り組みだと一目で分かる」ためのページなので、内容の詳細は載せない
        （詳細はダイジェスト側）。画像・リンクはページ深さから相対パスを自動計算する。
        """
        import html as _html

        rounds = extra.get("history", []) or []
        out = ['<div class="history">']
        for r in rounds:
            no = r.get("round", "")
            title = _html.escape(str(r.get("title", "")))
            area = _html.escape(str(r.get("area", "")))
            # 日付は hooks/schedule.py が extra.schedule から作る（「開催予定」はブラウザ側でも外れる）
            dates = r.get("dates_html") or _html.escape(str(r.get("dates", "")))
            summary = _html.escape(str(r.get("summary", "")))
            image = r.get("image")
            out.append('<article class="history-card">')
            if image:
                # SVG の図（文字を読ませる図）は、携帯では原寸の横スクロールにする（extra.css）。
                # 縮めると文字が5px前後になり読めないため。その旨の小さな案内を添える
                svg = str(image).endswith(".svg")
                out.append(
                    f'<div class="history-card__fig{" history-card__fig--svg" if svg else ""}">'
                    f'<img src="{_rel(image)}" alt="第{no}回の図" loading="lazy"></div>'
                )
                if svg:
                    out.append('<p class="history-card__hint">図は横にスクロールできます →</p>')
            out.append('<div class="history-card__body">')
            out.append(
                f'<div class="history-card__meta"><span class="history-card__no">第{no}回</span>'
                f'<span class="history-card__dates">{dates}</span></div>'
            )
            out.append(f'<h3 class="history-card__title">{title}</h3>')
            if area:
                out.append(f'<div class="history-card__area">{area}</div>')
            if summary:
                out.append(f'<p class="history-card__summary">{summary}</p>')
            out.append("</div></article>")
        out.append("</div>")
        return "\n".join(out)

    def _figure_head(title, sub):
        """join の図の見出し。<p> にして目次（toc）に載せない。"""
        return (f'<p class="jf__title">{title}</p>'
                f'<p class="jf__sub">{sub}</p>')

    @env.macro
    def payment_flow():
        """join の図1「お申し込みから初回のお支払いまでの流れ」と、解約の2つの場合。

        **例の日付を持たない**（2026年11月〜）。以前は `extra.sessions` の先頭の回の月を例に
        取っていたため、その月の途中から申し込む人や、前の月に申し込む人に当てはまらない
        日付が出ていた。具体的な日付は、すぐ下の `payment_table()`（申込の時期ごとの表。申込用
        GAS の COHORT_SCHEDULE と同じ決まり）が出す。

        PC では横4段・スマホでは縦の時系列（extra.css の `.jf`）。金額は `extra.pricing`、
        解約の文は `extra.billing`（ホーム・/subscribe/・FAQ・llms.txt と同じ文）。
        """
        import html as _html

        pricing = extra.get("pricing", {}) or {}
        billing = extra.get("billing", {}) or {}
        early = str(pricing.get("early_monthly", "")).replace("円", "")
        incl = pricing.get("early_monthly_incl", "")
        steps = [
            ("", "STEP 1", "お申し込み", "Stripeでカード情報を登録。お申し込み時のお支払いはありません", "お申し込み日"),
            ("jf-step--free", "STEP 2", "無料期間",
             '<span class="jf-step__free">¥0 <small>無料</small></span>'
             "次に開催される回（A日程・B日程）に参加できます", "次の回まで"),
            ("", "STEP 3", "初回のお支払い", f"¥{incl}（早期割引 {early}）", "その回のあとの15日"),
            ("", "STEP 4", "以降のお支払い", "毎月15日に自動で更新", "毎月15日"),
        ]
        out = ['<figure class="jf jf--flow">',
               _figure_head("お申し込みから初回のお支払いまでの流れ",
                            "初回のお支払い日は、お申し込みの時期で決まります（日付は下の表）。"),
               '<ol class="jf-steps">']
        for cls, no, name, desc, at in steps:
            out.append(
                f'<li class="jf-step {cls}"><span class="jf-step__at">{at}</span>'
                f'<span class="jf-step__card"><span class="jf-step__no">{no}</span>'
                f'<span class="jf-step__name">{name}</span>'
                f'<span class="jf-step__desc">{desc}</span></span></li>')
        out.append("</ol>")
        e = lambda k: _html.escape(str(billing.get(k, "")))
        portal = str(billing.get("portal_url") or "")
        portal_link = (f' <a href="{_html.escape(portal)}" target="_blank" rel="noopener">'
                       "カスタマーポータルを開く</a>") if portal.startswith("https://") else ""
        out.append(
            '<div class="jf-note"><p class="jf-note__lead">解約はいつでも、ご自身で。締め切りは2通りです。</p>'
            f'<p class="jf-note__case">{e("cancel_trial")}</p>'
            f'<p class="jf-note__case">{e("cancel_paid")}</p>'
            f'<p class="jf-note__ex">{e("cancel_note")}カード情報は弊社で保持しません。{portal_link}</p></div>')
        out.append("<figcaption>図1：お申し込みから初回のお支払いまでの流れ</figcaption>")
        out.append("</figure>")
        return "\n".join(out)

    @env.macro
    def pricing_ladder():
        """join の図2「早く申し込むほど、ずっとお得」。月額の段を上から並べる。

        段の金額は `extra.pricing.ladder`（税抜・高い順）。「いまここ」は
        `early_monthly` と同じ金額の段、それより下＝お申し込み済み（据え置き）、
        上＝今後の新規（例）、先頭＝定価。**料金改定は `extra.pricing` だけ直せばよい。**

        **金額を出すのは定価と「いまここ」の段だけ。** 据え置きの段（過去の早期価格）を
        出すと後から来た人が「損した」と感じ、今後の段の金額はまだ仮なので約束に見える。
        段の棒（長さ）だけで「上がっていく」ことを見せる。
        """
        import re

        pricing = extra.get("pricing", {}) or {}
        ladder = [str(v) for v in (pricing.get("ladder") or [])]
        if not ladder:
            return ""

        def num(v):
            m_ = re.search(r"[\d,]+", str(v))
            return int(m_.group().replace(",", "")) if m_ else 0

        now = num(pricing.get("early_monthly", ""))
        top = max(num(v) for v in ladder) or 1
        out = ['<figure class="jf jf--ladder">',
               _figure_head("早く申し込むほど、ずっとお得",
                            "お申し込み時の月額は当面そのまま。後から参加する方ほど、"
                            "割引は小さくなります。"),
               '<ul class="jf-ladder" aria-label="月額（税抜）">']
        for i, v in enumerate(ladder):
            n = num(v)
            if i == 0:
                cls, tag = "list", "定価"
            elif n == now:
                cls, tag = "now", "いまここ（現在の早期参加枠）"
            elif n < now:
                cls, tag = "past", "お申し込み済みの方は据え置き"
            else:
                cls, tag = "future", "今後の新規（例）"
            out.append(
                f'<li class="jf-rung jf-rung--{cls}"><span class="jf-rung__price">'
                f'{"¥" + v if cls in ("list", "now") else ""}</span>'
                f'<span class="jf-rung__bar"><i style="width:{round(n / top * 100)}%"></i></span>'
                f'<span class="jf-rung__tag">{tag}</span></li>')
        out.append("</ul>")
        out.append('<p class="jf-ladder__axis">月額（税抜）。上の段ほど、後から申し込む方の想定です'
                   '（時期・幅は運営側で調整）。</p>')
        out.append("<figcaption>図2：早期参加枠は「申込時の月額が据え置き」になります。"
                   "後から申し込む方ほど、月額は段階的に上がっていく想定です。</figcaption>")
        out.append("</figure>")
        return "\n".join(out)

    @env.macro
    def footer_cta(*related, join_cta=True):
        """全ページ末尾の共通動線ブロック（関連ページ＋次回開催＋CTA）。

        related には整形済みの Markdown リンク文字列を渡す。
        例: {{ footer_cta("[背景と狙い](../about/index.md)", "[設計思想](philosophy.md)") }}

        CTA はサイトの2本立てを常にボタン2つで見せる。ティール＝参加費とお申し込み
        （join）、金＝無料のメール登録。join ページ自身は申込ボタンが本文中に
        あるため、join_cta=False でメール登録のみを表示する。
        """
        url = extra.get("register_url", "#")
        nxt = extra.get("next_session_short", "")
        lines = ["", "---", ""]
        if related:
            lines.append("**関連ページ:** " + " ・ ".join(related))
            lines.append("")
        if nxt:
            # 日付は schedule.js が、開催日を過ぎたら次の日程に付け直す（data-next-session）
            nxt = f'<span data-next-session>{nxt}</span>'
            lines.append(f"次回開催は **{nxt}**。参加を決めた方も、まず情報だけ受け取りたい方も、"
                         "下のいずれかからどうぞ。" if join_cta else f"次回開催は **{nxt}**。")
            lines.append("")
        lines.append('<div class="cta-pair" markdown>')
        lines.append("")
        if join_cta:
            lines.append(
                f"[参加費とお申し込みを見る →]({_rel('join/')})"
                "{ .md-button .md-button--primary }"
            )
        lines.append("[案内メールを受け取る（無料のメール登録）]" + _link(url, ".md-button .md-button--gold"))
        lines.append("")
        lines.append("</div>")
        lines.append("")
        return "\n".join(lines)
