"""文件处理模块：处理文件上传"""

import requests
from pathlib import Path
from .config import Config


class FileHandler:
    """文件处理器"""
    
    def upload_pdf(self, pdf_path: str, params: dict) -> dict:
        """上传PDF文件到解析API
        
        Args:
            pdf_path: PDF文件路径
            params: API参数
            
        Returns:
            API响应数据
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        # 准备multipart/form-data，确保布尔值正确传递
        formatted_params = {}
        for key, value in params.items():
            if isinstance(value, bool):
                formatted_params[key] = 'true' if value else 'false'
            elif isinstance(value, list):
                formatted_params[key] = ','.join(value)
            else:
                formatted_params[key] = str(value)
        
        files = {'files': open(pdf_file, 'rb')}
        
        try:
            response = requests.post(
                Config.FILE_PARSE_ENDPOINT,
                files=files,
                data=formatted_params,
                timeout=Config.UPLOAD_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        finally:
            files['files'].close()