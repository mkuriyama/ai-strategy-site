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
│   ├─ schedule.md              開催予定・次回案内（次回＋月次予定表）
│   └─ history.md               開催履歴（`extra.history` を history_cards() で描画。本文は書かない）
├─ digests/                     **載せないが、URLを知っていれば開ける**（2026年9月〜）。
│                               ページは前のURLのまま。案内メールで配ったリンクと、
│                               Circle の詳細版からの「簡易版はこちら」が生きているため。
│                               nav・本文リンク・sitemap・llms.txt・サイト内検索からは
│                               外し、noindex を付けている。叙述と図は今後 B に作る
│                               会員限定の場所へ移す。
│   ├─ index.md                 ダイジェスト一覧（カードは最新順）
│   ├─ vol-01.md / vol-01b.md   第1回 A日程(5/26) / B日程(6/15)
│   ├─ vol-02.md / vol-02b.md   第2回 A日程(6/23) / B日程(7/10)
│   ├─ vol-03.md / vol-03b.md   第3回 A日程(7/21) / B日程(8/3)
│   └─ vol-04.md / vol-04b.md   第4回 A日程(8/18) / B日程(9/3)
│                               ※`vol-0N.md`=A日程、`vol-0Nb.md`=B日程。表記は Vol.NA / Vol.NB
├─ join/
│   ├─ index.md                 参加費とお申し込み（費用・課金図・申込・メール登録の統合ページ）
│   └─ corporate.md             法人の方へ
├─ start-guide.md               スタートガイド（参加準備・進め方）
├─ glossary.md                  用語集。**掲載場所はライブラリー（B）の /terms/ に移した**
│                               （2026年9月）。ダイジェストと同じ「載せないが、URLを
│                               知っていれば開ける」扱い ―― nav・検索・sitemap・llms.txt
│                               から外し noindex。**ファイルは正本として残す**（B が読む
│                               `site/data/glossary.json` の生成元。用語の追加手順も同じ）
├─ apply/index.html             申込リンクの転送用（スタンドアロン・navに載せない）
├─ welcome/index.html           決済完了後の着地ページ（Stripeのsuccess URL）
├─ paused/index.html            決済中断時の着地ページ（Stripeのcancel URL）
├─ includes/abbreviations.md    用語ツールチップ定義（全ページに自動付与）
├─ robots.txt                   クローラ方針（全許可＋AIクローラ明示）と sitemap の場所。静的
├─ stylesheets/extra.css        コーポレート配色・見出し等
└─ assets/
    ├─ logo-mincho-white.svg     **現行のヘッダーロゴ**（濃ティール背景用に白へ単色反転）
    ├─ logo-mincho-light.svg     プロジェクト正式ロゴ（ティール・明るい背景用の原本）
    ├─ logo-mincho-dark.svg      濃色版（全#004455。/welcome/・/paused/ で使用）
    ├─ logo-header.png           旧Antecanis社ロゴ。**現在は未使用**（履歴として保持）
    ├─ favicon.png               ファビコン
    ├─ profile.jpg               主催者写真（最適化済・ホームの主催者カードでも使用）
    ├─ flyer.html                A4印刷用チラシ（スタンドアロン・**単一ソース非連動＝手動更新**）
    ├─ img/                      ホーム/各ページ用の画像・図
    │   ├─ session-build.png       事業デザイン対抗戦の制作画面（ヒーロー/セッション）
    │   ├─ session-result.png      AI戦略対抗戦の合議結果画面（セッション/テーマ）
    │   ├─ community-circle.png    参加者コミュニティ(Circle)。※日付写込みあり＝GitHub Pages専用
    │   ├─ history/vol-0N.svg       開催履歴の図。各回ダイジェスト（A日程）の図1を切り出したもの
    │   └─ pricing-flow.svg / pricing-tiers.svg  料金図の**元SVG。現在どこからも参照されていない**
    │                              （join の図は .md に inline 埋め込み済。修正は join/index.md 側）
    └─ antecanis_*.png / profile_*.jpg   元画像（配信からは exclude_docs で除外）

overrides/
├─ main.html                    全ページ共通のお知らせバーCTA（announceブロック）＋
                                構造化データ JSON-LD（extrahead ブロック。Organization／Event／BreadcrumbList）
