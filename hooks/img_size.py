"""テンプレートの <img> に、元の画像の幅と高さを書き込む（グローバル関数 `img_attrs`）。

広告用LP（/start/）の画面写真は loading="lazy" で読み込む。幅と高さを書いていないと、
読み込まれた時点でページが伸び、読んでいる文がずれる（携帯で約1,200px伸びていた）。
ページ内の移動（帯の「参加する」など）の行き先もずれる。
ビルドの時に元の画像の大きさを読んで width・height を書き、場所を先に取っておく。
表示の大きさは CSS（`width: 100%; height: auto`）が決めるので、書くのは縦横の比のため。

使い方（overrides/*.html）:
    <img src="{{ src | url }}" {{ img_attrs(src) }} alt="…">
src はサイト相対（例：assets/img/start/studio.jpg）。読めない画像なら何も書かない。
"""

from __future__ import annotations

import functools
import os

from markupsafe import Markup

try:
    from PIL import Image
except ImportError:  # 画像ライブラリが無い環境では、幅と高さを書かない（表示は変わらない）
    Image = None

_docs_dir: str | None = None


def on_config(config):
    global _docs_dir
    _docs_dir = config["docs_dir"]
    return config


@functools.lru_cache(maxsize=256)
def _size(path: str):
    if Image is None or not os.path.isfile(path):
        return None
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def img_attrs(src) -> Markup:
    if not src or not _docs_dir:
        return Markup("")
    size = _size(os.path.join(_docs_dir, str(src).lstrip("/")))
    if not size:
        return Markup("")
    return Markup(f'width="{size[0]}" height="{size[1]}"')


def on_env(env, config, files):
    env.globals["img_attrs"] = img_attrs
    return env
