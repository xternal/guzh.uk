(function () {
  var root = document.documentElement;
  function isDark() {
    var t = root.getAttribute("data-theme");
    return t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function paintBar() {
    var dark = isDark();
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) {
      m.setAttribute("content", dark ? "#241F1A" : "#F1EFE9");
    });
  }
  var btn = document.querySelector(".theme");
  if (btn) btn.addEventListener("click", function () {
    var next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
    paintBar();
  });
  paintBar();

  /* Keep the current tab visible on a narrow screen. */
  var cur = document.querySelector('.tabs a[aria-current="page"]');
  if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: "nearest", inline: "center" });

  /* A page brought back with Back never keeps a spinning button. */
  window.addEventListener("pageshow", function (e) { if (e.persisted) location.reload(); });
})();

/* Shared helpers for the demos. */
window.Rebuild = {
  busy: function (button, group, on) {
    button.setAttribute("aria-busy", on ? "true" : "false");
    (group || [button]).forEach(function (b) { b.disabled = on; });
  },
  wait: function (ms) {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    return new Promise(function (r) { setTimeout(r, reduce ? Math.min(ms, 60) : ms); });
  },
  esc: function (s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  },
  gbp: function (n) {
    return (n < 0 ? "-£" : "£") + Math.round(Math.abs(n)).toLocaleString("en-GB");
  },
  num: function (n, d) {
    return Number(n).toLocaleString("en-GB", { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 });
  },
  /* Before/after: the reader's own numbers in, hours and people out. */
  calc: function (form, out) {
    function run() {
      var v = {};
      form.querySelectorAll("input").forEach(function (i) { v[i.name] = Math.max(0, parseFloat(i.value) || 0); });
      var saved = v.count * (v.before - v.after) / 60;
      out.innerHTML =
        '<div class="stat"><b>' + Rebuild.num(saved, 1) + '</b><span>hours saved a week</span></div>' +
        '<div class="stat"><b>' + Rebuild.num(saved * 46) + '</b><span>hours a year (46 working weeks)</span></div>' +
        '<div class="stat"><b>' + Rebuild.num(saved / 37.5, 1) + '</b><span>full-time people freed</span></div>';
    }
    form.addEventListener("input", run);
    run();
  }
};
