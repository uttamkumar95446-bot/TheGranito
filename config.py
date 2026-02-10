

# config.py
import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False

