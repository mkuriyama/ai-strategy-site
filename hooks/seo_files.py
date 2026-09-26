"""AIO 用の `llms.txt` をビルド時に生成する MkDocs hook。

`llms.txt` は AI アシスタントがサイトの要点を把握するための索引（https://llmstxt.org/）。
手書きにすると次回開催・参加費が本文と二重管理になるので、`mkdocs.yml` の `extra:`
（単一ソース）と各ページの `description` から毎回生成する。

- 変動情報（次回開催・参加費・メール登録の行き先）は `extra` から
- ページ一覧は、ビルドで描画された全ページの title / description / 絶対URL から
- `robots.txt` は静的（docs/robots.txt）。ここでは触らない
"""

from __future__ import annotations

import os

_pages: list[tuple[str, str, str]] = []


def on_pre_build(config):
    _pages.clear()


def on_page_context(context, page, config, nav):
    """描画された各ページの title / description / URL を集める。"""
    if not page.abs_url and not page.url:
        return context
    # ダイジェストと用語集は索引に載せない（公開はしているが、案内はしない）。
    # 用語集の掲載場所はライブラリー（B）の /terms/ ―― `extra.news_site_url` の
    # 関連サイトから辿れる。
    src = page.file.src_uri or ""
    # メール登録の完了ページも載せない（送信した人だけが見る。noindex）
    if src.startswith("digests/") or src == "glossary.md" or src.startswith("subscribe/thanks/"):
        return context
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    url = site_url + page.url
    title = "ホーム" if page.is_homepage else (page.meta.get("title") or page.title or "")
    desc = (page.meta.get("description") or "").strip()
    _pages.append((title, url, desc))
    return context


def on_post_build(config):
    extra = config.get("extra", {}) or {}
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    lines: list[str] = []
    lines.append(f"# {config.get('site_name', '')}")
    lines.append("")
    lines.append(f"> {config.get('site_description', '')}")
    lines.append("")
    lines.append("主催: 栗山実／株式会社アンテカニス（https://www.antecanis.com/）")
    lines.append("形式: オンライン（Zoom）・月次開催。各回は独立したテーマで、途中参加可。")

    sessions = extra.get("sessions") or []
    if sessions:
        lines.append("")
        lines.append("## 次回開催")
        lines.append("")
        for s in sessions:
            lines.append(f"- {s.get('label', '')}: {s.get('date', '')} ── {s.get('note', '')}")

    pricing = extra.get("pricing") or {}
    if pricing:
        lines.append("")
        lines.append("## 参加費")
        lines.append("")
        lines.append(
            f"- {pricing.get('early_label', '早期参加枠')}: 月額 {pricing.get('early_monthly', '')}"
            f"（税込 {pricing.get('early_monthly_incl', '')}円）"
        )
        lines.append(f"- 定価: 月額 {pricing.get('list_monthly', '')}（税込 {pricing.get('list_monthly_incl', '')}円）")
        lines.append("- 有償メンバーは初月無料。更新日（毎月15日）の前日までに解約すればその月は0円。")

    lines.append("")
    lines.append("## 入口")
    lines.append("")
    if extra.get("register_url"):
        # register_url はサイト相対（subscribe/）。llms.txt では絶対URLにする
        reg = extra["register_url"]
        reg = reg if reg.startswith("http") else site_url + reg.lstrip("/")
        lines.append(f"- 案内メール（無料のメール登録）: {reg}")
    lines.append(f"- 参加費とお申し込み: {site_url}join/")
    lines.append(f"- 法人の方へ: {site_url}join/corporate/")

    lines.append("")
    lines.append("## ページ一覧")
    lines.append("")
    seen = set()
    for title, url, desc in sorted(_pages, key=lambda p: p[1]):
        if url in seen:
            continue
        seen.add(url)
        lines.append(f"- [{title}]({url})" + (f": {desc}" if desc else ""))

    news = extra.get("news_site_url")
    if news:
        lines.append("")
        lines.append("## 関連サイト")
        lines.append("")
        # ライブラリー（B）には、日々の読み解きのほかに用語集・セッションの記録・
        # 参加者向けガイドが載っている。**掲載場所があちらに移ったものは、ここから
        # 辿れるようにしておく**（本サイトの nav には戻さない方針のため）。
        site = news.rstrip("/").rsplit("/d", 1)[0]
        lines.append(f"- AI戦略ライブラリー（毎日の読み解き・AI関連イベント）: {news}")
        lines.append(f"- 用語集: {site}/terms/")
        lines.append(f"- 参加ガイド（当日の流れ・手元の準備）: {site}/guide/")
        lines.append(f"- セッションの記録（各回で語られた論点）: {site}/context/")

    out = os.path.join(config["site_dir"], "llms.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
