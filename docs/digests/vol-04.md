---
description: 第4回（A日程・8/18）ダイジェスト：物理世界に接地したAIは、競争のルールをどう書き換えるか ──Sense→Think→Act。
---

# 第4回（A日程・8/18）ダイジェスト：物理世界に接地したAIは、競争のルールをどう書き換えるか

> **Sense（認識）→ Think（思考）→ Act（行動）―― ロボットの世界の話が、あらゆる業種の事業戦略の話になる。**

第4回（2026年8月18日開催・A日程）のダイジェストです。第1回は世界のニュース情報、第2回は戦略
事業案、第3回は組織の集合知 ―― いずれも「テキストになっている情報」をAIが扱う話でした。第4回は、
より直接的に **物理世界** を扱います。写真・地理データをAIが認識し、判断し、提案する。それを体験した
うえで、「簡単に作れる」時代の競争優位はどこに宿るのかを、架空企業のストーリーを題材に考えました。

<ul class="dg-meta">
<li><b>約2時間半</b> ハンズオン中心</li>
<li>テーマ <b>[1E]</b> 物理世界との接地と作用</li>
</ul>

!!! info "第4回には追加開催（B日程・9/3）があります"
    第4回は、**A日程（8/18）** と、同内容の **B日程（追加開催・9/3）** の2日程で実施します。
    こちらは **A日程（8/18）** のダイジェストです。B日程（9/3）のダイジェストは、開催後に掲載します。

## 本日の起点 — 「専用の認識」から「汎用の理解」へ

画像認識も音声認識も、昔からありました。けれど決定的に違うのは、**認識と思考が一続きになった**
ことです。

<figure markdown="span">
<svg viewBox="0 0 680 290" xmlns="http://www.w3.org/2000/svg" role="img">
  <g font-family="'Noto Sans JP', sans-serif">
  <text x="20" y="22" font-size="11" fill="#8a979a" font-weight="700">LLM以前（〜2022）　タスクごとの「専用AI」</text>
  <text x="392" y="22" font-size="11" fill="#004455" font-weight="700">LLM以後（2022〜）　理解・推論する「汎用モデル」</text>
  <rect x="20" y="34" width="330" height="46" rx="8" fill="#fff" stroke="rgba(0,68,85,.16)"/>
  <text x="36" y="54" font-size="12" fill="#5d6b6e" font-weight="600">従来の言語処理（NLP）</text>
  <text x="36" y="71" font-size="10.5" fill="#8a979a">抽出・分類まで。1タスク1モデル</text>
  <rect x="20" y="88" width="330" height="46" rx="8" fill="#fff" stroke="rgba(0,68,85,.16)"/>
  <text x="36" y="108" font-size="12" fill="#5d6b6e" font-weight="600">画像認識（CNN など）</text>
  <text x="36" y="125" font-size="10.5" fill="#8a979a">「これは猫」とラベルを付けるまで</text>
  <rect x="20" y="142" width="330" height="46" rx="8" fill="#fff" stroke="rgba(0,68,85,.16)"/>
  <text x="36" y="162" font-size="12" fill="#5d6b6e" font-weight="600">音声認識（ASR）</text>
  <text x="36" y="179" font-size="10.5" fill="#8a979a">文字起こしまで。内容は考えない</text>
  <rect x="20" y="196" width="330" height="46" rx="8" fill="#fff" stroke="rgba(0,68,85,.16)"/>
  <text x="36" y="216" font-size="12" fill="#5d6b6e" font-weight="600">従来の自動化・制御</text>
  <text x="36" y="233" font-size="10.5" fill="#8a979a">決められた動きの繰り返しだけ</text>
  <rect x="392" y="34" width="268" height="46" rx="8" fill="#f7f4ee" stroke="rgba(0,68,85,.2)"/>
  <text x="408" y="54" font-size="12" fill="#004455" font-weight="700">LLM ＝ 言語脳</text>
  <text x="408" y="71" font-size="10.5" fill="#5d6b6e">推論・知識・対話の土台</text>
  <rect x="392" y="88" width="268" height="46" rx="8" fill="#f7f4ee" stroke="rgba(0,68,85,.2)"/>
  <text x="408" y="108" font-size="12" fill="#004455" font-weight="700">VLM ＝ ＋目</text>
  <text x="408" y="125" font-size="10.5" fill="#5d6b6e">画像を見て、考えて、言葉で答える</text>
  <rect x="392" y="142" width="268" height="46" rx="8" fill="#f7f4ee" stroke="rgba(0,68,85,.2)"/>
  <text x="408" y="162" font-size="12" fill="#004455" font-weight="700">マルチモーダル ＝ ＋耳・口</text>
  <text x="408" y="179" font-size="10.5" fill="#5d6b6e">音声・動画も理解。生成もできる</text>
  <rect x="392" y="196" width="268" height="46" rx="8" fill="#004455"/>
  <text x="408" y="216" font-size="12" fill="#fff" font-weight="700">VLA ＝ ＋手足</text>
  <text x="408" y="233" font-size="10.5" fill="rgba(255,255,255,.78)">見て・考えて・動く。物理世界へ</text>
  <line x1="356" y1="138" x2="386" y2="138" stroke="#b88a3e" stroke-width="2"/>
  <polygon points="386,138 377,133 377,143" fill="#b88a3e"/>
  <text x="371" y="124" font-size="10" fill="#b88a3e" font-weight="700" text-anchor="middle">思考の獲得</text>
  <text x="340" y="266" font-size="11" fill="#5d6b6e" text-anchor="middle">縦（上→下）＝感覚の拡張：言語 → 目 → 耳 → 手足</text>
  <text x="340" y="282" font-size="11" fill="#004455" text-anchor="middle" font-weight="700">「これは猫だ」から、「この写真から、こんなことが考えられる」へ</text>
  </g>