├─ home.html                    ホーム（縦長ランディング）の専用テンプレート
└─ partials/header.html         Material の header partial を上書き。ヘッダーのタイトル文字を
                                site_name ではなく**ページ自身のタイトル**（トップは「ホーム」）に
                                する。ロゴのワードマークと重複させないため
main.py                         mkdocs-macros のマクロ定義（単一ソースを各ページへ流し込む）
mkdocs.yml                      設定・ナビ(nav)・配色・copyright・**extra:（単一ソースデータ）**
hooks/abbr_cjk.py               日本語の用語ツールチップを成立させる（変更不要）
hooks/seo_files.py              AIO 用 `llms.txt` をビルド時に生成（extra: と各ページの description から）
hooks/export_data.py            5つの役割。①`site/data/rounds.json`（回の表題・領域・開催日・
                                要約）を公開 ― B が回ページの見出しに使う。②`site/data/
                                glossary.json`（用語集）を公開 ― B の `/terms/` が読む。
                                **正本は本サイトの `docs/glossary.md` のまま**。
                                ③`site/data/areas.json`（5×5×5 の 15 領域）を公開 ― B の
                                領域マップが読む。**正本は `docs/about/philosophy.md` の表**。
                                ④sitemap からダイジェストを外す。⑤ダイジェストの本文を
                                `.build/digests.json`（`site/` の外＝**公開されない置き場**）へ
                                書き出す ― 会員限定の場所へ運ぶ材料。
                                あわせて `extra:` に真偽値として読まれたキーが無いか検査する
