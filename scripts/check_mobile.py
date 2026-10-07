"""ビルドしたサイトを**携帯の幅で実際に開いて**、読める形になっているか確かめる。

## なぜ要るか

2026年10月に測ったところ、/join/ の図1・図2（当時は横長の inline SVG）が、
携帯の幅では文字が6〜8px相当まで縮んでいた。「更新と解約のしくみ」という、
申込の判断に一番効く説明が、拡大しないと読めない状態だった。

見つけにくいのは、**PCの幅では何も起きない**ため。SVG は viewBox で縮むので
横にはみ出しもしない。コードを読んでも分からず、携帯で開くまで誰も気づかない。
だから実際に描画して測る（ライブラリー（B）の `scripts/check_mobile.py` と同じ考え方）。

## 何を見るか

- 横スクロールが出ていないか（`scrollWidth` が `clientWidth` を超えていないか）
- inline SVG の文字が、画面上で `MIN_TEXT_PX` 以上あるか
  （SVG の font-size × 実際に縮められた倍率で測る）

ダイジェスト（`digests/`）は「載せないが、URLを知っていれば開ける」ページで、
図は今後 B の会員限定の場所へ移すため、**所見を出すだけで落とさない**。

## 使い方

    python3 -m mkdocs build
    python3 scripts/check_mobile.py            # site/ を見る
    python3 scripts/check_mobile.py /tmp/site  # 別の場所にビルドしたとき

所見があれば終了コード 1。playwright が無ければ何もせず 0。
"""
from __future__ import annotations

import asyncio
import functools
import http.server
import os
import pathlib
import socketserver
import sys
import threading

# 実機で多い幅。320 は小型機・文字拡大時の下限として入れてある。
WIDTHS = (320, 360, 390, 412)
# 本文の最小（Material の携帯の本文は16px、注記類で12〜13px）より下は読めない扱い
MIN_TEXT_PX = 10
# 落とさず所見だけ出す場所
WARN_ONLY = ("digests/",)
# 開かない場所（素材）。転送用のページは中身で見分けて飛ばす
SKIP = ("assets/",)

CHROME = os.environ.get("CHECK_MOBILE_CHROME", "")

MEASURE = r"""async (minPx) => {
  const de = document.documentElement;
  const small = [];
  // <img src="*.svg"> の図も測る（開催履歴の図など）。画像の中の文字は DOM に出ないので、
  // SVG を取り寄せて最小の font-size と viewBox の幅を読み、表示幅との比で画面上の大きさを出す
  for (const img of document.querySelectorAll('img[src$=".svg"]')) {
    const w = img.getBoundingClientRect().width;
    if (!w || img.closest('.md-header, .md-footer, .md-nav')) continue;
    let txt;
    try { txt = await (await fetch(img.currentSrc || img.src)).text(); } catch (e) { continue; }
    const doc = new DOMParser().parseFromString(txt, 'image/svg+xml');
    const svg = doc.documentElement;
    const vb = (svg.getAttribute('viewBox') || '').split(/[\s,]+/).map(Number);
    if (vb.length !== 4 || !vb[2]) continue;
    const sizes = [...doc.querySelectorAll('text, tspan')].map(t =>
      parseFloat(t.getAttribute('font-size') || (t.getAttribute('style') || '').match(/font-size:\s*([\d.]+)/)?.[1]))
      .filter(n => n > 0);
    if (!sizes.length) continue;
    const px = Math.min(...sizes) * w / vb[2];
    if (px < minPx) small.push({ px: Math.round(px * 10) / 10,
      text: '画像 ' + (img.getAttribute('src') || '').split('/').pop() });
  }
  for (const t of document.querySelectorAll('svg text, svg tspan')) {
    const r = t.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const ctm = t.getScreenCTM();
    if (!ctm) continue;
    const px = parseFloat(getComputedStyle(t).fontSize) * Math.hypot(ctm.a, ctm.b);
    if (px < minPx) small.push({ px: Math.round(px * 10) / 10, text: t.textContent.trim().slice(0, 20) });
  }
  return { over: de.scrollWidth - de.clientWidth, small };
}"""


def pages(root: pathlib.Path) -> list[str]:
    out = []
    for f in sorted(root.rglob("index.html")):
        rel = f.parent.relative_to(root).as_posix()
        rel = "" if rel == "." else rel + "/"
        if rel.startswith(SKIP):
            continue
        # redirects プラグインが作る転送ページは見ない
        if 'http-equiv="refresh"' in f.read_text(encoding="utf-8", errors="ignore")[:2000]:
            continue
        out.append("/" + rel)
    return out


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Server(socketserver.TCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        """ブラウザが次のページへ移った後の BrokenPipe を黙らせる（表示の検査とは無関係）。"""


async def run(root: pathlib.Path) -> int:
    from playwright.async_api import async_playwright

    paths = pages(root)
    if not paths:
        print(f"[mobile] {root} にページが無い（先に mkdocs build を）")
        return 1

    handler = functools.partial(Quiet, directory=str(root))
    srv = Server(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    bad: list[str] = []
    warn: list[str] = []
    try:
        async with async_playwright() as pw:
            br = await pw.chromium.launch(**({"executable_path": CHROME} if CHROME else {}))
            for width in WIDTHS:
                ctx = await br.new_context(viewport={"width": width, "height": 860},
                                           is_mobile=True, has_touch=True, device_scale_factor=2)
                # 外部（フォント・計測・Turnstile）は読まない。結果を安定させ、速く回すため
                await ctx.route("**/*", lambda r: r.continue_()
                                if r.request.url.startswith(f"http://127.0.0.1:{port}/")
                                else r.abort())
                pg = await ctx.new_page()
                for path in paths:
                    await pg.goto(f"http://127.0.0.1:{port}{path}", timeout=60000)
                    m = await pg.evaluate(MEASURE, MIN_TEXT_PX)
                    found = []
                    if m["over"] > 0:
                        found.append(f"{path} が {width}px で横に {m['over']}px はみ出している")
                    if m["small"]:
                        ex = "・".join(f"「{s['text']}」{s['px']}px" for s in m["small"][:3])
                        found.append(f"{path} の図の文字 {len(m['small'])}個が {width}px で"
                                     f" {MIN_TEXT_PX}px 未満（{ex}）")
                    (warn if path.lstrip("/").startswith(WARN_ONLY) else bad).extend(found)
                await ctx.close()
            await br.close()
    finally:
        srv.shutdown()
        srv.server_close()

    if warn:
        print(f"[mobile] △ 所見のみ（落とさない）{len(warn)}件")
        for w in warn[:8]:
            print("   " + w)
    if bad:
        print(f"[mobile] ✗ {len(bad)}件")
        for b in bad[:20]:
            print("   " + b)
        return 1
    print(f"[mobile] ✓ {len(paths)}ページ × {len(WIDTHS)}幅、"
          f"横へのはみ出しなし・図の文字は {MIN_TEXT_PX}px 以上")
    return 0


def main() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("[mobile] playwright が入っていないので飛ばす")
        raise SystemExit(0)
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site").resolve()
    raise SystemExit(asyncio.run(run(root)))


if __name__ == "__main__":
    main()
