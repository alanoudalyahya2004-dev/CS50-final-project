/* Dark mode toggle with Bootstrap 5.3 color modes + class fallback */

(function() {
    const STORAGE_KEY = "vh-theme";
    const body = document.getElementById("appBody");
    const btn = document.getElementById("themeToggle");
    const icon = document.getElementById("themeIcon");
    const text = document.getElementById("themeText");
    const html = document.documentElement; // <html>

    if (!body || !btn || !icon || !text) return;

    function render(isDark) {
        // Bootstrap color mode
        html.setAttribute("data-bs-theme", isDark ? "dark" : "light");
        // Our custom overrides
        body.classList.toggle("theme-dark", isDark);
        // Button UI
        icon.textContent = isDark ? "☀️" : "🌙";
        const labelOn = btn.getAttribute("data-label-on") || "Disable dark mode";
        const labelOff = btn.getAttribute("data-label-off") || "Enable dark mode";
        text.textContent = isDark ? labelOn : labelOff;
        console.log("Dark mode:", isDark); // debug
    }

    // Apply stored preference on load
    const saved = localStorage.getItem(STORAGE_KEY);
    const startDark = saved === "dark";
    render(startDark);

    // Toggle
    btn.addEventListener("click", () => {
        const isDark = !body.classList.contains("theme-dark");
        localStorage.setItem(STORAGE_KEY, isDark ? "dark" : "light");
        render(isDark);
    });

})();
