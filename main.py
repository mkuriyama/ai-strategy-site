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
    def register_button(label="参加・案内登録へ"):
        """登録（Mailchimp）ボタン。URL は単一ソースから。"""
        url = extra.get("register_url", "#")
        return (
            f"[{label}]({url})"
            "{ .md-button .md-button--primary target=_blank rel=noopener }"
        )

    @env.macro
    def footer_cta(*related):
        """全ページ末尾の共通動線ブロック（関連ページ＋次回開催＋登録CTA）。

        related には整形済みの Markdown リンク文字列を渡す。
        例: {{ footer_cta("[背景と狙い](../about/index.md)", "[参加する](../join/index.md)") }}
        """
        url = extra.get("register_url", "#")
        nxt = extra.get("next_session_short", "")
        lines = ["", "---", ""]
        if related:
            lines.append("**関連ページ:** " + " ・ ".join(related))
            lines.append("")
        if nxt:
            lines.append(f"次回開催は **{nxt}**。継続的な開催案内はメール登録から受け取れます。")
            lines.append("")
        lines.append(
            f"[参加・案内登録へ]({url})"
            "{ .md-button .md-button--primary target=_blank rel=noopener }"
        )
        lines.append("")
        return "\n".join(lines)
