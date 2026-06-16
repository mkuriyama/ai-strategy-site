# 第1回ダイジェスト：人間の認知容量の解除

> **AIを「便利な道具」から「事業構想の前提」へ。**

第1回（パイロット・無償開催）では、参加者の皆さまご自身の手でAIを動かしながら、
「AI×戦略×実践」の最初の一歩 ―― 人間の認知容量の解除 ―― を体感していただきました。
当日参加できなかった方、途中から参加された方に、その全体の流れをお届けします。

<ul class="dg-meta">
<li><b>60</b> 名のご参加</li>
<li><b>2時間</b> ハンズオン中心</li>
<li>テーマ <b>[1A]</b> 認知容量の解除</li>
</ul>

## 本日の起点 — 始まりの物語

### 「AI活用講座」を受けた人が、世界を変えるわけではない。

1990年代、PCとインターネットが登場したとき、多くの人は「ExcelとWordの活用講座」
「ブラウザの活用講座」に熱心に通いました。けれど、その後の30年で世界を変えたのは、
講座の受講者ではなく、ネットを*前提に*事業そのものを構想した人たちでした。

いま生成AIで同じ構図が始まっています。「AIの便利活用講座」の延長線上に、世界を変える
事業はおそらく無い ―― この問題意識が、本プロジェクト全体の出発点です。

<div class="grid cards" markdown>

-   **これまで：AI as a tool**

    ---

    便利ツールとしての活用

-   **これから：AI as a strategy**

    ---

    AI前提の構想を描き・実現する

</div>

この転換を、理論の解説ではなく「手を動かして体感する」かたちで進めたのが第1回です。
本プロジェクトは、AIの戦略インパクトを3つの層で捉える **5×5×5の枠組み** を指針としています。

