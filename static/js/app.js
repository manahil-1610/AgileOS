// AgileOS theme toggle (dark/light)
// Kommentarer på norsk, kode på engelsk

(function () {
  const STORAGE_KEY = "agileos-theme"; // "dark" | "light"
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
  }

  function getSavedTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "light" || saved === "dark") return saved;
    return "dark"; // default
  }

  function updateButton(btn, theme) {
    const isDark = theme === "dark";
    btn.setAttribute("aria-pressed", String(isDark));
    btn.textContent = isDark ? "Light mode" : "Dark mode";
    btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
  }

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    let theme = getSavedTheme();
    applyTheme(theme);
    updateButton(btn, theme);

    btn.addEventListener("click", () => {
      theme = theme === "dark" ? "light" : "dark";
      localStorage.setItem(STORAGE_KEY, theme);
      applyTheme(theme);
      updateButton(btn, theme);
    });
  });
})();
