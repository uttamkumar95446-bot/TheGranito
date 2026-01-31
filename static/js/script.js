document.addEventListener("DOMContentLoaded", () => {
  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({ behavior: "smooth" });
    });
  });

  // Typewriter
  const text = "AI Engineer | Innovator | Full Stack Dev";
  let index = 0;
  const element = document.querySelector(".typewriter");
  function type() {
    element.textContent = text.slice(0, index++);
    if (index <= text.length) setTimeout(type, 80);
  }
  type();

  // Dark/Light Toggle
  const toggle = document.createElement("button");
  toggle.innerText = "Toggle Theme";
  toggle.className = "btn-3d";
  document.body.appendChild(toggle);
  toggle.onclick = () => {
    document.documentElement.dataset.theme =
      document.documentElement.dataset.theme === "light" ? "dark" : "light";
  };
});