/*
 * フォーム（/subscribe/ のメール登録・/join/corporate/ の法人問い合わせ）と、UTM の保持・計測。
 *
 * - 全ページで読み込まれる（mkdocs.yml の extra_javascript）。フォームの無いページでは
 *   URL の utm_* を覚えるだけ。広告でホーム等に着地してから /subscribe/ へ移っても、
 *   同じタブのあいだは最初の UTM を送れるようにする（sessionStorage）。
 * - Material の navigation.instant ではページ遷移で <script> が読み直されないので、
 *   初期化は document$（ページが描かれるたびに流れる）に載せる。
 * - 送信先はゲートウェイ（aisia-ops の gateway/forms.py）。フォームの data-endpoint。
 * - Turnstile（Cloudflare）は明示描画。トークンは1回きりなので、失敗したら作り直す。
 * - 計測は GA4 の generate_lead を送信成功の1回だけ（メール登録は完了ページの表示時）。
 */
(function () {
  "use strict";

  var UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content"];
  var UTM_STORE = "aisia_utm";
  var LEAD_STORE = "aisia_lead";

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
  function load(key) {
    try { return JSON.parse(sessionStorage.getItem(key) || "null"); } catch (e) { return null; }
  }
  function save(key, value) {
    try { sessionStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* 無視 */ }
  }
  function drop(key) {
    try { sessionStorage.removeItem(key); } catch (e) { /* 無視 */ }
  }

  // ---- UTM：URL にあればそれを、無ければ同じタブで最初に着地したときの値 ----
  function rememberUtm() {
    var params = new URLSearchParams(location.search);
    var found = {};
    var any = false;
    UTM_KEYS.forEach(function (k) {
      var v = (params.get(k) || "").slice(0, 100);
      if (v) { found[k] = v; any = true; }
    });
    if (any) save(UTM_STORE, found);
  }
  function currentUtm() {
    return load(UTM_STORE) || {};
  }

  // ---- GA4（Material は gtag をグローバルに出さないので dataLayer に直接積む）----
  // gtag.js は arguments オブジェクトを期待するので、同じ形にして積む
  function gtagEvent(name, params) {
    window.dataLayer = window.dataLayer || [];
    (function () { window.dataLayer.push(arguments); })("event", name, params);
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

      busy(true);
      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "omit"
      }).then(function (resp) {
        return resp.json().catch(function () { return { ok: false, error: "temporary" }; });
      }).then(function (res) {
        if (res && res.ok) {
          if (kind === "subscribe") {
            // 計測は完了ページで1回だけ（再読み込み・直アクセスでは数えない）
            save(LEAD_STORE, "subscribe");
            location.href = form.getAttribute("data-success");
            return;
          }
          gtagEvent("generate_lead", { form: kind });
          var done = document.querySelector("[data-form-done='" + kind + "']");
          if (done) {
            form.hidden = true;
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
    if (load(LEAD_STORE) === form) {
      drop(LEAD_STORE);
      gtagEvent("generate_lead", { form: form });
    }
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

  // ---- スマホの固定ボタン：フォームが見えている間は隠す ----
  var observer = null;
  function stickyCta() {
    if (observer) { observer.disconnect(); observer = null; }
    var bar = document.querySelector("[data-sticky-cta]");
    var target = document.getElementById("form");
    if (!bar || !target || !("IntersectionObserver" in window)) return;
    bar.hidden = false;
    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { bar.classList.toggle("is-hidden", en.isIntersecting); });
    }, { threshold: 0.15 });
    observer.observe(target);
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
