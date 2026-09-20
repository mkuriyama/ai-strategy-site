"""ダイジェストの**描画済み本文**を `site/data/digests.json` に書き出す MkDocs hook。

## なぜ要るか

ニュースサイト（B）の「回のページ」（`/context/S0N/`）に、各回の図と叙述をそのまま
載せるため。文章は書き直さず、ここで作ったものを運ぶ。

## なぜ Markdown ではなく HTML を渡すのか

**描画のコードを2つ持たないため。** ダイジェストの本文は素の Markdown ではなく、
`!!! info` の囲み・`<figure markdown="span">`・`<ul class="dg-meta">`・用語ツールチップ
（`hooks/abbr_cjk.py` が付ける `<abbr>`）が混ざっている。B 側で Markdown を解釈し直すと、
同じ拡張構成を2箇所に持つことになり、必ず片方だけが直される。**すでに正しく描けている
このビルドの出力をそのまま渡す。**

## 渡す前にやる加工

- 末尾の `{{ footer_cta(...) }}` ブロックを落とす（B には B の導線がある）
- `<h1>` を落とし、見出しを1段下げる（B のページでは日程が `<h2>` になるため）
- 見出しの `id` と `¶` のリンクを落とす（同じページに2日程が並ぶので id が衝突する）
- 相対リンクを絶対URLにする。ただし**同じ回のもう一方の日程へのリンクだけは
  `#digest:vol-04b` の形**に置き換える。B 側では同一ページ内なので、そちらで
  ページ内アンカーに解決する（A の URL 文字列を B に覚えさせない）

出力先は `site/data/digests.json`。B のビルドが HTTP で取りに来る。
用語集を B へ渡すときも、この hook に足して同じ場所から配る。
"""

from __future__ import annotations

import datetime
import json
import os
import re
from urllib.parse import urljoin

# src_uri（例 "digests/vol-04.md"） -> (絶対URL, 加工済みHTML, title, description)
_pages: dict[str, tuple[str, str, str, str]] = {}

_DIGEST = re.compile(r"^digests/(vol-[0-9a-z-]+)\.md$")
_HEADERLINK = re.compile(r'<a class="headerlink".*?</a>', re.S)
_H = re.compile(r"<(/?)h([1-6])([^>]*)>")
_H1 = re.compile(r"<h1[^>]*>.*?</h1>\s*", re.S)
_ATTR = re.compile(r'\b(href|src)="([^"]*)"')
_ID = re.compile(r'\s+id="[^"]*"')


def on_config(config):
    """`extra:` に**キーとして読まれなかった語**が無いか確かめ、あればビルドを止める。

    YAML 1.1 は `no:` `yes:` `on:` `off:` `y:` `n:` を真偽値として読む。つまり
    `- no: 4` と書くと、キーは文字列 `"no"` ではなく `False` になり、
    `r.get("no")` は静かに `None` を返す。**エラーにならず、表示だけが欠ける。**

    実際に起きた：開催履歴のカードが「第回」と出ていた（`extra.history` の `no:`）。
    画面を見ないと気づけず、見ても見落としやすい。キーを `round:` に改めたうえで、
    同じ踏み方を防ぐためにここで落とす。
    """
    bad: list[str] = []

    def walk(node, path):
        if hasattr(node, "items"):
            for k, v in node.items():
                if not isinstance(k, str):
                    bad.append(f"{path}: {k!r}（{type(k).__name__}）")
                walk(v, f"{path}.{k}")
        elif isinstance(node, (list, tuple)):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(config.get("extra") or {}, "extra")
    if bad:
        from mkdocs.exceptions import PluginError

        raise PluginError(
            "mkdocs.yml の extra: に、YAML が文字列キーとして読まなかった項目があります"
            "（no/yes/on/off は真偽値になります。引用するか別の語に変えてください）:\n  "
            + "\n  ".join(bad)
        )
    return config


def on_pre_build(config):
    _pages.clear()


def _unwrap(html: str) -> str:
    """`<html><head></head><body>…</body></html>` の殻を外す。

    用語ツールチップの hook が本文を HTML として解析し直すため、`page.content` は
    断片ではなく1枚の文書の形で返ってくる。テーマのテンプレートは中身だけを使うので
    サイト上は問題ないが、そのまま B へ渡すと文書の中に文書が入る。
    """
    for head in ("<html><head></head><body>", "<html><body>"):
        if html.startswith(head):
            html = html[len(head):]
            break
    for tail in ("</body></html>", "</body>"):
        if html.endswith(tail):
            html = html[: -len(tail)]
            break
    return html


