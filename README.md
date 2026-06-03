# AI戦略実践プロジェクト ドキュメント

AI戦略実践プロジェクトの参加者向けドキュメントサイトのソースです。
「スタートガイド」と「ボキャブラリーリスト（用語集）」を公開しています。

**公開サイト** → https://ai-strategy.antecanis.com/

## このサイトについて

- **スタートガイド** — 初めて参加される方が、プロジェクトの背景にある考え方を掴み、
  当日のセッションにスムーズに臨むための手引き
- **ボキャブラリーリスト** — セッションで登場するAI・技術・戦略関連の用語集

専門用語は本文中にカーソルを重ねると定義がツールチップ表示され、用語集ページと
相互にリンクしています。日本語の全文検索にも対応しています。

## 技術構成

[MkDocs](https://www.mkdocs.org/) ＋
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) で構築し、
GitHub Pages で公開しています。`main` ブランチへの更新は GitHub Actions により
自動でデプロイされます。

```
mkdocs.yml                    # サイト設定
requirements.txt              # 依存パッケージ
hooks/abbr_cjk.py             # 日本語の用語ツールチップを有効化する hook
.github/workflows/ci.yml      # 自動デプロイ
docs/
├─ index.md                   # ホーム
├─ start-guide.md             # スタートガイド
├─ glossary.md                # ボキャブラリーリスト（用語集）
└─ includes/abbreviations.md  # ツールチップ用の用語定義
```

## ローカルでのプレビュー

```bash
pip install -r requirements.txt
mkdocs serve     # http://127.0.0.1:8000 で確認
```

## 編集の手引き

- 本文を直す: `docs/start-guide.md` / `docs/glossary.md` を編集
- 用語を追加する: `docs/glossary.md` に項目を加え、`docs/includes/abbreviations.md`
  に `*[用語]: 定義` を同じ定義で追記すると、本文中でツールチップ表示されます

---

株式会社アンテカニス / AI戦略実践プロジェクト
