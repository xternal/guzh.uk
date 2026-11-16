/* Shared layer for the four /rebuild/ product demos.
   Agent: a panel where the AI says, line by line, what it is doing and what it found.
   Tour: a first-run walkthrough that dims the page, lights up one element at a time and says what it is for.
   Spark: the icon on the main AI action. */
(function () {
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var ICON = { go: "✦", ok: "✓", warn: "!", bad: "!", info: "•" };

  var Agent = {
    init: function (name) {
      if (this.box) return;
      var b = el("aside", "agent hidden min");
      b.setAttribute("aria-label", name + " agent");
      b.innerHTML = '<header><span class="dot"></span><b>' + esc(name) + ' agent</b><span class="st">idle</span><button class="tog" type="button" aria-label="Show or hide the agent notes">+</button></header><ol aria-live="polite"><li class="empty">I do the reading, checking and drafting. You approve.</li></ol>';
      document.body.appendChild(b);
      this.box = b; this.list = b.querySelector("ol"); this.st = b.querySelector(".st");
      var tog = b.querySelector(".tog"), self0 = this;
      this.setMin = function (m) { b.classList.toggle("min", m); tog.textContent = m ? "+" : "–"; };
      tog.addEventListener("click", function () { clearTimeout(self0.fold); self0.setMin(!b.classList.contains("min")); });
      b.addEventListener("mouseenter", function () { clearTimeout(self0.fold); });
      var self = this; setTimeout(function () { self.box.classList.remove("hidden"); }, 400);
    },
    start: function (status) {
      clearTimeout(this.fold); this.box.classList.remove("hidden"); this.setMin(false); this.box.classList.add("working"); this.st.textContent = status || "working";
      var e = this.list.querySelector(".empty"); if (e) e.remove();
    },
    /* Types a line out, then resolves. kind: go | ok | warn | bad | info */
    say: function (text, kind) {
      var list = this.list, li = el("li", "ag-" + (kind || "info"), "<i>" + (ICON[kind] || "•") + '</i><span class="cur"></span>');
      list.appendChild(li); list.scrollTop = list.scrollHeight;
      var span = li.querySelector("span");
      if (reduce) { span.textContent = text; span.className = ""; return Promise.resolve(); }
      return new Promise(function (res) {
        var i = 0, step = Math.max(1, Math.round(text.length / 28));
        (function tick() {
          i += step; span.textContent = text.slice(0, i); list.scrollTop = list.scrollHeight;
          if (i < text.length) setTimeout(tick, 14); else { span.className = ""; res(); }
        })();
      });
    },
    done: function (status) {
      var self = this; this.box.classList.remove("working"); this.st.textContent = status || "done, waiting for you";
      clearTimeout(this.fold); this.fold = setTimeout(function () { self.setMin(true); }, 9000);
      if (!this.offered) {
        this.offered = true;
        var li = el("li", "ag-go ag-cta", '<i>✦</i><span>Want this on your own process? <a href="https://calendar.app.google/RG3g5WzxB3y9tXu39" target="_blank" rel="noopener noreferrer">Book a free 30-minute teardown</a></span>');
        this.list.appendChild(li); this.list.scrollTop = this.list.scrollHeight;
      }
    },
    /* A one-off note: opens the panel, then folds it again */
    note: function (text, kind) { var self = this; this.start("working"); return this.say(text, kind).then(function () { self.done("waiting for you"); }); }
  };

  var Tour = {
    /* steps: [{ el: selector or function returning an element, title, text }]; key: remembers it was seen */
    start: function (steps, key, after) {
      var live = steps.filter(function (s) { return find(s.el); });
      if (!live.length) return;
      var i = 0, dim = el("div", "tour-dim"), hole = el("div", "tour-hole"), tip = el("div", "tour-tip");
      tip.setAttribute("role", "dialog"); tip.setAttribute("aria-modal", "true");
      document.body.append(dim, hole, tip);
      function find(s) { var e = typeof s === "function" ? s() : document.querySelector(s); return e && e.getClientRects().length ? e : null; }
      function place() {
        var s = live[i], e = find(s.el); if (!e) return next();
        e.scrollIntoView({ block: "nearest", inline: "nearest" });
        var r = e.getBoundingClientRect(), pad = 6;
        hole.style.left = r.left - pad + "px"; hole.style.top = r.top - pad + "px"; hole.style.width = r.width + pad * 2 + "px"; hole.style.height = r.height + pad * 2 + "px";
        tip.innerHTML = '<div class="n">Step ' + (i + 1) + " of " + live.length + "</div><h4>" + esc(s.title) + "</h4><p>" + esc(s.text) + '</p><div class="tb"><button class="skip" type="button">Skip</button><button class="next" type="button">' + (i === live.length - 1 ? "Got it" : "Next") + "</button></div>";
        var tw = tip.offsetWidth, th = tip.offsetHeight, vw = innerWidth, vh = innerHeight;
        var top = r.bottom + 14 + th < vh ? r.bottom + 14 : r.top - th - 14 > 0 ? r.top - th - 14 : Math.max(12, vh - th - 12);
        var left = Math.min(Math.max(12, r.left), vw - tw - 12);
        tip.style.top = top + "px"; tip.style.left = left + "px";
        tip.querySelector(".next").focus();
        tip.querySelector(".next").onclick = next; tip.querySelector(".skip").onclick = end;
      }
      function next() { i++; if (i >= live.length) end(); else place(); }
      function end() {
        dim.remove(); hole.remove(); tip.remove(); removeEventListener("resize", place); removeEventListener("keydown", keys);
        try { localStorage.setItem("tour:" + key, "1"); } catch (e) {}
        if (after) after();
      }
      function keys(e) { if (e.key === "Escape") end(); if (e.key === "Enter" && document.activeElement && document.activeElement.classList.contains("next")) { e.preventDefault(); next(); } }
      dim.addEventListener("click", next);
      addEventListener("resize", place); addEventListener("keydown", keys);
      place();
    },
    seen: function (key) { try { return localStorage.getItem("tour:" + key) === "1"; } catch (e) { return true; } },
    /* The "?" button that replays the tour, and the first-visit start */
    mount: function (steps, key, after) {
      var self = this, help = el("button", "tour-help", "?");
      help.type = "button"; help.setAttribute("aria-label", "Show me around"); help.title = "Show me around";
      help.onclick = function () { self.start(steps, key, after); };
      document.body.appendChild(help);
      if (location.hash === "#ready" || location.hash === "#triaged") return;  /* links used for share images */
      if (!self.seen(key)) setTimeout(function () { self.start(steps, key, after); }, 700); else if (after) after();
    }
  };

  /* Pulse the main action until it is used */
  function pulse(sel) {
    var b = document.querySelector(sel); if (!b) return;
    b.classList.add("ag-pulse");
    b.addEventListener("click", function () { b.classList.remove("ag-pulse"); }, { once: true });
  }
  var SPARK = '<svg class="spark" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2l1.9 5.6L19.5 9.5l-5.6 1.9L12 17l-1.9-5.6L4.5 9.5l5.6-1.9zM19 14l.9 2.6 2.6.9-2.6.9L19 21l-.9-2.6-2.6-.9 2.6-.9z"/></svg>';

  window.Agent = Agent; window.Tour = Tour; window.agPulse = pulse; window.SPARK = SPARK;
})();