requirements.txt                material[imaging] / macros / glightbox / redirects
```

> 📄 **join の統合（2026年8月）**: 旧 `join/register.md`（登録方法）は `join/index.md` に統合。
> 「参加費 → 課金と解約のしくみ → お申し込み → 法人 → 規約」の1ページで完結させ、広告・紹介の
> 着地先を1つのURLに揃えた。旧URL `/join/register/` は `redirects` プラグインで `/join/` へ転送
> （`mkdocs.yml` の `plugins.redirects.redirect_maps`）。**この転送設定は消さないこと**（メール等で
> 配布済みのリンクが切れる）。参加者コミュニティ（Circle）の説明は `sessions/index.md` に集約。

ナビ（タブ）: ホーム / プロジェクトについて / セッション（開催履歴を含む） / スタートガイド / 参加する
（ダイジェスト・用語集は nav から外した。ページは残っており、URLを知っていれば開ける）

> 🎯 **このサイトの目的は「広告で来た人を申込へ運ぶこと」。ナビに項目を足さない。**
>
> グローバルナビの項目は、それ自体が申込導線から目を逸らす。**情報を足すのではなく、
> 申込の判断に要らないものを削る**のがこのサイトの方向。ナビは今後も増やさず、減らす。
>
> ⚠ 2026年9月に「読む」（ライブラリー＝B へのタブ）を足して**すぐ撤去した**。
> B は「参加後の世界が充実していることの証左」であって、申込前に読み込ませる場所ではない。
> **B への導線は本文とフッタに置く**（`docs/about/index.md` の節）。タブにはしない。

---

## 毎回の更新チェックリスト（新しい回の開催ごと）

> ✅ **次回開催・参加費は `mkdocs.yml` の `extra:` を1か所更新すれば、ホーム/schedule/join に
> 自動反映**されます（以前のような index.md と schedule.md の二重編集は不要になりました）。

0. **⚠ 日付の曜日を必ず検証する**（過去に「7/10(木)」と誤記した実例あり）
   ```bash
   for d in 2026-09-15 2026-10-02; do printf "%s = " "$d"; date -d "$d" "+%a"; done
   ```
   ユーザー提供の資料でも曜日が誤っていることがある。**曜日はコマンドの結果を正とする**。
1. **次回開催・参加費（単一ソース）** `mkdocs.yml` の `extra:`
   - `extra.next_session_short`（ヘッダー/お知らせバー/導線の短縮表記）＝**直近に開催される1件**
   - `extra.sessions`（次回回の配列：`label` / `kind`(main|sub) / `date` / `note`）＝**通常2件**。
     終わった回を落とし、「次に来る2つ」を並べる（例：第4回B日程が終わったら
     「第5回 A日程(9/15)」＋「第5回 B日程(10/2)」）。`kind: main`=A日程（金タグ）、`sub`=B日程
   - `extra.pricing`（早期枠・定価の金額）… 後述「料金改定の運用」を参照
   - 各回の `start`（ISO 日時。例 `2026-09-15T20:00:00+09:00`）… 構造化データ Event の開催日時。
     `date` と食い違わないように同時に更新する
   - これだけで、ホームのライブパネル・お知らせバー・schedule の「次回開催」カード・join の
     価格表・JSON-LD・`llms.txt` が更新される。
   - **終わった回は `extra.history` の先頭に追加**（`round:`＝回番号・テーマ・領域・開催日・
     要約・図・ダイジェスト）。図は A日程ダイジェストの図1を
     `assets/img/history/vol-0N.svg` に切り出す。
     `extra.latest_digest` を新しいダイジェストに向ける（ホームの「新着」）。
     - ⚠ 回番号のキーは **`round:`**。`no:` は **YAML が真偽値として読む**ため使えない
       （2026年9月に実際に踏み、開催履歴が「第回」と表示されていた）。`hooks/export_data.py`
       が同種のキーを検出してビルドを止める。
2. **開催スケジュールの月次表** `docs/sessions/schedule.md`
   - 表は **A日程（メイン）/ B日程（追加開催・同内容）の2列構成**。終了した日程に「※開催済」を付ける
   - 「次回開催」カードは `{{ session_cards() }}` マクロ（手編集不要）。
   - 「これまでの回を振り返る」のダイジェストリンクを更新
   - ※ホームの「次回開催」は overrides/home.html が `extra.sessions` を直接描画（手編集不要）。
3. **月次テーマ** `docs/sessions/themes.md`
   - 開催した回を「開催済みのテーマ」に**先頭（最新順）**で追記（ダイジェストへのリンクも）
   - 「今後のテーマ領域」から消化済みを調整
4. **ダイジェスト**（新しい回の分） … 下記「ダイジェストの追加手順」
   ※**nav・一覧・本文リンクには載せない。** front-matter に `search: exclude: true` を
   付け、`extra.history` の `digests:` に対応表を足す。URLは案内メール・Circle から使う。
5. **紹介チラシ** `docs/assets/flyer.html`
   - **単一ソースと連動しないので手動更新**。更新箇所は「次回開催枠の2日程」「今後の開催予定の
     月次リスト（過去日を除去）」「テーマ欄（実施済表記）」「参加費欄の金額・対象」
   - 新版HTMLを提供された場合は**丸ごと差し替え**（print CSSを保ったスタンドアロンHTMLのまま）
6. **用語集 ＋ ツールチップ**（新しい用語が出た回） … 下記「用語の追加手順」
7. **日付スタンプ**の確認
   - `docs/glossary.md` 末尾「◯年◯月時点」
   - `docs/start-guide.md` 末尾「◯年◯月時点」
8. **ビルド確認 → コミット → プッシュ → mainにマージ → デプロイ確認**（下記「ビルドと公開」）

---

## 同期が必要な箇所（漏れやすい！）

| 情報 | 載っているファイル |
|---|---|
| 次回開催の日程 | **`mkdocs.yml` の `extra.sessions` / `extra.next_session_short`**（ホーム・schedule・お知らせバー・JSON-LD・llms.txt へ自動反映。`date` と `start` の両方）＋ **`docs/sessions/schedule.md` の月次表**（※開催済の付与）＋ **`docs/assets/flyer.html`**（手動） |
| 終わった回の記録 | **`mkdocs.yml` の `extra.history`**（開催履歴ページ・`rounds.json`・B の回ページの見出しへ自動反映）＋ `extra.latest_digest`（ホームの新着）＋ `docs/sessions/themes.md` の該当回 |
| 参加費の金額 | **`mkdocs.yml` の `extra.pricing`**（ホームのティーザー・join の価格表へ自動反映）＋ **`join/index.md` の inline SVG 2点**（図1の金額・日付、図2の「いまここ」＝手動）＋ **`flyer.html` の参加費欄**（手動） |
| 用語の定義 | `docs/glossary.md` と `docs/includes/abbreviations.md` の**両方**（定義文を一致させる）。**正本はこの2つだけ**。ライブラリー（B）の `/terms/` は `site/data/glossary.json` をビルド時に取りに来るので、B 側に書き足す必要はない（書き足すと片方だけ古くなる）。掲載場所は B だが、**編集する場所はここ** |
| 5×5×5 の 15 領域 | **`docs/about/philosophy.md` の表だけ**（B の領域マップは `site/data/areas.json` を取りに来る）。⚠ 表の書式（`**[1A]** 名前 ── 説明` を `<br>` 区切り／層と切り口の2列）を変えると読み取りが減る。15個そろわなければ `hooks/export_data.py` がビルドを止める |
| 登録フォームURL | **`mkdocs.yml` の `extra.register_url` の1か所のみ**（通常は固定: `https://mailchi.mp/antecanis/ai-strategy`） |
| 申込（Stripe）URL | **`mkdocs.yml` の `extra.join_url` の1か所のみ**（固定リンク: `https://go.antecanis.com/ai-strategy-join`。リンク先の差し替えはStripe側で行う） |

