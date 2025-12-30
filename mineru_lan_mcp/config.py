"""配置管理模块"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API配置
    API_BASE_URL = os.getenv("API_BASE_URL")
    if not API_BASE_URL:
        raise ValueError("API_BASE_URL 未配置")

    FILE_PARSE_ENDPOINT = f"{API_BASE_URL}/file_parse"
    
    # 默认参数
    DEFAULT_OUTPUT_DIR = "./output"
    DEFAULT_LANG_LIST = ["ch"]
    DEFAULT_BACKEND = "pipeline"
    DEFAULT_PARSE_METHOD = "auto"
    
    # 超时配置
    UPLOAD_TIMEOUT = int(os.getenv("UPLOAD_TIMEOUT", "300"))  # 5分钟
    
    # 缓存配置
    cache_dir_str = os.getenv("CACHE_DIR", str(Path.home() / ".mcp_pdf_parser_cache"))
    CACHE_DIR = Path(cache_dir_str).expanduser()
    
    @classmethod
    def ensure_cache_dir(cls):
        """确保缓存目录存在"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CACHE_DIR