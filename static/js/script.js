/**
 * ==========================================
 * SCROLL FIX - KEEP HASH IN URL BUT START FROM TOP
 * Solution for: URL has #services but want to load from top
 * ==========================================
 */

// SOLUTION: Prevent auto-scroll while keeping hash in URL

// Method 1: Override scroll behavior (BEST SOLUTION)
(function() {
    'use strict';
    
    // Save the hash
    const hash = window.location.hash;
    
    // Temporarily remove hash
    if (hash) {
        // Remove hash without adding to history
        history.replaceState(null, null, ' ');
    }
    
    // Force scroll to top immediately
    window.scrollTo(0, 0);
    
    // After page loads, restore hash without scrolling
    window.addEventListener('load', function() {
        // Restore hash
        if (hash) {
            history.replaceState(null, null, hash);
        }
        
        // Keep at top
        window.scrollTo(0, 0);
    });
})();

// Method 2: Prevent default scroll behavior
window.addEventListener('DOMContentLoaded', function() {
    // Force to top
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
});

// Method 3: Override hash scrolling
if (window.location.hash) {
    // Prevent automatic scroll to hash
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 1);
}

/**
 * ==========================================
 * COMPLETE SCRIPT.JS - WITH HASH PRESERVATION
 * Replace your entire script.js with this:
 * ==========================================
 */

// Prevent auto-scroll to hash
(function() {
    const hash = window.location.hash;
    
    // Remove hash temporarily
    if (hash) {
        history.replaceState(null, null, window.location.pathname + window.location.search);
    }
    
    // Force to top
    window.scrollTo(0, 0);
    
    // Restore hash after load (without scrolling)
    window.addEventListener('load', function() {
        if (hash) {
            // Add hash back without scrolling
            history.replaceState(null, null, hash);
        }
        setTimeout(() => window.scrollTo(0, 0), 0);
    });
})();

// Disable scroll restoration
if (history.scrollRestoration) {
    history.scrollRestoration = 'manual';
}

// Main code
document.addEventListener("DOMContentLoaded", () => {
    // Keep at top
    window.scrollTo(0, 0);
    
    // Smooth scroll for anchor links (when user clicks)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const href = this.getAttribute("href");
            if (href && href !== "#") {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: "smooth" });
                    
                    // Update URL with hash
                    history.pushState(null, null, href);
                }
            }
        });
    });

    // Typewriter
    const text = "Full Stack Web Developer";
    let index = 0;
    const element = document.querySelector(".typewriter") || document.querySelector(".typing-animation");
    
    if (element) {
        function type() {
            element.textContent = text.slice(0, index++);
            if (index <= text.length) setTimeout(type, 80);
        }
        type();
    }

    // Dark/Light Toggle
    const toggle = document.createElement("button");
    toggle.innerText = "Toggle Theme";
    toggle.className = "btn-3d";
    toggle.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 999;
    `;
    document.body.appendChild(toggle);
    
    toggle.onclick = () => {
        document.documentElement.dataset.theme =
            document.documentElement.dataset.theme === "light" ? "dark" : "light";
    };

    console.log('✅ Page loaded from top with hash preserved!');
});
