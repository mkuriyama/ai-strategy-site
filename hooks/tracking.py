"""Material を通らない静的ページ（/welcome/・/paused/）に、計測タグを差し込む hook。

`docs/welcome/index.html`（Stripe の success URL）と `docs/paused/index.html`（cancel URL）は、
テーマを通らずにそのまま配る静的HTMLなので、`overrides/main.html` の GA4・広告タグが入らない。
ビルドの最後に、GA4（`extra.analytics`）と `overrides/partials/tracking.html` の出力を
`</head>` の前に差し込む。広告のタグは、ページの側と同じく ID が空なら読み込まれない。
`?notrack=1` で開いたブラウザでは何も送らない（tracking.html と同じ印を、GA4 より前に確かめる）。

## 申込完了（/welcome/ だけ。2026年11月〜）

Stripe の success URL に `?session_id={CHECKOUT_SESSION_ID}` が付いているとき（申込用 GAS の
`SUCCESS_URL`）、1回だけ送る：GA4 `sign_up`・Meta `StartTrial`・Google 広告のコンバージョン
（`google_ads_signup_label`）・LinkedIn（`linkedin_signup_conversion`）。

- 同じ session_id では2回送らない（このブラウザの localStorage に覚える。Google 広告には
  transaction_id、Meta には eventID としても渡すので、先方でも重複が除かれる）
- session_id は、GA4・Meta がページの URL を読む前に URL から消す（決済の ID を URL として送らない）
- session_id が無い（GAS の SUCCESS_URL がまだ古い・直接開いた）ときは何も送らない
"""

from __future__ import annotations

import os
import re

PAGES = ("welcome/index.html", "paused/index.html")
MARK = "<!-- aisia-tags -->"
_GA = re.compile(r"^G-[A-Z0-9]+$")

# GA4 より前に動かす：?notrack の印を確かめて GA4 を止める。/welcome/ では session_id を URL から外して覚える
_PRE = (
    "<script>(function(){try{var q=new URLSearchParams(location.search).get('notrack');"
    "if(q==='1')localStorage.setItem('aisia_notrack','1');if(q==='0')localStorage.removeItem('aisia_notrack');"
    "if(localStorage.getItem('aisia_notrack')==='1')window['ga-disable-%(ga)s']=true;}catch(e){}})();</script>\n"
)
_WELCOME_PRE = (
    "<script>(function(){try{var u=new URL(location.href),s=u.searchParams.get('session_id');if(!s)return;"
    "u.searchParams.delete('session_id');history.replaceState(null,'',u.pathname+u.search+u.hash);"
    "if(/^cs_(live|test)_[A-Za-z0-9]+$/.test(s))window.__aisiaCheckout=s;}catch(e){}})();</script>\n"
)
# タグ（tracking.html）のあとに動かす：申込完了を1回だけ送る
_WELCOME_POST = (
    "<script>(function(){var s=window.__aisiaCheckout,t=window.__aisiaTags||{};if(!s||t.notrack)return;"
    "var k='aisia_signups',seen=[];try{seen=JSON.parse(localStorage.getItem(k)||'[]')||[];}catch(e){}"
    "if(seen.indexOf(s)>=0)return;try{localStorage.setItem(k,JSON.stringify(seen.concat([s]).slice(-10)));}catch(e){}"
    "window.dataLayer=window.dataLayer||[];var g=function(){window.dataLayer.push(arguments);};"
    "g('event','sign_up',{method:'stripe'});if(!t.on)return;"
    "if(t.meta&&typeof window.fbq==='function')window.fbq('track','StartTrial',{},{eventID:s});"
    "if(t.ads&&t.adsSignup)g('event','conversion',{send_to:t.ads+'/'+t.adsSignup,transaction_id:s});"
    "if(t.li&&t.liSignup&&typeof window.lintrk==='function')window.lintrk('track',{conversion_id:Number(t.liSignup)});"
    "})();</script>\n"
)


def _snippet(config, welcome: bool) -> str:
    env = config.theme.get_env()
    tags = env.get_template("partials/tracking.html").render(config=config)
    ga = str(((config.get("extra") or {}).get("analytics") or {}).get("property") or "")
    head = ""
    if welcome:
        head += _WELCOME_PRE
    if _GA.match(ga):
        head += _PRE % {"ga": ga}
        head += (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];"
            "function gtag(){dataLayer.push(arguments);}"
            f"gtag('js',new Date());gtag('config','{ga}');</script>\n"
        )
    tail = _WELCOME_POST if welcome else ""
    return MARK + "\n" + head + tags.strip() + "\n" + tail


def on_post_build(config):
    for rel in PAGES:
        path = os.path.join(config["site_dir"], rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if MARK in html or "</head>" not in html:
            continue
        snippet = _snippet(config, welcome=rel.startswith("welcome/"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(html.replace("</head>", snippet + "</head>", 1))
