/*
 * フォーム（/subscribe/ のメール登録・/join/corporate/ の法人問い合わせ）と、UTM の保持・計測。
 *
 * - 全ページで読み込まれる（mkdocs.yml の extra_javascript）。フォームの無いページでは
 *   UTM を覚えて、ページビュー（ページ移動のたび）と申込（Stripe）ボタンのクリックを送るだけ。
 * - Material の navigation.instant ではページ遷移で <script> が読み直されないので、
 *   初期化は document$（ページが描かれるたびに流れる）に載せる。
 * - 送信先はゲートウェイ（go.antecanis.com）。フォームの data-endpoint。
 * - Turnstile（Cloudflare）は明示描画。トークンは1回きりなので、失敗したら作り直す。
 *
 * ## UTM（2026年11月〜）
 * URL に utm_* があり、保存中の値が無い（または30日を過ぎた）ときだけ、localStorage に30日保存する
 * （**初回訪問の値を保つ**＝ファーストタッチ。上書きしない）。広告で来た人が日をおいて /subscribe/ に
 * 戻ってきても、最初の UTM を送れる。送り先はフォームの隠し項目 → ゲートウェイ → Mailchimp。
 *
 * ## 計測（GA4・Meta・Google 広告）
 * - メール登録：ゲートウェイが ok を返し、**このブラウザで同じアドレスをまだ数えていない**ときだけ、
 *   完了ページで1回：GA4 generate_lead・Meta Lead・Google 広告のコンバージョン（ラベルがあれば）。
 *   送り直し（2回目以降）は GA4 subscribe_repeat だけ。再読み込み・直アクセスでは何も送らない。
 *   ゲートウェイが応答に lead（真偽値。新規に作ったときだけ true）を返すようになったら、それに従う。
 * - 申込（Stripe）ボタンのクリック（href が extra.join_url で始まるリンク）：GA4 click_join・
 *   Meta InitiateCheckout・Google 広告のコンバージョン（ラベルがあれば）。
 * - 法人問い合わせの送信成功：GA4 generate_lead（form: corporate）・Meta Contact・Google 広告（ラベルがあれば）。
 * - Meta・Google 広告は、overrides/partials/tracking.html が ID と本番ホストを確かめて読み込んだときだけ
 *   送る（window.__aisiaTags.on）。GA4 は従来どおり Material の組み込み（dataLayer）。
 */