</svg>
<figcaption>図1：AIの進化地図。今回扱うVLMは、画像を認識するだけでなく、見たうえで考えます。</figcaption>
</figure>

この変化を業務の形に落とすと、**Sense → Think → Act のループ** になります。ロボットや自動運転で
語られてきた枠組みですが、実はあらゆる業務が同じループでできています ―― 現場・顧客の情報を集め、
分析して意思決定し、実行する。これまで「人間だけ」の領域だった真ん中に、AIが入りました。

<figure markdown="span">
<svg viewBox="0 0 680 220" xmlns="http://www.w3.org/2000/svg" role="img">
  <g font-family="'Noto Sans JP', sans-serif">
  <circle cx="130" cy="90" r="58" fill="#f7f4ee" stroke="rgba(0,68,85,.2)"/>
  <text x="130" y="84" font-size="13" fill="#004455" font-weight="700" text-anchor="middle">SENSE</text>
  <text x="130" y="104" font-size="10.5" fill="#5d6b6e" text-anchor="middle">知覚する</text>
  <circle cx="340" cy="90" r="58" fill="#004455"/>
  <text x="340" y="84" font-size="13" fill="#fff" font-weight="700" text-anchor="middle">THINK</text>
  <text x="340" y="104" font-size="10.5" fill="rgba(255,255,255,.8)" text-anchor="middle">考える・判断する</text>
  <circle cx="550" cy="90" r="58" fill="#f7f4ee" stroke="rgba(0,68,85,.2)"/>
  <text x="550" y="84" font-size="13" fill="#004455" font-weight="700" text-anchor="middle">ACT</text>
  <text x="550" y="104" font-size="10.5" fill="#5d6b6e" text-anchor="middle">行動する</text>
  <line x1="190" y1="90" x2="278" y2="90" stroke="#b88a3e" stroke-width="2"/>
  <polygon points="278,90 269,85 269,95" fill="#b88a3e"/>
  <line x1="400" y1="90" x2="488" y2="90" stroke="#b88a3e" stroke-width="2"/>
  <polygon points="488,90 479,85 479,95" fill="#b88a3e"/>
  <path d="M550 150 Q340 205 130 150" fill="none" stroke="#d8b878" stroke-width="1.5" stroke-dasharray="5 4"/>
  <polygon points="130,150 140,155 137,145" fill="#d8b878"/>
  <text x="340" y="196" font-size="10.5" fill="#8a979a" text-anchor="middle">結果をふたたび知覚し、次の判断へ ―― ループが回り続ける</text>
  <text x="340" y="30" font-size="11.5" fill="#b88a3e" font-weight="700" text-anchor="middle">人の役割は「ループの中で作業する」から「ループを設計し、監督する」へ</text>
  </g>
