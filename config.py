const CONFIG = {
    typewriter: {
        texts: [
            "Full Stack Web Developer",  // 
            "Python & Flask Expert",
            "UI/UX Designer",
            "Problem Solver"
        ],
        typingSpeed: 80,      // 
        deletingSpeed: 50,    //  
        pauseTime: 2000       // 
    },
    preloader: {
        minDisplayTime: 1000, // 
        fadeOutDuration: 500  //
    },
    navbar: {
        scrollThreshold: 50   //
    },
    backToTop: {
        showThreshold: 300,   // 
        scrollDuration: 800   // 
    },
    cursor: {
        enabled: true         // 
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

