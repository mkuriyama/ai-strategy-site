# CLAUDE.md — AI戦略実践プロジェクト ポータル 保守ガイド

このファイルは、本サイト（MkDocs Material + GitHub Pages）を**回ごとに更新する際の手順書**です。
人間の作業メモであると同時に、Claude Code が作業時に最初に読むファイルでもあります。
新しい回の開催に合わせて更新を依頼されたら、まず本ファイルの「毎回の更新チェックリスト」に従ってください。

公開URL: <https://ai-strategy.antecanis.com/>
主催: 栗山実／株式会社アンテカニス

---

## サイト構成と対応ファイル

> ⚙ **アーキテクチャ更新（2026年6月）**: ホームは縦長ランディングに刷新。専用テンプレート
> `overrides/home.html` で描画し、`docs/index.md` は front-matter（`template: home.html`）のみ。
> **次回開催・参加費・登録URLは `mkdocs.yml` の `extra:` が単一ソース**（本文にハードコードしない）。
> マクロは `main.py`（`session_cards` / `register_button` / `footer_cta`）。後述の
> 「単一ソース運用」「ホームの仕組み」を参照。

```
docs/
├─ index.md                     ホーム（front-matterのみ。実体は overrides/home.html）
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
    ├─ profile.jpg               主催者写真（最適化済・ホームの主催者カードでも使用）
    ├─ flyer.html                A4印刷用チラシ（スタンドアロン・回ごとに更新）
    ├─ img/                      ホーム/各ページ用の画像・図
    │   ├─ session-build.png       事業デザイン対抗戦の制作画面（ヒーロー/セッション）
    │   ├─ session-result.png      AI戦略対抗戦の合議結果画面（セッション/テーマ）
    │   ├─ community-circle.png    参加者コミュニティ(Circle)。※日付写込みあり＝GitHub Pages専用
    │   └─ pricing-flow.svg / pricing-tiers.svg  料金図（join に inline 埋め込み済の元SVG）
    └─ antecanis_*.png / profile_*.jpg   元画像（配信からは exclude_docs で除外）

overrides/
├─ main.html                    全ページ共通のお知らせバーCTA（announceブロック）
└─ home.html                    ホーム（縦長ランディング）の専用テンプレート
main.py                         mkdocs-macros のマクロ定義（単一ソースを各ページへ流し込む）
mkdocs.yml                      設定・ナビ(nav)・配色・copyright・**extra:（単一ソースデータ）**
hooks/abbr_cjk.py               日本語の用語ツールチップを成立させる（変更不要）
requirements.txt                material[imaging] / macros / glightbox
```

ナビ（タブ）: ホーム / プロジェクトについて / セッション / ガイド・用語集 / 参加する

---

## 毎回の更新チェックリスト（新しい回の開催ごと）

> ✅ **次回開催・参加費は `mkdocs.yml` の `extra:` を1か所更新すれば、ホーム/schedule/join に
> 自動反映**されます（以前のような index.md と schedule.md の二重編集は不要になりました）。

1. **次回開催・参加費（単一ソース）** `mkdocs.yml` の `extra:`
   - `extra.next_session_short`（ヘッダー/お知らせバー/導線の短縮表記）
   - `extra.sessions`（次回回の配列：`label` / `kind`(main|sub) / `date` / `note`）
   - `extra.pricing`（早期枠・定価の金額）
   - これだけで、ホームのライブパネル・schedule の「次回開催」カード・join の価格表が更新される。
2. **開催スケジュールの月次表** `docs/sessions/schedule.md`
   - 「今後の月次予定（仮）」表：終了した回に「※開催済」を付け、必要なら行を追加
   - 「次回開催」カードは `{{ session_cards() }}` マクロ（手編集不要）。
   - ※ホームの「次回開催」は overrides/home.html が `extra.sessions` を直接描画（手編集不要）。
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
| 次回開催の日程 | **`mkdocs.yml` の `extra.sessions` / `extra.next_session_short` の1か所のみ**（ホーム・schedule・お知らせバーへ自動反映） |
| 参加費の金額 | **`mkdocs.yml` の `extra.pricing` の1か所のみ**（ホーム・join へ自動反映）。ただし `join` の料金図SVGは画像内テキストなので別途手修正が必要 |
| 用語の定義 | `docs/glossary.md` と `docs/includes/abbreviations.md` の**両方**（定義文を一致させる） |
| 登録フォームURL | **`mkdocs.yml` の `extra.register_url` の1か所のみ**（通常は固定: `https://mailchi.mp/antecanis/ai-strategy`） |

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

## 単一ソース運用とホームの仕組み（重要）

- **変動情報の正本は `mkdocs.yml` の `extra:`**。`sessions` / `next_session_short` / `pricing` /
  `register_url` をここで定義し、**本文（.md）にハードコードしない**。
- **マクロ（`main.py`）**:
  - `{{ session_cards() }}` … `extra.sessions` から「次回開催」カードを描画（schedule で使用）
  - `{{ register_button("ラベル") }}` … 登録URLボタン
  - `{{ footer_cta("リンク1", "リンク2", …) }}` … 全ページ末尾の共通動線（関連リンク＋登録CTA）
  - マクロは**全 .md ページが Jinja2 で処理される**ことを意味する。本文に素の `{{ ` `{%` `{#` を
    書かない（特に attr_list の `{#id}` は Jinja コメントと衝突する。見出しIDは付けず、
    CJK見出しは `toc.slugify`(Unicode保持) が生成するアンカーを使う）。
- **ホーム**は `overrides/home.html`（`base→main→home` の継承）。`docs/index.md` は front-matter
  （`template: home.html` と `hide: [navigation, toc]`、`description`）のみ。セクションのコピーは
  テンプレート内、スタイルは `extra.css` の `.home-landing` 配下。
- **お知らせバーCTA**は `overrides/main.html` の `announce` ブロックで全ページに表示。
- **OGP/ソーシャルカード**（`social` プラグイン）はフォント取得にネットワークが要るため、
  **ローカルでは無効（既定）／CI でのみ有効**（`.github/workflows/ci.yml` が `CARDS=true` と
  画像ライブラリ導入を行う）。ローカルで試すには `CARDS=true mkdocs build`（要ネット接続）。

---

## ビルドと公開

```bash
pip install -r requirements.txt        # 初回のみ（material[imaging]/macros/glightbox を含む）
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

- **配色**: コーポレートティール `#004455` ＋ ゴールド `#C0962F`。見出しは Noto Serif JP。
  ブランドトークンは `extra.css` 冒頭の `:root`（`--teal/--teal2/--teal-deep/--gold/--gold-pale/
  --gold-soft/--pale/--line/--ink/--muted/--paper`）に集約。料金図SVG・ホームもこれに一致。
  変更は `docs/stylesheets/extra.css` と `mkdocs.yml`（palette: custom）。
  金（gold）は **ボタン＋意味的アクセント1点（ライブパネルの本編タグ）** に限定（キャッチコピーの
  強調には使わない＝色の濃淡＋細い下線で表現。home-draft 準拠）。
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
