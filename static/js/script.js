// script.js के top पर
if (history.scrollRestoration) {
    history.scrollRestoration = 'manual';
}

window.addEventListener('load', () => {
    if (window.location.hash) {
        // URL से # हटा दें (scroll को reset करते हुए)
        history.pushState("", document.title, window.location.pathname);
    }

    // browser को अपना native smooth scroll देने दो
    // scroll top की need न हो तो setTimeout(scrollTo) हटा दो
});

 * ==========================================
 * THEGRANITO PORTFOLIO - PROFESSIONAL JS
 * Version: 2.0
 * Author: Uttam Kumar
 * ==========================================
 */

(function() {
    'use strict';

    // ==================== CONFIGURATION ====================
    const CONFIG = {
        typewriter: {
            texts: [
                "Full Stack Web Developer",
                "Python & Flask Expert",
                "UI/UX Designer",
                "Problem Solver"
            ],
            typingSpeed: 80,
            deletingSpeed: 50,
            pauseTime: 2000
        },
        preloader: {
            minDisplayTime: 1000,
            fadeOutDuration: 500
        },
        navbar: {
            scrollThreshold: 50
        },
        backToTop: {
            showThreshold: 300,
            scrollDuration: 800
        },
        cursor: {
            enabled: true // Set to false to disable custom cursor
        }
    };

    // ==================== UTILITY FUNCTIONS ====================
    
    /**
     * Debounce function to limit how often a function can fire
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Check if element is in viewport
     */
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    /**
     * Smooth scroll to element
     */
    function smoothScrollTo(element, duration = 800) {
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = ease(timeElapsed, startPosition, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }

        function ease(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        }

        requestAnimationFrame(animation);
    }

    // ==================== PRELOADER ====================
    
    class Preloader {
        constructor() {
            this.preloader = document.getElementById('preloader');
            this.minDisplayTime = CONFIG.preloader.minDisplayTime;
            this.fadeOutDuration = CONFIG.preloader.fadeOutDuration;
        }

        hide() {
            if (!this.preloader) return;

            const loadTime = Date.now() - window.performance.timing.navigationStart;
            const remainingTime = Math.max(0, this.minDisplayTime - loadTime);

            setTimeout(() => {
                this.preloader.classList.add('hidden');
                setTimeout(() => {
                    this.preloader.style.display = 'none';
                }, this.fadeOutDuration);
            }, remainingTime);
        }
    }

    // ==================== NAVIGATION ====================
    
    class Navigation {
        constructor() {
            this.navbar = document.querySelector('.navbar');
            this.navLinks = document.querySelectorAll('.nav-link');
            this.scrollThreshold = CONFIG.navbar.scrollThreshold;
            this.init();
        }

        init() {
            this.handleScroll();
            this.setActiveLink();
            this.setupSmoothScroll();
            window.addEventListener('scroll', debounce(() => this.handleScroll(), 10));
            window.addEventListener('scroll', debounce(() => this.setActiveLink(), 100));
        }

        handleScroll() {
            if (window.scrollY > this.scrollThreshold) {
                this.navbar?.classList.add('scrolled');
            } else {
                this.navbar?.classList.remove('scrolled');
            }
        }

        setActiveLink() {
            const sections = document.querySelectorAll('section[id]');
            const scrollPosition = window.scrollY + 100;

            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                const sectionId = section.getAttribute('id');

                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    this.navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${sectionId}`) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }

        setupSmoothScroll() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    const href = anchor.getAttribute('href');
                    if (href === '#' || href === '') return;

                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        smoothScrollTo(target);
                        
                        // Close mobile menu if open
                        const navbarCollapse = document.querySelector('.navbar-collapse');
                        if (navbarCollapse?.classList.contains('show')) {
                            navbarCollapse.classList.remove('show');
                        }
                    }
                });
            });
        }
    }

    // ==================== TYPEWRITER EFFECT ====================
    
    class Typewriter {
        constructor(element, texts) {
            this.element = element;
            this.texts = texts;
            this.currentTextIndex = 0;
            this.currentCharIndex = 0;
            this.isDeleting = false;
            this.typingSpeed = CONFIG.typewriter.typingSpeed;
            this.deletingSpeed = CONFIG.typewriter.deletingSpeed;
            this.pauseTime = CONFIG.typewriter.pauseTime;
        }

        type() {
            if (!this.element) return;

            const currentText = this.texts[this.currentTextIndex];
            
            if (this.isDeleting) {
                this.currentCharIndex--;
            } else {
                this.currentCharIndex++;
            }

            this.element.textContent = currentText.substring(0, this.currentCharIndex);

            let typeSpeed = this.isDeleting ? this.deletingSpeed : this.typingSpeed;

            if (!this.isDeleting && this.currentCharIndex === currentText.length) {
                typeSpeed = this.pauseTime;
                this.isDeleting = true;
            } else if (this.isDeleting && this.currentCharIndex === 0) {
                this.isDeleting = false;
                this.currentTextIndex = (this.currentTextIndex + 1) % this.texts.length;
                typeSpeed = 500;
            }

            setTimeout(() => this.type(), typeSpeed);
        }

        start() {
            this.type();
        }
    }

    // ==================== THEME TOGGLE ====================
    
    class ThemeToggle {
        constructor() {
            this.currentTheme = localStorage.getItem('theme') || 'dark';
            this.init();
        }

        init() {
            this.createToggleButton();
            this.applyTheme(this.currentTheme);
        }

        createToggleButton() {
            const button = document.createElement('button');
            button.className = 'theme-toggle';
            button.innerHTML = `
                <i class="fas fa-moon"></i>
                <i class="fas fa-sun"></i>
            `;
            button.setAttribute('aria-label', 'Toggle theme');
            button.setAttribute('title', 'Toggle light/dark theme');

            button.addEventListener('click', () => this.toggle());
            document.body.appendChild(button);

            this.button = button;
        }

        toggle() {
            this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
            this.applyTheme(this.currentTheme);
            localStorage.setItem('theme', this.currentTheme);
        }

        applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            if (this.button) {
                this.button.setAttribute('data-theme', theme);
            }
        }
    }

    // ==================== BACK TO TOP BUTTON ====================
    
    class BackToTop {
        constructor() {
            this.button = document.getElementById('backToTop');
            this.showThreshold = CONFIG.backToTop.showThreshold;
            this.init();
        }

        init() {
            if (!this.button) return;

            window.addEventListener('scroll', debounce(() => this.handleScroll(), 100));
            this.button.addEventListener('click', () => this.scrollToTop());
        }

        handleScroll() {
            if (window.scrollY > this.showThreshold) {
                this.button.style.display = 'flex';
                setTimeout(() => this.button.style.opacity = '1', 10);
            } else {
                this.button.style.opacity = '0';
                setTimeout(() => this.button.style.display = 'none', 300);
            }
        }

        scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    }

    // ==================== CUSTOM CURSOR ====================
    
    class CustomCursor {
        constructor() {
            if (!CONFIG.cursor.enabled) return;
            
            this.cursor = document.getElementById('cursor');
            this.cursorOutline = document.getElementById('cursor-outline');
            this.init();
        }

        init() {
            if (!this.cursor || !this.cursorOutline) return;

            document.addEventListener('mousemove', (e) => {
                this.cursor.style.left = e.clientX + 'px';
                this.cursor.style.top = e.clientY + 'px';
                
                setTimeout(() => {
                    this.cursorOutline.style.left = e.clientX + 'px';
                    this.cursorOutline.style.top = e.clientY + 'px';
                }, 50);
            });

            // Add hover effect on clickable elements
            const clickableElements = document.querySelectorAll('a, button, input, textarea, select, .clickable');
            clickableElements.forEach(el => {
                el.addEventListener('mouseenter', () => {
                    this.cursor.style.transform = 'scale(2)';
                    this.cursorOutline.style.transform = 'scale(1.5)';
                });
                el.addEventListener('mouseleave', () => {
                    this.cursor.style.transform = 'scale(1)';
                    this.cursorOutline.style.transform = 'scale(1)';
                });
            });
        }
    }

    // ==================== ANIMATED COUNTERS ====================
    
    class AnimatedCounter {
        constructor() {
            this.counters = document.querySelectorAll('[data-count]');
            this.init();
        }

        init() {
            if (this.counters.length === 0) return;

            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.animateCounter(entry.target);
                            observer.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.5 }
            );

            this.counters.forEach(counter => observer.observe(counter));
        }

        animateCounter(element) {
            const target = parseInt(element.getAttribute('data-count'));
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    element.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = target;
                }
            };

            updateCounter();
        }
    }

    // ==================== PROGRESS BARS ANIMATION ====================
    
    class ProgressBars {
        constructor() {
            this.progressBars = document.querySelectorAll('.progress-bar');
            this.init();
        }

        init() {
            if (this.progressBars.length === 0) return;

            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const width = entry.target.style.width || entry.target.getAttribute('style').match(/width:\s*(\d+)/)?.[1] + '%';
                            entry.target.style.width = '0%';
                            setTimeout(() => {
                                entry.target.style.width = width;
                            }, 100);
                            observer.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.5 }
            );

            this.progressBars.forEach(bar => observer.observe(bar));
        }
    }

    // ==================== FORM VALIDATION ====================
    
    class FormValidator {
        constructor() {
            this.forms = document.querySelectorAll('form[data-validate]');
            this.init();
        }

        init() {
            this.forms.forEach(form => {
                form.addEventListener('submit', (e) => this.handleSubmit(e, form));
                
                // Real-time validation
                const inputs = form.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    input.addEventListener('blur', () => this.validateField(input));
                    input.addEventListener('input', () => {
                        if (input.classList.contains('is-invalid')) {
                            this.validateField(input);
                        }
                    });
                });
            });
        }

        handleSubmit(e, form) {
            e.preventDefault();
            
            const inputs = form.querySelectorAll('input, textarea, select');
            let isValid = true;

            inputs.forEach(input => {
                if (!this.validateField(input)) {
                    isValid = false;
                }
            });

            if (isValid) {
                // Form is valid, proceed with submission
                form.submit();
            }
        }

        validateField(field) {
            const value = field.value.trim();
            const type = field.type;
            let isValid = true;
            let errorMessage = '';

            // Required validation
            if (field.hasAttribute('required') && !value) {
                isValid = false;
                errorMessage = 'This field is required';
            }
            // Email validation
            else if (type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid email';
                }
            }
            // Pattern validation
            else if (field.hasAttribute('pattern') && value) {
                const pattern = new RegExp(field.getAttribute('pattern'));
                if (!pattern.test(value)) {
                    isValid = false;
                    errorMessage = field.getAttribute('title') || 'Invalid format';
                }
            }
            // Minlength validation
            else if (field.hasAttribute('minlength')) {
                const minLength = parseInt(field.getAttribute('minlength'));
                if (value.length < minLength) {
                    isValid = false;
                    errorMessage = `Minimum ${minLength} characters required`;
                }
            }

            this.showValidationState(field, isValid, errorMessage);
            return isValid;
        }

        showValidationState(field, isValid, errorMessage) {
            const feedbackElement = field.parentElement.querySelector('.invalid-feedback') || 
                                   this.createFeedbackElement(field);

            if (isValid) {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
                feedbackElement.textContent = '';
            } else {
                field.classList.remove('is-valid');
                field.classList.add('is-invalid');
                feedbackElement.textContent = errorMessage;
            }
        }

        createFeedbackElement(field) {
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentElement.appendChild(feedback);
            return feedback;
        }
    }

    // ==================== TOOLTIPS ====================
    
    class Tooltips {
        constructor() {
            this.init();
        }

        init() {
            // Initialize Bootstrap tooltips if available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                const tooltipTriggerList = [].slice.call(
                    document.querySelectorAll('[data-bs-toggle="tooltip"]')
                );
                tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
            }
        }
    }

    // ==================== LAZY LOADING IMAGES ====================
    
    class LazyLoader {
        constructor() {
            this.images = document.querySelectorAll('img[data-src]');
            this.init();
        }

        init() {
            if ('IntersectionObserver' in window) {
                const imageObserver = new IntersectionObserver(
                    (entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                this.loadImage(entry.target);
                                imageObserver.unobserve(entry.target);
                            }
                        });
                    }
                );

                this.images.forEach(img => imageObserver.observe(img));
            } else {
                // Fallback for older browsers
                this.images.forEach(img => this.loadImage(img));
            }
        }

        loadImage(img) {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
            img.classList.add('loaded');
        }
    }

    // ==================== INITIALIZATION ====================
    
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize Preloader
        const preloader = new Preloader();
        window.addEventListener('load', () => preloader.hide());

        // Initialize Navigation
        new Navigation();

        // Initialize Typewriter
        const typewriterElement = document.querySelector('.typing-animation');
        if (typewriterElement) {
            const typewriter = new Typewriter(
                typewriterElement,
                CONFIG.typewriter.texts
            );
            typewriter.start();
        }

        // Initialize Theme Toggle
        new ThemeToggle();

        // Initialize Back to Top
        new BackToTop();

        // Initialize Custom Cursor
        new CustomCursor();

        // Initialize Animated Counters
        new AnimatedCounter();

        // Initialize Progress Bars
        new ProgressBars();

        // Initialize Form Validation
        new FormValidator();

        // Initialize Tooltips
        new Tooltips();

        // Initialize Lazy Loading
        new LazyLoader();

        // Initialize AOS (Animate On Scroll) if available
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                once: true,
                offset: 100
            });
        }

        console.log('🚀 TheGranito Portfolio initialized successfully!');
    });

    // ==================== EASTER EGG ====================
    
    // Konami Code Easter Egg
    let konamiCode = [];
    const konamiPattern = [
        'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
        'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
        'b', 'a'
    ];

    document.addEventListener('keydown', (e) => {
        konamiCode.push(e.key);
        konamiCode = konamiCode.slice(-konamiPattern.length);

        if (konamiCode.join(',') === konamiPattern.join(',')) {
            console.log('🎉 Konami Code Activated!');
            document.body.style.animation = 'rainbow 5s infinite';
        }
    });

})();

// ==================== RAINBOW ANIMATION (Easter Egg) ====================
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
`;
document.head.appendChild(style);