---

## ダイジェストの追加手順（例：第5回A日程 → vol-05.md）

**命名**: A日程＝`vol-0N.md`（表記 Vol.NA）／B日程＝`vol-0Nb.md`（表記 Vol.NB）。
各回は2日程あるので、**同じ回でもダイジェストは2本**になる（B日程はA日程の内容＋その回の改良点）。

1. 新しいダイジェストを `docs/digests/vol-05.md` として作成
   - 既存の vol-04.md と同じ体裁。ユーザーから提供される軽量版mdは、**そのままでは体裁が違う**ので
     以下を必ず変換する（過去回はすべてこの形に統一済み）:
     - front-matter に `description:` を追加
     - 生の `<svg>` ＋ `*図N：…*`（斜体キャプション）→ **`<figure markdown="span">` ＋
       `<figcaption>`** でラップ
     - SVG内の `font-family="sans-serif"` → `'Noto Sans JP', sans-serif`、
       `"serif"` → `'Noto Serif JP', serif`（CJK描画をサイトと揃えるため）
     - 参加人数などの箇条書き → `<ul class="dg-meta">` に変換
     - 末尾の販促文・「詳細版はこちら」等は入れない（`{{ footer_cta(...) }}` が導線を担う）
   - **A↔B の相互リンク**：`!!! info` ボックスで相手日程へリンクし、`footer_cta` の第1引数にも
     相手日程を入れる。B日程側には「この回で何を改良したか」を明記する
2. `docs/digests/index.md` にカードを追加 ―― **最新順（先頭）**
3. `mkdocs.yml` の `nav:` → セッション → ダイジェスト に **最新順（先頭）** で追加
   `- Vol.5A 第5回（A日程・9/15）：（テーマ名）: digests/vol-05.md`
   - **並び順は時系列の降順**（例：4B → 4A → 3B → 3A → …）。同じ回ならB日程が先（日付が新しいため）
4. **導線の更新**：`mkdocs.yml` の `extra.latest_digest`（ホームの「新着」リンク）と
   `extra.history`（開催履歴）、`docs/sessions/schedule.md` の「これまでの回を振り返る」、
   `docs/sessions/themes.md` の該当回

> 🔒 **ダイジェストは「載せないが、URLを知っていれば開ける」**（2026年9月〜）。
> 登録前の人に過去回の詳細を大量に見せないため、辿り着く経路は塞ぐ。一方でページ自体は
> 前のURLのまま残す ―― 案内メールで配ったリンクと、Circle の詳細版記事からの
> 「簡易版はこちら」が生きているため。塞いでいるのは5か所:
> **nav** / **本文リンク**（月次テーマ・開催スケジュール・開催履歴カード・ホームの新着）/
> **noindex**（`overrides/main.html`）/ **sitemap・llms.txt**（hooks）/
> **サイト内検索**（各 .md の `search: exclude: true`）。
>
> ⚠ これは**アクセス制御ではない**。URLを知っていれば誰でも読める。本当に閉じるには
> 認証が要る（B に作る会員限定の場所）。
> ⚠ `robots.txt` で `Disallow: /digests/` に**しないこと**。クロールを止めると noindex が
> 読まれず、すでに索引された分が消えない。
>
> 公開サイトで案内するのは開催履歴のカード（テーマ・領域・開催日・2〜3行の要約・図1点）まで。
> 叙述と図は、今後 B に作る**会員限定の場所**（メール認証を通した先。過去の文脈から
> シナリオやケースを組み立てる機能を置く）で使う。材料は `.build/digests.json`。
>
> 💡 **詳細版ダイジェストは公開しない**。**セッション文脈パック**（登壇者の発言録＝主催者自身の
> 講義発言のみを収録）の原本はデータリポジトリ `ai-strategy-news-data` の `context/packs/` にあり、
> 公開はニュースサイト（B）の文脈ライブラリー経由で行う。**本サイトには転載しない**。
> 提供された場合は、**一般化できる用語・概念だけ**を用語集へ反映する（社内議論・特定回の運用
> 詳細は載せない）。

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

