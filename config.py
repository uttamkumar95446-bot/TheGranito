import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-here'
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class DevelopmentConfig(Config):
    DEBUG = True
