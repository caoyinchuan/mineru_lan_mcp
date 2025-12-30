"""PDF解析核心逻辑模块"""

from pathlib import Path
from typing import Optional, Dict, Any
from mineru_lan_mcp.file_handler import FileHandler
from mineru_lan_mcp.cache import CacheManager
from mineru_lan_mcp.config import Config


class PDFParser:
    """PDF解析器"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.cache = CacheManager()
    
    def parse_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        lang_list: Optional[list] = None,
        backend: Optional[str] = None,
        parse_method: Optional[str] = None,
        formula_enable: Optional[bool] = None,
        table_enable: Optional[bool] = None,
        server_url: Optional[str] = None,
        return_md: Optional[bool] = None,
        return_middle_json: Optional[bool] = None,
        return_model_output: Optional[bool] = None,
        return_content_list: Optional[bool] = None,
        return_images: Optional[bool] = None,
        response_format_zip: Optional[bool] = None,
        start_page_id: Optional[int] = None,
        end_page_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """解析PDF为Markdown"""
        # 检查缓存
        cached_result = self.cache.get(pdf_path, output_dir)
        if cached_result:
            return cached_result
        
        params = {
            'output_dir': output_dir or Config.DEFAULT_OUTPUT_DIR,
            'lang_list': lang_list or Config.DEFAULT_LANG_LIST,
            'backend': backend or Config.DEFAULT_BACKEND,
            'parse_method': parse_method or Config.DEFAULT_PARSE_METHOD,
            'formula_enable': formula_enable if formula_enable is not None else True,
            'table_enable': table_enable if table_enable is not None else True,
            'return_md': return_md if return_md is not None else True,
            'return_middle_json': return_middle_json if return_middle_json is not None else False,
            'return_model_output': return_model_output if return_model_output is not None else False,
            'return_content_list': return_content_list if return_content_list is not None else False,
            'return_images': return_images if return_images is not None else True,
            'response_format_zip': response_format_zip if response_format_zip is not None else False,
            'start_page_id': start_page_id if start_page_id is not None else 0,
            'end_page_id': end_page_id if end_page_id is not None else 99999,
        }
        
        if server_url is not None:
            params['server_url'] = server_url
        
        response = self.file_handler.upload_pdf(pdf_path, params)
        
        if 'results' not in response:
            raise ValueError(f"API响应格式异常: {response}")
        
        results = response['results']
        if not results:
            raise ValueError(f"API响应中没有结果数据: {response}")
        
        # 获取第一个文件的结果
        file_name = list(results.keys())[0]
        file_result = results[file_name]
        
        md_content = file_result.get('md_content')
        if not md_content:
            raise ValueError(f"API响应中没有markdown内容: {response}")
        
        # 创建输出目录
        output_path = Path(output_dir or Config.DEFAULT_OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存markdown文件
        pdf_name = Path(pdf_path).stem
        md_file_path = output_path / f"{pdf_name}.md"
        md_file_path.write_text(md_content, encoding='utf-8')
        
        # 处理图片
        images_data = file_result.get('images', {})
        saved_images = []
        images_dir = output_path / "images"
        
        if images_data:
            images_dir.mkdir(parents=True, exist_ok=True)
            for img_name, img_base64 in images_data.items():
                # 提取base64数据
                if img_base64.startswith('data:'):
                    img_base64 = img_base64.split(',', 1)[1]
                
                img_path = images_dir / img_name
                import base64
                img_path.write_bytes(base64.b64decode(img_base64))
                saved_images.append(str(img_path))
        
        result = {
            'markdown_file': str(md_file_path),
            'images': saved_images
        }
        
        # 保存到缓存
        self.cache.set(pdf_path, result)
        
        return result