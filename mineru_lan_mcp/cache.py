"""缓存管理模块"""

import hashlib
import sqlite3
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from .config import Config


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.cache_dir = Config.ensure_cache_dir()
        self.db_path = self.cache_dir / "cache.db"
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdf_cache (
                    cache_key TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _get_cache_key(self, pdf_path: str) -> str:
        """生成缓存键：使用文件路径的SHA256哈希"""
        return hashlib.sha256(pdf_path.encode('utf-8')).hexdigest()
    
    def _get_file_hash(self, pdf_path: str) -> str:
        """计算文件的SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _get_cache_files_dir(self, cache_key: str) -> Path:
        """获取缓存文件存储目录"""
        return self.cache_dir / "files" / cache_key
    
    def get(self, pdf_path: str, output_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取缓存
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果提供则将缓存文件复制到该目录
            
        Returns:
            缓存的解析结果，如果不存在或文件已变更则返回None
        """
        cache_key = self._get_cache_key(pdf_path)
        current_hash = self._get_file_hash(pdf_path)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT file_hash, result FROM pdf_cache WHERE cache_key = ?",
                    (cache_key,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                cached_hash, result_json = row
                
                # 检查文件哈希是否匹配
                if cached_hash != current_hash:
                    # 文件已变更，删除旧缓存
                    conn.execute(
                        "DELETE FROM pdf_cache WHERE cache_key = ?",
                        (cache_key,)
                    )
                    conn.commit()
                    self._delete_cache_files(cache_key)
                    return None
                
                result = json.loads(result_json)
                cache_files_dir = self._get_cache_files_dir(cache_key)
                
                # 检查缓存文件是否存在
                if not cache_files_dir.exists():
                    return None
                
                # 如果指定了输出目录，复制缓存文件
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    # 复制markdown文件
                    cached_md = cache_files_dir / Path(result['markdown_file']).name
                    if cached_md.exists():
                        target_md = output_path / cached_md.name
                        shutil.copy2(cached_md, target_md)
                        result['markdown_file'] = str(target_md)
                    
                    # 复制图片文件
                    cached_images_dir = cache_files_dir / "images"
                    if cached_images_dir.exists():
                        target_images_dir = output_path / "images"
                        target_images_dir.mkdir(parents=True, exist_ok=True)
                        new_images = []
                        for img_path in result['images']:
                            img_name = Path(img_path).name
                            cached_img = cached_images_dir / img_name
                            if cached_img.exists():
                                target_img = target_images_dir / img_name
                                shutil.copy2(cached_img, target_img)
                                new_images.append(str(target_img))
                        result['images'] = new_images
                
                return result
        except (sqlite3.Error, json.JSONDecodeError, IOError):
            return None
    
    def set(self, pdf_path: str, result: Dict[str, Any]) -> None:
        """设置缓存
        
        Args:
            pdf_path: PDF文件路径
            result: 解析结果
        """
        cache_key = self._get_cache_key(pdf_path)
        file_hash = self._get_file_hash(pdf_path)
        result_json = json.dumps(result, ensure_ascii=False)
        
        # 保存文件到缓存目录
        cache_files_dir = self._get_cache_files_dir(cache_key)
        cache_files_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制markdown文件
        md_file = Path(result['markdown_file'])
        if md_file.exists():
            shutil.copy2(md_file, cache_files_dir / md_file.name)
        
        # 复制图片文件
        for img_path in result['images']:
            img_file = Path(img_path)
            if img_file.exists():
                cache_images_dir = cache_files_dir / "images"
                cache_images_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img_file, cache_images_dir / img_file.name)
        
        # 保存到数据库
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO pdf_cache (cache_key, file_hash, result)
                VALUES (?, ?, ?)
                """,
                (cache_key, file_hash, result_json)
            )
            conn.commit()
    
    def _delete_cache_files(self, cache_key: str) -> None:
        """删除缓存文件目录"""
        cache_files_dir = self._get_cache_files_dir(cache_key)
        if cache_files_dir.exists():
            shutil.rmtree(cache_files_dir)
    
    def clear(self) -> None:
        """清空所有缓存"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM pdf_cache")
            conn.commit()
        
        # 删除所有缓存文件
        files_dir = self.cache_dir / "files"
        if files_dir.exists():
            shutil.rmtree(files_dir)