> 📖 **用語集の掲載場所はライブラリー（B）の `/terms/` に移った**（2026年9月）。
> ただし**正本は本サイトの上の2ファイルのまま**で、B は `site/data/glossary.json` を
> ビルド時に取りに来るだけ。**用語を増やす手順は何も変わらない。**
>
> 本サイトの `/glossary/` は、ダイジェストと同じ「載せないが、URLを知っていれば開ける」
> 扱いにした（nav・サイト内検索・sitemap・`llms.txt` から外し、noindex）。転送にしないのは、
> 旧URLを踏んだ人が**動く用語集に着地するほう**がよいため。検索では noindex により
> B に一本化される。
>
> ⚠ `docs/glossary.md` を**消さないこと**。消すと B の用語集が止まる（`glossary.json` の
> 生成元がこのファイル）。

---

## 単一ソース運用とホームの仕組み（重要）

- **変動情報の正本は `mkdocs.yml` の `extra:`**。`sessions` / `next_session_short` / `pricing` /
  `register_url` をここで定義し、**本文（.md）にハードコードしない**。
- **マクロ（`main.py`）**:
  - `{{ session_cards() }}` … `extra.sessions` から「次回開催」カードを描画（schedule で使用）
  - `{{ history_cards() }}` … `extra.history` から開催履歴カードを描画（sessions/history で使用）
  - `{{ register_button("ラベル") }}` … メール登録ボタン（**金**・`.md-button--gold`）
  - `{{ join_button("ラベル") }}` … 申込（Stripe）ボタン（**ティール**・`.md-button--primary`）。
    **join ページでのみ使う**
  - `{{ footer_cta("リンク1", …, join_cta=False) }}` … 全ページ末尾の共通動線。2つの入口を
    ボタン2つで並べる（ティール＝「参加費とお申し込みを見る →」／金＝メール登録）。join への
    リンクはページ深さから相対パスを自動計算。join ページ自身は申込ボタンが本文中にあるため
    `join_cta=False` でメール登録のみ表示
  - マクロは**全 .md ページが Jinja2 で処理される**ことを意味する。本文に素の `{{ ` `{%` `{#` を
    書かない（特に attr_list の `{#id}` は Jinja コメントと衝突する。見出しIDは付けず、
    CJK見出しは `toc.slugify`(Unicode保持) が生成するアンカーを使う）。
- **ホーム**は `overrides/home.html`（`base→main→home` の継承）。`docs/index.md` は front-matter
  （`template: home.html` と `hide: [navigation, toc]`、`description`）のみ。セクションのコピーは
  テンプレート内、スタイルは `extra.css` の `.home-landing` 配下。
- **お知らせバーCTA**は `overrides/main.html` の `announce` ブロックで全ページに表示。
- **構造化データ（JSON-LD）**も `overrides/main.html` の `extrahead` ブロックで生成。
  Organization は全ページ、Event は `extra.sessions` の `start` がある回をホーム・schedule・join に、
  BreadcrumbList はホーム以外。手編集しない（`extra:` を直せば追随する）。
- **`llms.txt`** は `hooks/seo_files.py` がビルド時に `site/llms.txt` へ生成。`extra:` と各ページの
  `description` が材料なので、新しいページには必ず `description` を付ける。