</svg>
<figcaption>図2：Sense→Think→Act。物理AIだけでなく、あらゆる業務がこのループでできています。</figcaption>
</figure>

本プロジェクトの **5×5×5の枠組み** では、第4回は第1層に戻り **[1E] 物理世界との接地と作用** を
扱います（第1回＝[1A] 認知容量、第2回＝第3層 戦略転換、第3回＝第2層 組織変革）。回ごとにタイルを
埋めながら、AI戦略の全体像を形づくっていきます。

## 本日のストーリー — 架空企業「株式会社ソトイエ」

今回は、架空のアウトドア＆インテリア企業を舞台に考えました。長野発祥、「外で過ごす心地よさを、
家の中に」を掲げるライフスタイル企業。直営18店とEC、カタログ約860点、売上高180億円。抱える課題は
2つです。

**グランピングフィールドの土地探し** ―― 全国に中小型フィールドを数十棟という構想だが、条件に合う
土地は不動産市場に出てこない。航空写真を一枚一枚、目で追って探すしかなく、1件の一次調査に数週間。
目と根気が先に尽きる。

**「くらしまるごと提案」** ―― 成約率が高く客単価は通常の6倍。だが1件3時間、その大半は顧客の写真と
860点のカタログを突き合わせる照合作業。腕の良いコーディネーターほど予約が埋まり、貴重な感性の
時間が単調な作業に溶けていく。

若手が生成AIで試作を始め、2つのプロトタイプ ―― 「AIロケーションファインダー」と「AIライフ
スタイルデザイナー」―― が形になった。そして経営会議で意見が割れます。**外販すれば桁違いに大きな
業界に届く**（専務）。**同じものは競合もすぐ作れるし、大手は内製を選ぶ。「AIで作れるもの」の値段は
下がり続けている**（営業本部長）。**来年の新モデルが標準機能でやってしまったら、作った仕組みごと
陳腐化しないか**（入社3年目）。

<figure markdown="span">
<svg viewBox="0 0 680 250" xmlns="http://www.w3.org/2000/svg" role="img">
  <g font-family="'Noto Sans JP', sans-serif">
  <text x="20" y="24" font-size="12" fill="#b88a3e" font-weight="700">4つの問い ―― この企業だけの話ではありません</text>
  <rect x="20" y="38" width="316" height="88" rx="10" fill="#fff" stroke="rgba(0,68,85,.2)"/>
  <text x="40" y="62" font-size="13" fill="#004455" font-weight="700">作れるか</text>
  <text x="40" y="84" font-size="10.5" fill="#5d6b6e">誰が・どれくらいのコストで作れるように</text>
  <text x="40" y="100" font-size="10.5" fill="#5d6b6e">なったか。チャットAIをそのまま使うのと、</text>
  <text x="40" y="116" font-size="10.5" fill="#5d6b6e">業務が回る仕組みの段差はどこにあるか</text>
  <rect x="344" y="38" width="316" height="88" rx="10" fill="#fff" stroke="rgba(0,68,85,.2)"/>
  <text x="364" y="62" font-size="13" fill="#004455" font-weight="700">勝てるか</text>
  <text x="364" y="84" font-size="10.5" fill="#5d6b6e">同じものを作れるプレイヤーが次々に</text>
  <text x="364" y="100" font-size="10.5" fill="#5d6b6e">現れる中で、自社が勝てる理由は何か</text>
  <text x="364" y="116" font-size="10.5" fill="#8a979a">〔＝優位の源泉はどこに移ったか〕</text>
  <rect x="20" y="136" width="316" height="88" rx="10" fill="#fff" stroke="rgba(0,68,85,.2)"/>
  <text x="40" y="160" font-size="13" fill="#004455" font-weight="700">内製に勝るか</text>
  <text x="40" y="182" font-size="10.5" fill="#5d6b6e">想定顧客が「自分で作る」未来と比べて、</text>
  <text x="40" y="198" font-size="10.5" fill="#5d6b6e">それでも買ってもらえる理由は残るか</text>
  <text x="40" y="214" font-size="10.5" fill="#8a979a">〔＝売り手として何を担うのか〕</text>
  <rect x="344" y="136" width="316" height="88" rx="10" fill="#004455"/>
  <text x="364" y="160" font-size="13" fill="#fff" font-weight="700">続くか</text>
  <text x="364" y="182" font-size="10.5" fill="rgba(255,255,255,.8)">AIの進化の波を越えて、価値を持ち続ける</text>
  <text x="364" y="198" font-size="10.5" fill="rgba(255,255,255,.8)">源泉はどこにあるか</text>
  <text x="364" y="214" font-size="10.5" fill="#ffe9c2">〔＝一時的な優位と構造的な優位の境目〕</text>
  </g>
