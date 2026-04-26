import os
from datetime import timedelta
from werkzeug.utils import secure_filename
import re

# 在配置类定义之前加载.env文件
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(env_path)

class Config:
    # 安全配置 - 必须通过环境变量设置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置 - 缩短过期时间提高安全性
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 2)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 7)))
    
    # 文件上传配置 - 限制大小和类型
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50)) * 1024 * 1024  # 默认50MB
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'mp4,mp3,jpg,jpeg,png,pdf,doc,docx').split(','))
    
    # 安全配置
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'default_salt')
    
    # 验证配置
    MAX_USERNAME_LENGTH = 50
    MAX_PASSWORD_LENGTH = 128
    MIN_PASSWORD_LENGTH = 6
    
    # 输入验证正则表达式
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,50}$')
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @classmethod
    def validate_config(cls):
        """验证必要配置是否存在"""
        required = {
            'SECRET_KEY': cls.SECRET_KEY,
            'JWT_SECRET_KEY': cls.JWT_SECRET_KEY,
            'SQLALCHEMY_DATABASE_URI': cls.SQLALCHEMY_DATABASE_URI,
        }
        missing_vars = [k for k, v in required.items() if not v]
        
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        
        # 验证数据库URL格式
        if not cls.SQLALCHEMY_DATABASE_URI.startswith(('mysql+pymysql://', 'postgresql://', 'sqlite://')):
            raise ValueError("数据库URL格式不正确")
            
        return True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 开发环境显示SQL查询

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # 生产环境安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 文件上传限制更严格
    MAX_CONTENT_LENGTH = min(Config.MAX_CONTENT_LENGTH, 20 * 1024 * 1024)  # 生产环境最大20MB

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}