- ホームからの深いリンクは、CJK 見出しの自動スラッグに依存させず、本文側に `<a id="…"></a>` を
  置いてそこへ張る（例：`sessions/index.md` の `monthly-challenge`）。
- **OGP/ソーシャルカード**（`social` プラグイン）はフォント取得にネットワークが要るため、
  **ローカルでは無効（既定）／CI でのみ有効**（`.github/workflows/ci.yml` が `CARDS=true` と
  画像ライブラリ導入を行う）。ローカルで試すには `CARDS=true mkdocs build`（要ネット接続）。

---

## A/B日程の運用（2026年7月〜）

- 各回に **A日程（火曜・メイン）** と **B日程（追加開催・同内容）** の2日程がある。B日程はA日程の
  内容をベースに改良を加えることが多い（その差分はダイジェストに書く）。
- `extra.sessions` には「次に来る2つ」を並べる。回をまたぐこともある
  （例：第4回B(9/3)が終わったら「第5回A(9/15)」＋「第5回B(10/2)」）。
- `extra.next_session_short` は**直近の1件**。A/Bどちらであっても、単純に日付が近い方。
- 月次表（schedule.md）は A日程／B日程 の2列。過去分に `※開催済` を付ける。

## 挑戦セット・挑戦ボード（2026年8月〜、恒久提供）

セッション後も取り組みが続く仕組みで、**プロジェクトの常設要素**として掲載している（特定回の
話ではない）。正本は `docs/sessions/index.md` の「セッションの外へ ── 毎月の挑戦」節。

- **挑戦セット**：戦略レーン（コード不要）／実践レーン（手順書つき）の2レーン × 3段階〈守・破・離〉
- **挑戦ボード**：Circle上に記録を持ち寄り、次回冒頭で紹介する
- **参加者の発表枠**（第4回〜・先着）
- ホームの「続く場（Circle）」節と `start-guide.md` からも言及している。回ごとの更新は不要。

## 料金改定の運用

- 金額の正本は `extra.pricing`。**値に「円」を含めない**（テンプレート側で「円」を付けるため、
  含めると「6,930円円」になる。過去に実際に発生）。
- **既存契約者は申込時の月額のまま据え置き**が原則。改定は「これから申し込む人」にのみ適用。
- 改定時に手動更新が要るのは：`join/index.md` の**図1**（金額・次回コホートの日付・初回課金日・
  解約期限の例）、**図2**（「いまここ」の位置と金額）、`flyer.html` の参加費欄。
- **⚠ 編集方針：割引が「いつ終わったか」は書かない。** 直後に訪れた人が「損した」と感じるため、
  具体的な旧価格・改定日・「受付終了」といった表現は載せない。「先に申し込んだ方は据え置き」
  「後から申し込む方ほど割引幅は小さくなる」という一般的な説明に留める。

## 文言の方針（サイト全体）

- **「受講」を使わない**（受け身の学びのニュアンスを避ける）。「参加」「参加準備」と書く。
  ※ダイジェスト内の「講座の受講者」は、1990年代の“受け身の学習者”との対比という主旨なので例外。
- **「コホート」はユーザー向けの文言に出さない**（裏側の運用概念）。
- **具体的なAIモデル名・バージョンは書かない**（陳腐化が速い）。「軽量モデル」等の概念表記にする。
  用語集も「モデル（世代／グレード）」という概念エントリで扱っている。
- 入口の2本立て（無料メール登録／Stripe申込）の言い回しは全ページで統一する。

## 既知の落とし穴

