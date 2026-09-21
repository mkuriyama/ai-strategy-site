"""ビルド時のデータ書き出しと、公開範囲の調整、`extra:` の検査。

## ダイジェストの扱い（2026年9月〜）

**「載せないが、URLを知っていれば開ける」。** ページは前のURLのまま残す ――
案内メールで配ったリンクと、Circle の詳細版記事からの「簡易版はこちら」が
生きているため。一方で、登録前の人が辿り着く経路は塞ぐ:

  - nav から外す（`mkdocs.yml`）
  - 本文ページ（月次テーマ・開催スケジュール・開催履歴・ホームの新着）から
    リンクを外す
  - `<meta name="robots" content="noindex">`（`overrides/main.html`）
  - sitemap.xml から除く（この hook の `on_post_build`）
  - `llms.txt` から除く（`hooks/seo_files.py`）
  - サイト内検索から除く（各 .md の front-matter `search: exclude: true`）

⚠ これは**アクセス制御ではない**。URLを知っていれば誰でも読める。本当に閉じるには
認証が要る（ニュースサイト側に作る会員限定の場所）。robots.txt で `Disallow` に
しないこと ―― クロールを止めると noindex が読まれず、既に索引された分が消えない。

## 書き出し

**`site/data/rounds.json`（公開）** … 各回の表題・領域・開催日・要約。開催履歴ページ
に出しているのと同じ内容を機械可読にしたもの。ニュースサイト（B）が回ページの
見出しに使う。パックの `theme` は「〜（実装・第1層 [1E]…）」のように枠組みの注記まで
含む運用の文字列で、読み手に見せる名前ではないため。

**`site/data/glossary.json`（公開）** … 用語集（セクション・用語・定義）。**正本はこの
サイトの `docs/glossary.md`**（用語の追加手順も `docs/includes/abbreviations.md` と
セットのまま）。B はこれを読んで自前の用語集ページを描く。取得元を差し替えたく
なったら B 側の `PROJECT_DATA_BASE` 1か所。

**`site/data/areas.json`（公開）** … 5×5×5 の枠組み（3層 × 5切り口＝15領域）。**正本は
`docs/about/philosophy.md` の表**。B が「どの領域を扱ってきたか」の地図を描くのに使う。
15 個そろわなければビルドを止める（表の書式を変えたときに、片側だけ静かに減るのを防ぐ）。

**`.build/digests.json`（公開しない）** … ダイジェストの描画済み本文（図の inline SVG・
用語ツールチップ込み）。`site/` の外に置くので GitHub Pages は配らない。会員限定の
場所へ運ぶときの材料。
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
from urllib.parse import urljoin

# src_uri（例 "digests/vol-04.md"） -> (絶対URL, 加工済みHTML, title, description)
# **ダイジェストだけを入れる。** 下の `_digests()` が全要素に `_DIGEST.match()` を
# 当てるので、別の種類のページを混ぜると落ちる（用語集を入れて実際に落とした）。
_pages: dict[str, tuple[str, str, str, str]] = {}

# 用語集・設計思想の描画済み本文。`_pages` とは別に持つ（上のとおり）
_glossary_html = ""
_philosophy_html = ""

_DIGEST = re.compile(r"^digests/(vol-[0-9a-z-]+)\.md$")
_GLOSSARY = "glossary.md"
_PHILOSOPHY = "about/philosophy.md"
_ABBR = re.compile(r"<abbr[^>]*>(.*?)</abbr>", re.S)
_TAG = re.compile(r"<[^>]+>")
_SECTION = re.compile(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|\Z)", re.S)
_LEAD = re.compile(r"<p>(.*?)</p>", re.S)
_TERM = re.compile(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", re.S)
_NUM = re.compile(r"^\s*\d+\.\s*")
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
    サイト上は問題ないが、そのまま渡すと文書の中に文書が入る。
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

    運ぶ先では日程が `<h2>` になる。ダイジェスト側の `<h2>` をそのまま置くと
    日程と同じ高さになり、文書の階層が崩れる。
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
    src = page.file.src_uri or ""
    if src == _GLOSSARY:
        global _glossary_html
        _glossary_html = page.content or ""
        return context
    if src == _PHILOSOPHY:
        global _philosophy_html
        _philosophy_html = page.content or ""
        return context
    if not _DIGEST.match(src):
        return context
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    _pages[page.file.src_uri] = (
        urljoin(site_url, page.url),
        page.content or "",
        page.meta.get("title") or page.title or "",
        (page.meta.get("description") or "").strip(),
    )
    return context


def _rounds(config) -> list[dict]:
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    out = []
    for entry in (config.get("extra", {}) or {}).get("history") or []:
        out.append({
            "session_no": entry.get("round"),
            "title": entry.get("title") or "",
            "area": entry.get("area") or "",
            "dates": entry.get("dates") or "",
            "summary": entry.get("summary") or "",
            "image": urljoin(site_url, entry["image"]) if entry.get("image") else "",
        })
    return out


def _digests(config) -> list[dict]:
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    digest_urls = {url: _DIGEST.match(src).group(1) for src, (url, *_) in _pages.items()}
    out = []
    for entry in (config.get("extra", {}) or {}).get("history") or []:
        items = []
        for src in entry.get("digests") or []:
            got = _pages.get(src)
            if not got:
                continue
            url, html, title, desc = got
            slug = _DIGEST.match(src).group(1)
            html = _links(_demote(_strip_footer(_unwrap(html))), url, digest_urls).strip()
            for token, why in (("<html", "文書の殻が残っている"),
                               ("cta-pair", "footer_cta を落とし損ねている"),
                               ("<h1", "h1 が残っている"),
                               ("headerlink", "permalink の ¶ が残っている")):
                if token in html:
                    from mkdocs.exceptions import PluginError

                    raise PluginError(f"digests.json: {slug} の本文に {why}（{token}）")
            items.append({
                "slug": slug,
                # `vol-0Nb` が追加開催（B日程）。命名規則そのまま
                "kind": "sub" if slug.endswith("b") else "main",
                "url": url,
                "title": title,
                "description": desc,
                "html": html,
            })
        if items:
            out.append({"session_no": entry.get("round"), "digests": items})
    return out


def _plain(html: str) -> str:
    """素のテキストにする。

    ツールチップの殻（`<abbr>`）と permalink（`¶` のリンク）を先に落とす ――
    タグだけ剥がすと `¶` が文字として残り、見出しが「AI・生成AIの基本¶」になる。
    """
    return _TAG.sub("", _ABBR.sub(r"\1", _HEADERLINK.sub("", html))).strip()


def _glossary(config) -> list[dict]:
    """描画済みの用語集を、セクション → 用語 → 定義 に畳む。

    Markdown を読み直さず `page.content` から取るのは、定義リスト（`:   ` 記法）の
    解釈を2箇所に持たないため。定義の中の**ツールチップの殻だけ外す** ―― 用語集の
    中で用語集の語にツールチップが付くのは入れ子で、運んだ先では邪魔になる。
    """
    if not _glossary_html:
        return []
    body = _unwrap(_strip_footer(_glossary_html))
    out = []
    for m in _SECTION.finditer(body):
        title = _NUM.sub("", _plain(m.group(1)))
        block = m.group(2)
        lead = _LEAD.search(block.split("<dl>")[0]) if "<dl>" in block else None
        terms = [{"term": _plain(t), "definition": _plain(d)}
                 for t, d in _TERM.findall(block)]
        if terms:
            out.append({"title": title,
                        "lead": _plain(lead.group(1)) if lead else "",
                        "terms": terms})
    return out


_ROW = re.compile(r"<tr>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>", re.S)
_AREA = re.compile(r"\[(\d[A-Z])\]\s*(.*?)\s*──\s*(.*)", re.S)


def _areas() -> list[dict]:
    """5×5×5 の枠組みを、設計思想ページの表から読む。

    **正本は `docs/about/philosophy.md` の表**。ここで別に定義し直すと、表を直した
    ときに片側だけが古くなる ―― 15行を2箇所に書く価値はない。

    表の各行は「層」と「5つの切り口」の2列で、切り口は `<br>` 区切りの
    `**[1A]** 名前 ── 説明` という形をしている。
    """
    if not _philosophy_html:
        return []
    out = []
    for layer_cell, areas_cell in _ROW.findall(_unwrap(_philosophy_html)):
        # 「**第1層**<br>実装方法<br>（業務・施策）」→ 第1層 / 実装方法（業務・施策）
        parts = [_plain(x) for x in re.split(r"<br\s*/?>", layer_cell)]
        parts = [x for x in parts if x]
        if not parts:
            continue
        layer, kind = parts[0], "".join(parts[1:])
        for seg in re.split(r"<br\s*/?>", areas_cell):
            m = _AREA.search(_plain(seg))
            if m:
                out.append({"code": m.group(1), "layer": layer, "layer_kind": kind,
                            "name": m.group(2), "description": m.group(3)})
    return out


def _check_areas(areas: list[dict]) -> None:
    """15領域そろっているか。**足りなければビルドを止める。**

    表の書式を変えると、この読み取りは静かに件数を減らす。減ったまま配ると、
    B の地図から領域が消えるだけで、どちらの画面にもエラーは出ない。
    """
    codes = [a["code"] for a in areas]
    want = [f"{n}{c}" for n in (1, 2, 3) for c in "ABCDE"]
    if codes != want:
        from mkdocs.exceptions import PluginError

        raise PluginError(
            "areas.json: 5×5×5 の枠組みを 15 領域そろって読めませんでした"
            f"（読めたのは {len(codes)} 個: {codes}）。"
            f"{_PHILOSOPHY} の表の書式（`**[1A]** 名前 ── 説明` を `<br>` 区切り、"
            "層と切り口の2列）が変わっていないか確認してください")


def _strip_digests_from_sitemap(config) -> None:
    """sitemap.xml からダイジェストの行を落とす。

    MkDocs は全ページを sitemap に入れる。noindex を付けてあるので索引はされないが、
    「載せない」と決めたものを自分から申告する理由がない。
    """
    import gzip

    path = pathlib.Path(config["site_dir"]) / "sitemap.xml"
    if not path.is_file():
        return
    xml = path.read_text(encoding="utf-8")
    kept = re.sub(r"\s*<url>\s*<loc>[^<]*/digests/[^<]*</loc>.*?</url>", "", xml, flags=re.S)
    # 用語集も同じ（掲載場所はライブラリー側の /terms/。あちらの sitemap に載っている）
    kept = re.sub(r"\s*<url>\s*<loc>[^<]*/glossary/</loc>.*?</url>", "", kept, flags=re.S)
    if kept == xml:
        return
    path.write_text(kept, encoding="utf-8")
    gz = path.with_suffix(".xml.gz")
    if gz.is_file():
        gz.write_bytes(gzip.compress(kept.encode("utf-8")))


def on_post_build(config):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    site_url = (config.get("site_url") or "").rstrip("/") + "/"

    out_dir = os.path.join(config["site_dir"], "data")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "rounds.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": now, "site": site_url, "rounds": _rounds(config)},
                  f, ensure_ascii=False, separators=(",", ":"))

    sections = _glossary(config)
    with open(os.path.join(out_dir, "glossary.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": now, "site": site_url,
                   "source": site_url + "glossary/", "sections": sections},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"[export] data/glossary.json に {len(sections)}節・"
          f"{sum(len(x['terms']) for x in sections)}語")

    areas = _areas()
    _check_areas(areas)
    with open(os.path.join(out_dir, "areas.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": now, "site": site_url,
                   "source": site_url + "about/philosophy/", "areas": areas},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"[export] data/areas.json に {len(areas)}領域")

    _strip_digests_from_sitemap(config)

    # **`site/` の外へ置く。** ここに入れると GitHub Pages がそのまま配ってしまう。
    path = pathlib.Path(config["config_file_path"]).parent / ".build" / "digests.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    rounds = _digests(config)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"generated": now, "site": site_url, "rounds": rounds},
                  f, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(r["digests"]) for r in rounds)
    print(f"[export] {path} に {len(rounds)}回・{n}本（公開されない置き場）")
