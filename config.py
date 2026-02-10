const CONFIG = {
    typewriter: {
        texts: [
            "Full Stack Web Developer",  // ← Edit these
            "Python & Flask Expert",
            "UI/UX Designer",
            "Problem Solver"
        ],
        typingSpeed: 80,      // ← Typing speed (ms)
        deletingSpeed: 50,    // ← Deleting speed (ms)
        pauseTime: 2000       // ← Pause between texts (ms)
    },
    preloader: {
        minDisplayTime: 1000, // ← Minimum preloader time (ms)
        fadeOutDuration: 500  // ← Fade out duration (ms)
    },
    navbar: {
        scrollThreshold: 50   // ← Scroll distance for sticky navbar
    },
    backToTop: {
        showThreshold: 300,   // ← Scroll distance to show button
        scrollDuration: 800   // ← Scroll animation duration (ms)
    },
    cursor: {
        enabled: true         // ← Enable/disable custom cursor
    }
};

# config.py
import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False

