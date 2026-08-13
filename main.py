"""mkdocs-macros module.

変動情報（次回開催・参加費・登録URL）の単一ソースは mkdocs.yml の `extra:` に置き、
ここではそれを各ページへ流し込むためのマクロだけを定義する。
本文に日付・価格をハードコードしないこと（§3 単一ソース原則）。
"""


def define_env(env):
    extra = env.conf.get("extra", {}) or {}

    @env.macro
    def session_cards():
        """次回開催を grid cards で描画（schedule / 必要箇所が参照）。"""
        sessions = extra.get("sessions", [])
        out = ['<div class="grid cards" markdown>', ""]
        for s in sessions:
            out.append(f'-   **{s["label"]}**')
            out.append("")
            out.append("    ---")
            out.append("")
            out.append(f'    **{s["date"]}** ／ {s["note"]}')
            out.append("")
        out.append("</div>")
        return "\n".join(out)

    @env.macro
    def register_button(label="案内メールを受け取る（無料登録）", primary=True):
        """案内メール配信（Mailchimp）への登録ボタン。URL は単一ソースから。

        primary=False は、申込ボタンが「主」になるページ（register）で
        メール登録を視覚的に控えめにするためのアウトライン表示。
        """
        url = extra.get("register_url", "#")
        style = " .md-button--primary" if primary else ""
        return f"[{label}]({url})" + "{ .md-button" + style + " target=_blank rel=noopener }"

    @env.macro
    def join_button(label="今すぐ申し込む（申込月無料）"):
        """申込（Stripe）への直リンクボタン。URL は単一ソースから。"""
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
    def footer_cta(*related, join_cta=True):
        """全ページ末尾の共通動線ブロック（関連ページ＋次回開催＋CTA）。

        related には整形済みの Markdown リンク文字列を渡す。
        例: {{ footer_cta("[背景と狙い](../about/index.md)", "[設計思想](philosophy.md)") }}

        CTA はサイトの2本立てに揃える。主＝参加費とお申し込み（join）、
        従＝案内メールの無料登録。join ページ自身では自己リンクになるため、
        join_cta=False でメール登録のみを表示する。
        """
        url = extra.get("register_url", "#")
        nxt = extra.get("next_session_short", "")
        lines = ["", "---", ""]
        if related:
            lines.append("**関連ページ:** " + " ・ ".join(related))
            lines.append("")
        if nxt:
            lines.append(f"次回開催は **{nxt}**。")
            lines.append("")
        if join_cta:
            lines.append(
                f"[参加費とお申し込みを見る →]({_rel('join/')})"
                "{ .md-button .md-button--primary }"
            )
            lines.append("")
            lines.append(
                f"まだ検討中の方は、[案内メールだけ受け取る（無料登録）]({url})"
                "{ target=_blank rel=noopener } こともできます。"
            )
        else:
            lines.append(
                f"[案内メールを受け取る（無料登録）]({url})"
                "{ .md-button .md-button--primary target=_blank rel=noopener }"
            )
        lines.append("")
        return "\n".join(lines)
