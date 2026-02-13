document.addEventListener("DOMContentLoaded", function () {

    // Highlight Active Nav Link
    const currentPath = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath) {
            link.classList.add("active");
        }
    });

    // Smooth scroll for anchor links only
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    console.log("Production Stable Version Loaded 🚀");
});
