"""Material を通らない静的ページ（/welcome/・/paused/）に、計測タグを差し込む hook。

`docs/welcome/index.html`（Stripe の success URL）と `docs/paused/index.html`（cancel URL）は、
テーマを通らずにそのまま配る静的HTMLなので、`overrides/main.html` の GA4・広告タグが入らない。
ビルドの最後に、GA4（`extra.analytics`）と `overrides/partials/tracking.html` の出力を
`</head>` の前に差し込む。広告のタグは、ページの側と同じく ID が空なら読み込まれない。

送るのはページビューだけ。申込の完了（/welcome/）を Meta の StartTrial や Google 広告の
コンバージョンとして送るかは、まだ決めていない。
"""

from __future__ import annotations

import os
import re

PAGES = ("welcome/index.html", "paused/index.html")
MARK = "<!-- aisia-tags -->"
_GA = re.compile(r"^G-[A-Z0-9]+$")


def _snippet(config) -> str:
    env = config.theme.get_env()
    tags = env.get_template("partials/tracking.html").render(config=config)
    ga = str(((config.get("extra") or {}).get("analytics") or {}).get("property") or "")
    head = ""
    if _GA.match(ga):
        head += (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];"
            "function gtag(){dataLayer.push(arguments);}"
            f"gtag('js',new Date());gtag('config','{ga}');</script>\n"
        )
    return MARK + "\n" + head + tags.strip() + "\n"


def on_post_build(config):
    snippet = None
    for rel in PAGES:
        path = os.path.join(config["site_dir"], rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if MARK in html or "</head>" not in html:
            continue
        snippet = snippet or _snippet(config)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html.replace("</head>", snippet + "</head>", 1))
