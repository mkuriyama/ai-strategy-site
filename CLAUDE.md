# CLAUDE.md — AI戦略実践プロジェクト ポータル 保守ガイド

このファイルは、本サイト（MkDocs Material + GitHub Pages）を**回ごとに更新する際の手順書**です。
人間の作業メモであると同時に、Claude Code が作業時に最初に読むファイルでもあります。
新しい回の開催に合わせて更新を依頼されたら、まず本ファイルの「毎回の更新チェックリスト」に従ってください。

公開URL: <https://ai-strategy.antecanis.com/>
主催: 栗山実／株式会社アンテカニス

---

## サイト構成と対応ファイル

```
docs/
├─ index.md                     ホーム（次回開催・目的別入口・紹介リンク）
├─ about/
│   ├─ index.md                 背景と狙い（＋「何でないか」）
│   ├─ philosophy.md            設計思想（3層・5×5×5の枠組み）
│   ├─ profile.md               主催者プロフィール（顔写真・会社リンク）
│   └─ share.md                 このプロジェクトを紹介する（チラシへの導線）
├─ sessions/
│   ├─ index.md                 進め方と持ち帰るもの
│   ├─ themes.md                月次テーマ（開催済み＋今後の領域）
│   └─ schedule.md              開催予定・次回案内（次回＋月次予定表）
├─ digests/
│   ├─ index.md                 ダイジェスト一覧
│   └─ vol-01.md                第1回ダイジェスト（テーマ内・SVG図解）
├─ start-guide.md               スタートガイド（受講準備・進め方）
├─ glossary.md                  用語集
├─ includes/abbreviations.md    用語ツールチップ定義（全ページに自動付与）
├─ stylesheets/extra.css        コーポレート配色・見出し等
└─ assets/
    ├─ logo-header.png           ヘッダーロゴ（白抜きワードマークをトリミング済）
    ├─ favicon.png               ファビコン
    ├─ profile.jpg               主催者写真（最適化済）
    ├─ flyer.html                A4印刷用チラシ（スタンドアロン・回ごとに更新）
    └─ antecanis_*.png / profile_*.jpg   元画像（配信からは exclude_docs で除外）

mkdocs.yml                      設定・ナビ（nav）・配色・copyright（フッタ規約リンク）
hooks/abbr_cjk.py               日本語の用語ツールチップを成立させる（変更不要）
```

ナビ（タブ）: ホーム / プロジェクトについて / セッション / ガイド・用語集 / 参加する

---

## 毎回の更新チェックリスト（新しい回の開催ごと）

> ⚠ 同じ情報が複数ファイルに載っている箇所があります。**必ず両方そろえて**ください（下の「同期が必要な箇所」参照）。

1. **開催スケジュール** `docs/sessions/schedule.md`
   - 「次回開催」カード（直近2件程度）を最新化
   - 「今後の月次予定（仮）」表：終了した回に「※開催済」を付け、必要なら行を追加
2. **ホームの「次回開催」** `docs/index.md`
   - schedule.md の「次回開催」と**同じ内容**に更新（← 重複。要同期）
3. **月次テーマ** `docs/sessions/themes.md`
   - 開催した回を「開催済みのテーマ」に追記（ダイジェストへのリンクも）
   - 「今後のテーマ領域」から消化済みを調整
4. **ダイジェスト**（新しい回の分） … 下記「ダイジェストの追加手順」
5. **紹介チラシ** `docs/assets/flyer.html`
   - 新版HTML（日程等を含む完成版）に**差し替え**。print CSSを保ったスタンドアロンHTMLのまま置く
6. **用語集 ＋ ツールチップ**（新しい用語が出た回） … 下記「用語の追加手順」
7. **日付スタンプ**の確認
   - `docs/glossary.md` 末尾「◯年◯月時点」
   - `docs/start-guide.md` 末尾「◯年◯月時点」
8. **ビルド確認 → コミット → プッシュ → mainにマージ**（下記「ビルドと公開」）

---

## 同期が必要な箇所（漏れやすい！）

