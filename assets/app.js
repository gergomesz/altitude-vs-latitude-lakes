(function () {
  "use strict";
  // dark mode button
  (function themeToggle() {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    const root = document.documentElement;
    const mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
    let stored = null;
    try { stored = localStorage.getItem("lakes-theme"); } catch (e) { /* storage unavailable */ }
    if (stored === "dark" || stored === "light") root.setAttribute("data-theme", stored);
    const current = () => root.getAttribute("data-theme") || (mq && mq.matches ? "dark" : "light");
    const label = () => {
      const dark = current() === "dark";
      btn.setAttribute("aria-pressed", String(dark));
      btn.querySelector("span").textContent = dark ? "Light mode" : "Dark mode";
    };
    btn.addEventListener("click", () => {
      const next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("lakes-theme", next); } catch (e) {}
      label();
    });
    if (mq && mq.addEventListener) mq.addEventListener("change", label);
    label();
  })();

  document.querySelectorAll(".eli-btn").forEach((b) => b.addEventListener("click", () => {
    const panel = document.getElementById(b.getAttribute("aria-controls"));
    if (!panel) return;
    const open = b.getAttribute("aria-expanded") !== "true";
    b.setAttribute("aria-expanded", String(open)); panel.hidden = !open;
  }));

})();