def _strip_footer(html: str) -> str:
    """`footer_cta()` が吐く「区切り線＋関連ページ＋CTA」を末尾ごと落とす。

    マクロは必ず `---`（＝`<hr>`）を置いてから `<div class="cta-pair">` を出すので、
    その `<div>` の直前の `<hr>` から後ろを捨てればよい。
    """
    i = html.find('<div class="cta-pair"')
    if i < 0:
        return html
    j = html.rfind("<hr", 0, i)
    return html[:j] if j >= 0 else html[:i]


def _demote(html: str) -> str:
    """見出しを1段下げ、id と permalink を落とす。

    B の回ページでは「A日程」「B日程」が `<h2>`。ダイジェスト側の `<h2>` をそのまま
    置くと日程と同じ高さになり、文書の階層が崩れる（見出しの構造は検索側も読む）。
    """
    html = _HEADERLINK.sub("", html)
    html = _H1.sub("", html, count=1)

    def sub(m):
        close, level, attrs = m.group(1), int(m.group(2)), m.group(3)
        return f"<{close}h{min(level + 1, 6)}{_ID.sub('', attrs)}>"

    return _H.sub(sub, html)


def _links(html: str, page_url: str, digest_urls: dict[str, str]) -> str:
    """相対リンクを絶対URLに。同じ回のもう一方の日程だけは合図に置き換える。"""

    def sub(m):
        attr, val = m.group(1), m.group(2)
        if not val or val.startswith(("http://", "https://", "#", "mailto:", "data:")):
            return m.group(0)
        absolute = urljoin(page_url, val)
        slug = digest_urls.get(absolute.rstrip("/") + "/")
        if attr == "href" and slug:
            return f'{attr}="#digest:{slug}"'
        return f'{attr}="{absolute}"'

    return _ATTR.sub(sub, html)


def on_page_context(context, page, config, nav):
    m = _DIGEST.match(page.file.src_uri or "")
    if not m:
        return context
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    url = urljoin(site_url, page.url)
    _pages[page.file.src_uri] = (
        url,
        page.content or "",
        page.meta.get("title") or page.title or "",
        (page.meta.get("description") or "").strip(),
    )
    return context


def on_post_build(config):
    if not _pages:
        return
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    history = (config.get("extra", {}) or {}).get("history") or []

    # 「この URL はどのダイジェストか」の対応表。リンク書き換えで使う。
    digest_urls = {url: _DIGEST.match(src).group(1) for src, (url, *_ ) in _pages.items()}

    rounds = []
    for entry in history:
        digests = []
        for src in entry.get("digests") or []:
            got = _pages.get(src)
            if not got:
                continue
            url, html, title, desc = got
            slug = _DIGEST.match(src).group(1)
            html = _links(_demote(_strip_footer(_unwrap(html))), url, digest_urls)
            digests.append({
                "slug": slug,
                # `vol-0Nb` が追加開催（B日程）。A 側の命名規則そのまま
                "kind": "sub" if slug.endswith("b") else "main",
                "url": url,
                "title": title,
                "description": desc,
                "html": html.strip(),
            })
        if not digests:
            continue
        rounds.append({
            "session_no": entry.get("round"),
            "title": entry.get("title") or "",
            "area": entry.get("area") or "",
            "dates": entry.get("dates") or "",
            "summary": entry.get("summary") or "",
            "image": urljoin(site_url, entry["image"]) if entry.get("image") else "",
            "digests": digests,
        })

    # 加工し損ねたものを黙って配らない。B 側で気づくのは「ページが変」になってから。
    for r in rounds:
        for d in r["digests"]:
            for token, why in (("<html", "文書の殻が残っている"),
                               ("cta-pair", "footer_cta を落とし損ねている"),
                               ("<h1", "h1 が残っている"),
                               ("headerlink", "permalink の ¶ が残っている")):
                if token in d["html"]:
                    from mkdocs.exceptions import PluginError

                    raise PluginError(f"digests.json: {d['slug']} の本文に {why}（{token}）")

    out_dir = os.path.join(config["site_dir"], "data")
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "site": site_url,
        "rounds": rounds,
    }
    with open(os.path.join(out_dir, "digests.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