| 情報 | 載っているファイル |
|---|---|
| 次回開催の日程 | `docs/index.md`（ホーム）と `docs/sessions/schedule.md` の**両方** |
| 用語の定義 | `docs/glossary.md` と `docs/includes/abbreviations.md` の**両方**（定義文を一致させる） |
| 登録フォームURL | `docs/index.md` / `docs/sessions/schedule.md` / `docs/join/register.md`（通常は固定: `https://mailchi.mp/antecanis/ai-strategy`） |

---

## ダイジェストの追加手順（例：第2回 → vol-02）

1. 新しいダイジェストを `docs/digests/vol-02.md` として作成
   - vol-01.md と同じ体裁。図は **SVGをインラインで貼り付け**（テーマ内に収め、検索・ツールチップを効かせる）
   - デザインHTML（凝った図解）が提供された場合は、`<svg>…</svg>` 部分を抽出して md に埋め込む。
     末尾の販促CTA・フッターは入れない（サイトのナビが導線を担う）
2. `docs/digests/index.md` にカードを1枚追加
3. `mkdocs.yml` の `nav:` → セッション → ダイジェスト に
   `- Vol.2 第2回：（テーマ名）: digests/vol-02.md` を追加

---

## 用語の追加手順

新しい用語が出たら、**2ファイルを必ずセットで**更新します（定義文は一致させる）。

1. `docs/glossary.md` … 該当セクションに `**用語（読み/英語）**` ＋ 定義（`:   ` 始まりの定義リスト）
2. `docs/includes/abbreviations.md` … `*[用語]: 定義` を1行追加
   - ここに登録した語が、全ページ本文中でカーソル時にツールチップ表示される
   - 英字の語（API等）は単語境界、日本語の語は文中どこでもマッチ（`hooks/abbr_cjk.py` が処理）
   - 「AI」のような頻出すぎる語は**入れない**（過剰表示になるため。意図的に除外済み）
   - 短いカナ語が**別の語の一部に誤マッチ**することがある。例：「セル」は「キャン**セル**」に
     一致してしまうため、ツールチップ対象からは除外している（用語集には掲載）。
     新規の短い語を入れる前に、よくある単語の一部にならないか確認する

---

## ビルドと公開

```bash
pip install -r requirements.txt        # 初回のみ
mkdocs serve                           # ローカルプレビュー（http://127.0.0.1:8000）
mkdocs build --strict                  # リンク切れ等を含め検証（公開前に必ず通す）
```

- 作業用ブランチで編集 → コミット → プッシュ → **`main` にマージ**すると、GitHub Actions
  （`.github/workflows/ci.yml`）が `mkdocs gh-deploy` で自動デプロイします。
- **反映の遅延**: GitHub Pages がHTMLに `Cache-Control: max-age=600` を付与するため、
  既訪ブラウザは最大10分古い版を表示することがあります（変更不可・新規訪問者は即時最新）。
  自分で即確認したいときは URL に `?v=任意の数字` を付けるか、DevToolsの「キャッシュ無効化」。

---

## デザイン・規約（変更時の注意）

- **配色**: コーポレートティール `#004455` ＋ ゴールド `#b88a3e`。見出しは Noto Serif JP。
  変更は `docs/stylesheets/extra.css` と `mkdocs.yml`（palette: custom）。
- **フッタの規約リンク**（プライバシー/キャンセル/利用規約/特商法/お問い合わせ）は
  `mkdocs.yml` の `copyright:` にHTMLで記載。URLは `https://www.antecanis.com/...`。
- **決済（Stripe）リンクは公開ページに載せない**。コホート管理のうえメールで個別案内する方針。
- **大きい元画像**は `mkdocs.yml` の `exclude_docs` で配信から除外（リポジトリにはソースとして保持）。
- `hooks/abbr_cjk.py` は日本語ツールチップの要。**触らない**。
- チラシ(`flyer.html`)とダイジェストの元デザインHTMLはテーマCSSと独立。チラシは
  スタンドアロン（印刷用）のまま、ダイジェストは図のみ流用してテーマ内に再構成する。

---

## やらないこと

- 会員限定情報（Zoomリンク・当日資料・録画URL・決済リンク）は**サイトに載せない**。
- PRの作成は依頼があったときのみ。