| 症状 | 原因と対処 |
|---|---|
| 税込金額が「6,930**円円**」になる | `extra.pricing` の値に「円」を含めている。値は数字のみ（テンプレートが「円」を付ける） |
| 開催履歴が「第**回**」と番号抜けで出る | `extra:` のキーに `no:` `yes:` `on:` `off:` を使うと YAML が真偽値として読み、`r.get("no")` が静かに `None` を返す。**エラーにならず表示だけ欠ける**。キーは `round:` のように別の語にする（`hooks/export_data.py` が検出してビルドを止める） |
| ダイジェストや料金図のSVGが極端に小さい | Material の `figure{width:fit-content}` が、`viewBox` だけで幅指定のないinline SVGを潰す。`extra.css` の `.md-typeset figure{width:100%}` で対処済み（消さないこと） |
| 用語集の見出しを文字列grepしても一致しない | 見出し内の用語が `<abbr>` で囲まれ文字列が分断されるため。検証は用語単体か `<abbr title=...>` で行う。**サイト名「AI戦略ライブラリー」も同じ理由で grep に引っかからないことがある** |
| サイト名「AI戦略ライブラリー」の途中にツールチップが出る | `abbreviations.md` に「ライブラリ」があると名前の中に一致する（「セル」＝「キャンセル」と同じ）。2026年9月にツールチップから外した（用語集には残している） |
| ローカルで `mkdocs: command not found` | コンテナ再起動で依存が消えている。`pip install -q -r requirements.txt` で復旧（`python3 -m mkdocs` で実行） |
| `git push origin main` が rejected | 別セッションの変更が先に入っている。**force push は禁止**。`git fetch` → 差分確認 → `git merge` で統合してから push（過去に実際に発生し、マージで解決） |
| ビルド時の「MkDocs may break…」警告 | `redirects` プラグインが出す将来予告。ビルドは正常（無視してよい） |

---

## ビルドと公開

```bash
pip install -q -r requirements.txt     # 依存導入（コンテナ再起動後は毎回必要になることがある）
python3 -m mkdocs serve                # ローカルプレビュー（http://127.0.0.1:8000）
python3 -m mkdocs build --strict       # リンク切れ等を含め検証（公開前に必ず通す）
```

- 作業用ブランチで編集 → コミット → プッシュ → **`main` にマージ**すると、GitHub Actions
  （`.github/workflows/ci.yml`）が **`mkdocs build --strict` で検証してから** `mkdocs gh-deploy` で
  自動デプロイします（リンク切れがあるとデプロイ前に止まる）。
- デプロイは「新しい版を作ってから切り替える」ので**ダウンタイムは生じない**。本番が変わるのは
  `main` へのマージ時だけ。
- **デプロイ確認**：Actions のジョブは apt インストールに数分かかることがある（過去に5分超の例）。
  確実なのは **`gh-pages` ブランチの最新コミットメッセージ**を見ること。
  `Deployed <push した main の短縮SHA> with MkDocs version: …` になっていれば反映完了。
  ※CIのジョブAPIはキャッシュで「実行中」のまま見えることがあるので、gh-pages を正とする。
- **反映の遅延**: GitHub Pages がHTMLに `Cache-Control: max-age=600` を付与するため、
  既訪ブラウザは最大10分古い版を表示することがあります（変更不可・新規訪問者は即時最新）。
  自分で即確認したいときは URL に `?v=任意の数字` を付けるか、DevToolsの「キャッシュ無効化」。

---

## デザイン・規約（変更時の注意）

- **配色**: コーポレートティール `#004455` ＋ ゴールド `#C0962F`。見出しは Noto Serif JP。
  ファビコン（`docs/assets/favicon.png`）も `#004455`。**ライブラリー（B）と同一ファイル**
  ―― 同じ主体のサイトが別々の印として並ぶのは読み手の得にならない。片方だけ変えないこと。
  ※2026年9月まで `#008080`（CSS の teal）でブランド色とずれていた。
  ブランドトークンは `extra.css` 冒頭の `:root`（`--teal/--teal2/--teal-deep/--gold/--gold-pale/
  --gold-soft/--pale/--line/--ink/--muted/--paper`）に集約。料金図SVG・ホームもこれに一致。
  変更は `docs/stylesheets/extra.css` と `mkdocs.yml`（palette: custom）。
  金（gold）は **ボタン＋意味的アクセント1点（ライブパネルの本編タグ）** に限定（キャッチコピーの
  強調には使わない＝色の濃淡＋細い下線で表現。home-draft 準拠）。
- **フッタの規約リンク**（プライバシー/キャンセル/利用規約/特商法/お問い合わせ）は
  `mkdocs.yml` の `copyright:` にHTMLで記載。URLは `https://www.antecanis.com/...`。
- **決済（Stripe）リンクは `docs/join/index.md` の「お申し込み」節にのみ掲載**（URLは
  `extra.join_url` が単一ソース）。他ページから直リンクは張らず、ホーム等は join ページへ
  誘導する（課金条件を一度目に入れてもらうため）。入口は「情報を受け取りたい人＝無料メール登録」
  「参加を決めた人＝Stripe申込」の2本立てで、文言もこの2択で統一する。
