"""配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 数据库
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ai_agile.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
    LLM_TEMPERATURE = 0.3
    LLM_MAX_TOKENS = 4096

    # 文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