<figure markdown="span">
<svg viewBox="0 0 680 318" xmlns="http://www.w3.org/2000/svg" role="img">
        <defs>
          <style>
            .lyr{fill:#fff;stroke:var(--line);stroke:rgba(0,68,85,.18)}
            .ltag{font-family:'Noto Sans JP',sans-serif;font-size:11px;letter-spacing:.18em;fill:#8a979a;font-weight:700}
            .lname{font-family:'Noto Serif JP',serif;font-size:17px;fill:#004455;font-weight:600}
            .lscale{font-family:'Noto Sans JP',sans-serif;font-size:11px;fill:#5d6b6e}
            .chip{font-family:'Noto Sans JP',sans-serif;font-size:12px;fill:#0a5567;font-weight:500}
            .axis{font-family:'Noto Sans JP',sans-serif;font-size:11px;fill:#8a979a;letter-spacing:.1em}
          </style>
        </defs>
        <!-- scale axis -->
        <line x1="26" y1="40" x2="26" y2="270" stroke="#b88a3e" stroke-width="1.5"/>
        <polygon points="26,32 22,44 30,44" fill="#b88a3e"/>
        <text class="axis" x="20" y="155" transform="rotate(-90 20,155)" text-anchor="middle">戦略インパクト・スケール</text>

        <!-- L3 -->
        <rect class="lyr" x="56" y="36" width="600" height="68" rx="9"/>
        <text class="ltag" x="78" y="62">＜第3層＞ 戦略転換</text>
        <text class="lname" x="78" y="86">産業・事業スケールの変化</text>
        <rect x="430" y="50" width="208" height="40" rx="7" fill="#f7f4ee" stroke="rgba(0,68,85,.12)"/>
        <text class="chip" x="446" y="66">[3A] 顧客価値の</text>
        <text class="chip" x="446" y="82">　　　 シフト</text>

        <!-- L2 -->
        <rect class="lyr" x="56" y="118" width="600" height="68" rx="9"/>
        <text class="ltag" x="78" y="144">＜第2層＞ 組織変革</text>
        <text class="lname" x="78" y="168">事業組織スケールの変化</text>
        <rect x="430" y="132" width="208" height="40" rx="7" fill="#f7f4ee" stroke="rgba(0,68,85,.12)"/>
        <text class="chip" x="446" y="148">[2A] 情報流通の</text>
        <text class="chip" x="446" y="164">　　　 血流化</text>

        <!-- L1 highlighted -->
        <rect x="56" y="200" width="600" height="74" rx="9" fill="#004455"/>
        <text class="ltag" x="78" y="228" style="fill:rgba(255,255,255,.6)">＜第1層＞ 実装</text>
        <text class="lname" x="78" y="252" style="fill:#fff">現場・個人スケールの変化</text>
        <rect x="430" y="214" width="208" height="46" rx="7" fill="#b88a3e"/>
        <text class="chip" x="446" y="232" style="fill:#fff;font-weight:700">[1A] 人間の認知</text>
        <text class="chip" x="446" y="250" style="fill:#fff;font-weight:700">　　　 容量の解除</text>
        <text x="78" y="296" style="font-family:'Noto Sans JP',sans-serif;font-size:12px;fill:#b88a3e;font-weight:700">↑ 第1回は、ここを起点に。</text>
      </svg>
<figcaption>図1：AIの戦略インパクトを捉える3層構造。第1回は最下層の起点 [1A] を中心に扱いました。</figcaption>
</figure>

## 当日の流れ — 5つのハンズオン

### 対話する → 作らせる → 仕組みにする

「個人で便利使いする世界」から「事業戦略への組込みを構想・実装する世界」へ。参加者は
実際に手元のAI（ChatGPT / Gemini / Claude）を動かしながら、一段ずつステップを上がって
いきました。

<figure markdown="span">
<svg viewBox="0 0 680 178" xmlns="http://www.w3.org/2000/svg" role="img">
        <defs>
          <style>
            .node{fill:#f7f4ee;stroke:rgba(0,68,85,.18)}
            .nt{font-family:'Noto Serif JP',serif;font-size:15px;fill:#004455;font-weight:600;text-anchor:middle}
            .ns{font-family:'Noto Sans JP',sans-serif;font-size:11px;fill:#5d6b6e;text-anchor:middle}
            .band{font-family:'Noto Sans JP',sans-serif;font-size:11.5px;fill:#8a979a;text-anchor:middle;letter-spacing:.05em}
          </style>
        </defs>
        <!-- nodes -->
        <rect class="node" x="20" y="36" width="190" height="64" rx="10"/>
        <text class="nt" x="115" y="66">AIと対話する</text>
        <text class="ns" x="115" y="86">チャットで使う</text>

        <rect class="node" x="245" y="36" width="190" height="64" rx="10"/>
        <text class="nt" x="340" y="66">AIに作らせる</text>
        <text class="ns" x="340" y="86">コード・成果物を生成</text>

        <rect x="470" y="36" width="190" height="64" rx="10" fill="#004455"/>
        <text class="nt" x="565" y="66" style="fill:#fff">仕組みにする</text>
        <text class="ns" x="565" y="86" style="fill:rgba(255,255,255,.72)">API・自動化で動かす</text>

        <!-- arrows -->
        <line x1="212" y1="68" x2="243" y2="68" stroke="#b88a3e" stroke-width="2"/>
        <polygon points="243,68 234,63 234,73" fill="#b88a3e"/>
        <line x1="437" y1="68" x2="468" y2="68" stroke="#b88a3e" stroke-width="2"/>
        <polygon points="468,68 459,63 459,73" fill="#b88a3e"/>

        <!-- transition band -->
        <line x1="60" y1="134" x2="620" y2="134" stroke="#d8b878" stroke-width="1" stroke-dasharray="4 4"/>
        <text class="band" x="115" y="156">個人の便利使い</text>
        <polygon points="350,150 362,146 362,154" fill="#d8b878"/>
        <line x1="200" y1="150" x2="356" y2="150" stroke="#d8b878" stroke-width="1"/>
        <line x1="356" y1="150" x2="500" y2="150" stroke="#d8b878" stroke-width="1"/>
        <text class="band" x="565" y="156" style="fill:#004455;font-weight:700">事業戦略への組込み</text>
      </svg>
<figcaption>図2：3つのモードを上がるほど、「個人の便利使い」から「事業戦略への組込み」へと重心が移ります。</figcaption>
</figure>

#### 01 — 課題を言語化し、AIと比べる

「自分の業界・部門における"人間の認知容量の限界"とは何か」をまず自分の言葉で書き、
同じ問いをAIにも考えさせ、人間案とAI案を比較。"伝えられないものはAIも汲み取れない"
―― 言語化の重要性を体感する導入です。

#### 02 — 世界のニュース100件を、AIに使わせる

AIが取得した世界のビジネスニュース100件を題材に、「先読み」「人材育成」など目的を
1つ選び、自分の業界・部門設定を添えて実行。同じデータでも、目的の置き方で引き出せる
価値が変わることを確認しました。

<figure markdown="span">
<svg viewBox="0 0 680 168" xmlns="http://www.w3.org/2000/svg" role="img">
        <defs>
          <style>
            .pb{fill:#fff;stroke:rgba(0,68,85,.2)}
            .pt{font-family:'Noto Serif JP',serif;font-size:15px;fill:#004455;font-weight:600;text-anchor:middle}
            .ps{font-family:'Noto Sans JP',sans-serif;font-size:10.5px;fill:#5d6b6e;text-anchor:middle}
            .lab{font-family:'Noto Sans JP',sans-serif;font-size:11px;fill:#b88a3e;font-weight:700;text-anchor:middle}
          </style>
        </defs>
        <rect class="pb" x="24" y="30" width="180" height="58" rx="9"/>
        <text class="pt" x="114" y="56">取得</text>
        <text class="ps" x="114" y="76">input</text>

        <rect class="pb" x="250" y="30" width="180" height="58" rx="9"/>
        <text class="pt" x="340" y="56">活用</text>
        <text class="ps" x="340" y="76">output</text>

        <rect class="pb" x="476" y="30" width="180" height="58" rx="9"/>
        <text class="pt" x="566" y="56">蓄積</text>
        <text class="ps" x="566" y="76">store</text>

        <line x1="206" y1="59" x2="248" y2="59" stroke="#0a5567" stroke-width="2"/>
        <polygon points="248,59 239,54 239,64" fill="#0a5567"/>
        <line x1="432" y1="59" x2="474" y2="59" stroke="#0a5567" stroke-width="2"/>
        <polygon points="474,59 465,54 465,64" fill="#0a5567"/>

        <!-- AI build layer -->
        <rect x="24" y="108" width="632" height="44" rx="9" fill="#f7f4ee" stroke="rgba(184,138,62,.4)"/>
        <text class="lab" x="340" y="129">この「仕組み自体」をAIで作れるか？</text>
        <text x="340" y="145" style="font-family:'Noto Sans JP',sans-serif;font-size:10.5px;fill:#5d6b6e;text-anchor:middle">取得システムをAIコーディングで作る ／ 処理でAIをAPI経由で呼び出す</text>
      </svg>
<figcaption>図3：情報を「取得→活用→蓄積」する流れ。鍵は、その仕組み自体を自分の手でAIに作らせられるか。</figcaption>
</figure>

#### 03 — "ちょっとしたAIエンジニア"になってみる

生成AIに書かせたPythonコードを Google Colaboratory に貼り付け、APIキーを設定して実行。
「素人でもこれだけ簡単に作れて、動かせる」 ―― 競争優位の源泉そのものがシフトしている
感覚を、自分の手で確かめました。

#### 04 — 15部署のニュースマップを描く

大量の記事をAIに評価させ、「どの部署がどの記事を重視するか」を色分けした地図に可視化。
リスク管理・CFO・マーケ…と、立場ごとに見える景色が違うことが一枚で立ち上がります。
さらに、毎朝メールやSlackに自動配信する"仕組み化"までを提示しました。

<figure markdown="span">
<svg viewBox="0 0 680 200" xmlns="http://www.w3.org/2000/svg" role="img">
        <defs>
          <style>.cap{font-family:'Noto Sans JP',sans-serif;font-size:11px;fill:#5d6b6e}.dep{font-family:'Noto Sans JP',sans-serif;font-size:11px;fill:#004455;font-weight:500}</style>
        </defs>
        <!-- grid of colored cells -->
        <g>
          <!-- row generation: colors evoke department heatmap -->
          <!-- We hand-place a 9x4 grid -->
          <!-- palette: teal, gold, soft teal, muted -->
          <g>
            <!-- r1 --><rect x="40" y="24" width="30" height="30" rx="4" fill="#004455"/><rect x="74" y="24" width="30" height="30" rx="4" fill="#d8b878"/><rect x="108" y="24" width="30" height="30" rx="4" fill="#0a5567"/><rect x="142" y="24" width="30" height="30" rx="4" fill="#b88a3e"/><rect x="176" y="24" width="30" height="30" rx="4" fill="#004455"/><rect x="210" y="24" width="30" height="30" rx="4" fill="#9fb3b6"/><rect x="244" y="24" width="30" height="30" rx="4" fill="#d8b878"/><rect x="278" y="24" width="30" height="30" rx="4" fill="#0a5567"/><rect x="312" y="24" width="30" height="30" rx="4" fill="#b88a3e"/>
            <!-- r2 --><rect x="40" y="58" width="30" height="30" rx="4" fill="#9fb3b6"/><rect x="74" y="58" width="30" height="30" rx="4" fill="#004455"/><rect x="108" y="58" width="30" height="30" rx="4" fill="#b88a3e"/><rect x="142" y="58" width="30" height="30" rx="4" fill="#0a5567"/><rect x="176" y="58" width="30" height="30" rx="4" fill="#d8b878"/><rect x="210" y="58" width="30" height="30" rx="4" fill="#004455"/><rect x="244" y="58" width="30" height="30" rx="4" fill="#0a5567"/><rect x="278" y="58" width="30" height="30" rx="4" fill="#9fb3b6"/><rect x="312" y="58" width="30" height="30" rx="4" fill="#d8b878"/>
            <!-- r3 --><rect x="40" y="92" width="30" height="30" rx="4" fill="#d8b878"/><rect x="74" y="92" width="30" height="30" rx="4" fill="#0a5567"/><rect x="108" y="92" width="30" height="30" rx="4" fill="#004455"/><rect x="142" y="92" width="30" height="30" rx="4" fill="#9fb3b6"/><rect x="176" y="92" width="30" height="30" rx="4" fill="#b88a3e"/><rect x="210" y="92" width="30" height="30" rx="4" fill="#0a5567"/><rect x="244" y="92" width="30" height="30" rx="4" fill="#004455"/><rect x="278" y="92" width="30" height="30" rx="4" fill="#d8b878"/><rect x="312" y="92" width="30" height="30" rx="4" fill="#9fb3b6"/>
            <!-- r4 --><rect x="40" y="126" width="30" height="30" rx="4" fill="#0a5567"/><rect x="74" y="126" width="30" height="30" rx="4" fill="#b88a3e"/><rect x="108" y="126" width="30" height="30" rx="4" fill="#9fb3b6"/><rect x="142" y="126" width="30" height="30" rx="4" fill="#004455"/><rect x="176" y="126" width="30" height="30" rx="4" fill="#0a5567"/><rect x="210" y="126" width="30" height="30" rx="4" fill="#d8b878"/><rect x="244" y="126" width="30" height="30" rx="4" fill="#9fb3b6"/><rect x="278" y="126" width="30" height="30" rx="4" fill="#004455"/><rect x="312" y="126" width="30" height="30" rx="4" fill="#b88a3e"/>
          </g>
        </g>
        <!-- legend -->
        <text class="cap" x="40" y="182">記事 × 部署の重視度を色で可視化</text>
        <g>
          <rect x="396" y="30" width="14" height="14" rx="3" fill="#004455"/><text class="dep" x="418" y="42">リスク管理</text>
          <rect x="396" y="56" width="14" height="14" rx="3" fill="#b88a3e"/><text class="dep" x="418" y="68">CFO・財務</text>
          <rect x="396" y="82" width="14" height="14" rx="3" fill="#0a5567"/><text class="dep" x="418" y="94">マーケティング</text>
          <rect x="396" y="108" width="14" height="14" rx="3" fill="#d8b878"/><text class="dep" x="418" y="120">事業開発</text>
          <rect x="396" y="134" width="14" height="14" rx="3" fill="#9fb3b6"/><text class="dep" x="418" y="146">その他部署 …（計15部署）</text>
        </g>
      </svg>
<figcaption>図4：同じニュース群でも、部署＝立場ごとに「重視する記事」は異なる。それを一枚の地図にしたイメージ。</figcaption>
</figure>

#### 05 — そして、次への物語へ

最後に冒頭の「始まりの物語」へ戻り、今日扱った技術が経営戦略にどう紐づき、どうスケール
していくのかを各自のストーリーとして展開。技術体験を、戦略の文脈に着地させて締めくくりました。

## 技術の体験を、戦略の文脈へ。

第1回で扱ったのは、AIを自分の手で動かす"入口"です。ここで得た感覚を、皆さんご自身の
業界・事業の構想にどうつなげていくか ―― 本編は、そこから始まります。

{{ footer_cta("[ダイジェスト一覧](index.md)", "[月次テーマ](../sessions/themes.md)", "[開催予定・次回案内](../sessions/schedule.md)") }}