- **ボタンの色は役割で固定する**：**金＝案内メールの無料登録**、**ティール（塗り）＝申込
  （Stripe）または申込ページへの遷移**、**アウトライン＝回遊**。ホーム（`.btn-gold` /
  `.btn-teal` / `.btn-outline`）と本文ページ（`.md-button--gold` / `.md-button--primary` /
  `.md-button`）で同じ意味になるよう対応させている。2つの入口を並べるときは
  `<div class="cta-pair" markdown>` で囲む。**同じ見た目のボタンに別の行き先を割り当てない。**
- **「コホート」はユーザー向けの文言に出さない**（回ごとの参加者管理は裏側の運用概念）。
- **大きい元画像**は `mkdocs.yml` の `exclude_docs` で配信から除外（リポジトリにはソースとして保持）。
- `hooks/abbr_cjk.py` は日本語ツールチップの要。**触らない**。
- チラシ(`flyer.html`)とダイジェストの元デザインHTMLはテーマCSSと独立。チラシは
  スタンドアロン（印刷用）のまま、ダイジェストは図のみ流用してテーマ内に再構成する。

---

## やらないこと

- 会員限定情報（Zoomリンク・当日資料・録画URL）は**サイトに載せない**。
  ※申込（Stripe）リンクは2026年8月に方針変更し、join ページにのみ掲載する。
- PRの作成は依頼があったときのみ。

---

## SEO / AIO の現状（2026年9月時点・次の検討テーマ）

目的は「プロジェクトに関心を持ち**登録・申込してくれる人を増やす**」こと。着手前の棚卸し。

**すでにできていること**

- 独自ドメイン `https://ai-strategy.antecanis.com/` ＋ `site_url` による **canonical** 出力
- **全 .md ページに `description` front-matter** を設定済み（OGP description にも使われる）
- **sitemap.xml** を自動生成（MkDocs標準）
- **OGP / Twitter カード**：`social` プラグインで自動生成（**CIでのみ生成**。ローカルは既定オフ）
- 日本語検索（`search.lang: ja`）、意味の通るURL構造（`/join/`, `/sessions/schedule/` 等）
- 旧URL `/join/register/` → `/join/` のリダイレクト（`redirects` プラグイン。GitHub Pages は
  HTTP 301 を出せないので、実体は meta refresh ＋ canonical の HTML ページ）
- 用語集＋全ページ自動付与のツールチップ（用語の網羅性そのものは資産になり得る）
- `robots.txt`（全許可＋AIクローラ明示＋sitemap の場所）… `docs/robots.txt`
- 構造化データ JSON-LD（Organization／Event／BreadcrumbList）… `overrides/main.html`
- `llms.txt`（AIO）… `hooks/seo_files.py` がビルド時に生成
- 開催履歴ページ（`sessions/history/`）… 実績を1ページで示す。ダイジェスト8本は将来ニュースサイト
  （B）の回ページへ移し、本サイトはここに集約する予定
- CI の `mkdocs build --strict`（リンク切れで止まる）

**未着手・検討候補**

- **キーワード設計・内部リンク設計が未検討**（現状は運用の都合で自然発生した構造）
- `extra.news_site_url` … 設定済み（`llms.txt` の「関連サイト」に出る）。
  ⚠ **nav の「読む」タブとホームの「公開ライブラリー」節は、一度入れて撤去した**
  （上記「ナビに項目を足さない」）。B への導線は `about/index.md` の節とフッタのみ
- ~~用語集の B への移設~~ … 2026年9月に完了（B の `/terms/` を検索に開き、本サイトの
  `/glossary/` を nav・検索・sitemap・llms.txt から外して noindex）。ダイジェストの B への
  移設は、会員限定の場所ができてから
- 計測は GA4（`extra.analytics` に設定済み）のみ。Search Console 連携状況は未確認

> ⚠ SEO/AIO の施策を入れるときも、本ファイルの既存方針（単一ソース原則・ボタンの役割固定・
> 文言の方針・会員限定情報を載せない）を崩さないこと。
