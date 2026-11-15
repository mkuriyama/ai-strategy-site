"""日本語の見出しを、語の途中で改行させない（テンプレートのフィルター `phrase`）。

広告用LP（/start/）の見出しで使う。BudouX で句の切れ目を見つけて `<wbr>` を入れ、
CSS の `word-break: keep-all` と組み合わせて、改行を句の切れ目だけに限る。

CSS の `word-break: auto-phrase` は Chrome 系でしか効かない。iPhone の Safari と、
Instagram・Facebook のアプリ内ブラウザ（iPhone では Safari と同じ仕組み）では効かないので、
ビルドの時点で改行してよい位置を書き込んでおく。

使い方（overrides/*.html）:
    <h2>{{ "こんな状況に、心当たりはありませんか。" | phrase }}</h2>
文字はエスケープしてから `<wbr>` でつなぐ（HTML を含む文字列には使わない）。
"""

from __future__ import annotations

import functools

import budoux
from markupsafe import Markup, escape


@functools.lru_cache(maxsize=1)
def _parser():
    return budoux.load_default_japanese_parser()


# BudouX が語の途中で切る語。この中では改行させない（例：「据え｜置き」「お支払い｜日」「都合のよい｜方」）
KEEP = ("据え置き", "お支払い日", "都合のよい方")


def _chunks(s: str) -> list[str]:
    chunks = _parser().parse(s)
    cuts, pos = set(), 0
    for c in chunks[:-1]:
        pos += len(c)
        cuts.add(pos)
    for w in KEEP:
        i = s.find(w)
        while i >= 0:
            cuts -= set(range(i + 1, i + len(w)))
            i = s.find(w, i + 1)
    out, last = [], 0
    for c in sorted(cuts):
        out.append(s[last:c])
        last = c
    out.append(s[last:])
    return out


def phrase(text) -> Markup:
    s = str(text or "")
    if not s:
        return Markup("")
    return Markup("<wbr>").join(escape(c) for c in _chunks(s))


def on_env(env, config, files):
    env.filters["phrase"] = phrase
    return env