</svg>
<figcaption>図3：手を動かす前と後、同じ4つの問いに向き合いました。選択肢は「自社で使う」「外販する」から「作り込まず市販のチャットAIで済ませる」まで5つ。</figcaption>
</figure>

## 当日の流れ — 2つのプロトタイプを、自分の手で動かす

#### 01 — AIロケーションファインダー：AIが航空写真を読んで、探し続ける

Colabノートブックを各自のドライブにコピーして実行。国土地理院が無償公開する航空写真を使い、自分の
好きな地名（県庁所在地、あるいは緯度経度で任意の場所）を起点に、AIが5×5＝25枚の写真を読んで
「ここは良さそう」「ここは道路がなさそう」と判断しながら探索を進めます。実行ボタンを押すたびに
5ステップずつ自動で探し続け、赤枠で候補地を提示。

効いたのは **速さと安さ** でした。軽量モデルを使うことで1枚あたりごく短時間で読み進められ、何十回
繰り返しても苦になりません。候補が決まれば、その場所を題材にした提案文まで自動生成されます。一方で、
**最初の条件設定が厳しすぎると候補がなかなか出ない** ―― 「どこまで作り込めばこれは実務で役に立つ
のか」という現実も、同時に体感することになりました。

#### 02 — AIライフスタイルデザイナー：写真32枚と商品860点を、丸ごと読む

2つ目は、顧客から届いた **32枚の住まいの写真** と、**860点の自社カタログ** を突き合わせる体験です
（顧客は「片づけても散らかって見える、家族が自然と集まる部屋にしたい、予算80万円」という設定）。

AIは32枚すべてを一気に読み、それぞれに見立てを付け、「この家族が実は大切にしていること」まで
推し量ります。次に860点・約7万字（人が1点30秒で見ても7時間かかる分量）のカタログから商品を選び、
予算内で提案を組み立て、完成イメージの画像まで生成する。ここで見えたのが **コスト構造** でした ――
1回あたり約70円のうち、**画像生成が50円、大量の画像を読む側はわずか5円**。つまり「AIに大量の写真を
読ませる」ことは、ビジネスとして十分スケールする、ということです。

## 手を動かす前と、後で。

同じ問い（5つの選択肢のどれを、どの順で、どこまでやるか）を、ストーリーを読んだ直後と、2つの
プロトタイプを動かした後の2回、参加者に問いました。**手を動かす前と後で、視野が変わる** ―― その
変化自体が、この回の設計意図でした。

AIで簡単に作れるということは、他社にも簡単に作れるということ。半年前に独自価値だったものが、大手の
標準機能に飲み込まれる。それでも、**土地の目利きや暮らし提案のノウハウごと載せて届けられるなら、
選ばれる余地は残る** のではないか。答えのない問いに、手触りを持って向き合う時間になりました。

第4回B日程は 9/3（木）。第5回（9/15・10/2）は改めて戦略レイヤーへ ―― 「AIを皆が使える前提で、
企業戦略の質やセンスはどこで分かれるのか」を扱う構想です。

{{ footer_cta("[ダイジェスト一覧](index.md)", "[月次テーマ](../sessions/themes.md)", "[開催予定・次回案内](../sessions/schedule.md)") }}