(function () {
  "use strict";

  var UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content"];
  var UTM_STORE = "aisia_utm_v2";
  var UTM_TTL = 30 * 24 * 60 * 60 * 1000;   // 30日
  var LEAD_STORE = "aisia_lead";             // 送信直後 → 完了ページへの受け渡し（sessionStorage）
  var LEADS_SEEN = "aisia_leads";            // このブラウザで数えたアドレス（ハッシュ。localStorage）

  var MESSAGES = {
    invalid_input: "入力内容をご確認ください。",
    verification_failed: "送信を確認できませんでした。お手数ですが、もう一度お試しください。",
    rate_limited: "短い時間に送信が続いたため、受け付けを一時止めています。しばらくしてからお試しください。",
    cannot_subscribe: "このアドレスでは登録できませんでした。support@antecanis.com にご連絡ください。",
    not_ready: "送信の準備をしています。数秒おいて、もう一度お試しください。",
    temporary: "ただいま送信できませんでした。時間をおいて、もう一度お試しください。"
  };
  var CORPORATE_SUFFIX = "お急ぎの場合は support@antecanis.com へメールでご連絡ください。";

  // ---- storage（プライベートブラウズ等で使えなくても落ちないように）----
  function store(kind) {
    try { var s = window[kind]; s.setItem("__aisia", "1"); s.removeItem("__aisia"); return s; }
    catch (e) { return null; }
  }
  function load(key, kind) {
    var s = store(kind || "sessionStorage");
    try { return s ? JSON.parse(s.getItem(key) || "null") : null; } catch (e) { return null; }
  }
  function save(key, value, kind) {
    var s = store(kind || "sessionStorage");
    try { if (s) s.setItem(key, JSON.stringify(value)); } catch (e) { /* 無視 */ }
  }
  function drop(key, kind) {
    var s = store(kind || "sessionStorage");
    try { if (s) s.removeItem(key); } catch (e) { /* 無視 */ }
  }
  // 30日の保持は localStorage。使えなければ sessionStorage（そのタブの間だけ）に落とす
  function longKind() { return store("localStorage") ? "localStorage" : "sessionStorage"; }

  // ---- UTM：初回訪問の値を30日（上書きしない）----
  function storedUtm() {
    var cur = load(UTM_STORE, longKind());
    if (!cur || !cur.ts || !cur.v || Date.now() - cur.ts >= UTM_TTL) return null;
    return cur;
  }
  function rememberUtm() {
    var params = new URLSearchParams(location.search);
    var found = {};
    var any = false;
    UTM_KEYS.forEach(function (k) {
      var v = (params.get(k) || "").slice(0, 100);
      if (v) { found[k] = v; any = true; }
    });
    if (!any || storedUtm()) return;
    save(UTM_STORE, { v: found, ts: Date.now() }, longKind());
  }
  function currentUtm() {
    var cur = storedUtm();
    return cur ? cur.v : {};
  }

  // ---- 計測 ----
  // GA4：Material は gtag をグローバルに出さないので dataLayer に直接積む（gtag.js は arguments の形を期待する）
  function gtagPush() {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(arguments);
  }
  function gtagEvent(name, params) { gtagPush("event", name, params || {}); }
  function tags() { return window.__aisiaTags || {}; }
  function metaTrack(name, params) {
    var t = tags();
    if (!t.on || !t.meta || typeof window.fbq !== "function") return;
    if (params) window.fbq("track", name, params); else window.fbq("track", name);
  }
  function adsConversion(label) {
    var t = tags();
    if (!t.on || !t.ads || !label) return;
    gtagPush("event", "conversion", { send_to: t.ads + "/" + label });
  }

  // メールアドレスをブラウザ内に置かないための短いハッシュ（cyrb53。照合に使うだけで、どこにも送らない）
  function hash(str) {
    var h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    for (var i = 0, ch; i < str.length; i++) {
      ch = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
  }
  // 数える登録か（ゲートウェイの lead があればそれに従う。無ければ、このブラウザで初めてのアドレスか）
  function countLead(email, res) {
    var key = hash("aisia:" + String(email || "").trim().toLowerCase());
    var kind = longKind();
    var seen = load(LEADS_SEEN, kind);
    if (!Array.isArray(seen)) seen = [];
    var first = seen.indexOf(key) < 0;
    if (first) save(LEADS_SEEN, seen.concat([key]).slice(-20), kind);
    return res && typeof res.lead === "boolean" ? res.lead : first;
  }

  // ---- Turnstile ----
  var turnstileLoading = null;
  function loadTurnstile() {
    if (window.turnstile) return Promise.resolve(window.turnstile);
    if (turnstileLoading) return turnstileLoading;
    turnstileLoading = new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      s.async = true;
      s.onload = function () { resolve(window.turnstile); };
      s.onerror = function () { turnstileLoading = null; reject(new Error("turnstile")); };
      document.head.appendChild(s);
    });
    return turnstileLoading;
  }

  // ---- フォーム ----
  function setupForm(form) {
    if (form.dataset.ready) return;
    form.dataset.ready = "1";

    var kind = form.getAttribute("data-aisia-form");
    var endpoint = form.getAttribute("data-endpoint");
    var sitekey = form.getAttribute("data-sitekey");
    var button = form.querySelector("[type=submit]");
    var buttonLabel = button.textContent;
    var errorBox = form.querySelector(".lp-form__error");
    var slot = form.querySelector(".lp-turnstile");
    var widgetId = null;

    if (sitekey && slot) {
      loadTurnstile().then(function (ts) {
        if (!document.body.contains(slot)) return;   // 別ページへ移った
        widgetId = ts.render(slot, {
          sitekey: sitekey,
          language: "ja",
          appearance: "interaction-only",   // 必要なときだけ表示
          action: kind
        });
      }).catch(function () { /* 送信時に not_ready を出す */ });
    }

    function token() {
      if (!sitekey) return "";
      try { return window.turnstile && widgetId !== null ? window.turnstile.getResponse(widgetId) || "" : ""; }
      catch (e) { return ""; }
    }
    function resetToken() {
      try { if (window.turnstile && widgetId !== null) window.turnstile.reset(widgetId); } catch (e) { /* 無視 */ }
    }

    function showError(code, fields) {
      var msg = MESSAGES[code] || MESSAGES.temporary;
      if (kind === "corporate" && (code === "temporary" || !MESSAGES[code])) msg += CORPORATE_SUFFIX;
      errorBox.textContent = msg;
      errorBox.hidden = false;
      (fields || []).forEach(function (name) {
        var el = form.elements[name];
        if (el && el.setAttribute) el.setAttribute("aria-invalid", "true");
      });
      var first = fields && fields.length && form.elements[fields[0]];
      if (first && first.focus) first.focus();
    }
    function clearError() {
      errorBox.hidden = true;
      errorBox.textContent = "";
      Array.prototype.forEach.call(form.querySelectorAll("[aria-invalid]"), function (el) {
        el.removeAttribute("aria-invalid");
      });
    }
    function busy(on) {
      button.disabled = on;
      button.textContent = on ? (button.getAttribute("data-busy-label") || "送信しています…") : buttonLabel;
    }

    function payload() {
      var data = {};
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.disabled) return;
        if (el.type === "checkbox") {
          if (!data[el.name]) data[el.name] = [];
          if (el.checked) data[el.name].push(el.value);
        } else {
          data[el.name] = el.value.trim();
        }
      });
      // 「知ったきっかけ」が任意のフォーム：空欄のときに送る値（mkdocs.yml の extra.forms.source_blank）
      var blank = form.getAttribute("data-source-blank");
      if (blank !== null && "source" in data && !data.source) data.source = blank;
      var utm = currentUtm();
      UTM_KEYS.forEach(function (k) { data[k] = data[k] || utm[k] || ""; });
      data.turnstile_token = token();
      return data;
    }

    form.addEventListener("input", function (e) {
      if (e.target && e.target.removeAttribute) e.target.removeAttribute("aria-invalid");
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearError();
      if (!form.reportValidity()) return;
      var data = payload();
      if (sitekey && !data.turnstile_token) { showError("not_ready"); return; }

      function send() {
        return fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
          credentials: "omit"
        }).then(function (resp) {
          return resp.json().catch(function () { return { ok: false, error: "temporary" }; });
        });
      }

      busy(true);
      send().then(function (res) {
        if (res && res.ok) {
          if (kind === "subscribe") {
            // 計測は完了ページで1回だけ（再読み込み・直アクセスでは数えない）。
            // 数える登録か、送り直しかをここで決めて渡す
            save(LEAD_STORE, countLead(data.email, res) ? "subscribe" : "subscribe:repeat");
            location.href = form.getAttribute("data-success");
            return;
          }
          gtagEvent("generate_lead", { form: kind });
          if (kind === "corporate") {
            metaTrack("Contact");
            adsConversion(tags().adsInquiry);
          }
          var done = document.querySelector("[data-form-done='" + kind + "']");
          if (done) {
            form.hidden = true;
            Array.prototype.forEach.call(document.querySelectorAll("[data-form-intro='" + kind + "']"), function (el) {
              el.hidden = true;
            });
            done.hidden = false;
            done.setAttribute("tabindex", "-1");
            done.focus();
          }
          busy(false);
          return;
        }
        busy(false);
        resetToken();
        showError(res && res.error, res && res.fields);
      }).catch(function () {
        busy(false);
        resetToken();
        showError("temporary");
      });
    });
  }

  // ---- 完了ページ：送信直後に着いたときだけ計測する ----
  function trackThanks() {
    var marker = document.querySelector("[data-lead-page]");
    if (!marker) return;
    var form = marker.getAttribute("data-lead-page");
    var v = load(LEAD_STORE);
    if (v === form) {
      drop(LEAD_STORE);
      gtagEvent("generate_lead", { form: form });
      metaTrack("Lead");
      adsConversion(tags().adsLead);
    } else if (v === form + ":repeat") {
      drop(LEAD_STORE);
      gtagEvent("subscribe_repeat", { form: form });
    }
  }

  // ---- ページビュー：Material の instant navigation でのページ移動のたびに（Meta・Google 広告）----
  // 最初の表示は partials/tracking.html が送っているので、2回目以降だけ。GA4 は Material が送る
  var lastPath = null;
  function pageView() {
    var p = location.pathname + location.search;
    if (lastPath === null || p === lastPath) { lastPath = p; return; }
    lastPath = p;
    var t = tags();
    if (!t.on) return;
    if (t.meta && typeof window.fbq === "function") window.fbq("track", "PageView");
    if (t.ads) gtagPush("config", t.ads);
  }

  // ---- クリックの計測（申込ボタン・data-ga のリンク）。document に1回だけ付ける ----
  var clicksBound = false;
  function bindClicks() {
    if (clicksBound) return;
    clicksBound = true;
    document.addEventListener("click", function (e) {
      var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
      if (!a) return;
      var join = tags().joinUrl;
      if (join && a.href.indexOf(join) === 0) {
        gtagEvent("click_join", {
          page_path: location.pathname,
          link_text: (a.textContent || "").replace(/\s+/g, " ").trim().slice(0, 60)
        });
        metaTrack("InitiateCheckout");
        adsConversion(tags().adsJoin);
        return;
      }
      var name = a.getAttribute("data-ga");
      if (name) gtagEvent(name, { page_path: location.pathname, link_url: a.href });
    }, true);
  }

  // ---- ライブラリーから来た人向けの小見出し ----
  function libraryEyebrow() {
    var el = document.querySelector("[data-library-eyebrow]");
    if (!el) return;
    var src = new URLSearchParams(location.search).get("utm_source") || currentUtm().utm_source;
    if (src === "library") {
      var span = el.querySelector("span") || el;
      span.textContent = el.getAttribute("data-library-eyebrow");
    }
  }

  // ---- スマホの固定ボタン：同じ行き先のボタンが見えている間は隠す ----
  // 隠す相手は data-sticky-hide（CSS セレクタ）。無ければ /subscribe/ のフォーム（#form）。
  // ホームはヒーローのボタン・最後の CTA・フッター（規約リンクを覆わないため）
  var observer = null;
  function stickyCta() {
    if (observer) { observer.disconnect(); observer = null; }
    var bar = document.querySelector("[data-sticky-cta]");
    if (!bar || !("IntersectionObserver" in window)) return;
    var targets = document.querySelectorAll(bar.getAttribute("data-sticky-hide") || "#form");
    if (!targets.length) return;
    var seen = new Set();
    bar.hidden = false;
    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) seen.add(en.target); else seen.delete(en.target);
      });
      bar.classList.toggle("is-hidden", seen.size > 0);
    }, { threshold: 0.15 });
    Array.prototype.forEach.call(targets, function (t) { observer.observe(t); });
  }

  // ---- 「無料で案内を受け取る」でフォームへ移り、最初の欄にフォーカス ----
  function scrollLinks() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-scroll-to-form]"), function (a) {
      if (a.dataset.ready) return;
      a.dataset.ready = "1";
      a.addEventListener("click", function (e) {
        var target = document.getElementById("form");
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        var first = target.querySelector("input:not([type=hidden])");
        if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 400);
      });
    });
  }

  function init() {
    rememberUtm();
    pageView();
    bindClicks();
    Array.prototype.forEach.call(document.querySelectorAll("form[data-aisia-form]"), setupForm);
    trackThanks();
    libraryEyebrow();
    stickyCta();
    scrollLinks();
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
