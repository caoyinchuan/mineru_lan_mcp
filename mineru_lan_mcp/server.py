"""MCP PDF Parser 服务 - 使用 FastMCP 框架"""

from fastmcp import FastMCP
from pathlib import Path
from .pdf_parser import PDFParser

mcp = FastMCP("MCP PDF Parser")

pdf_parser = PDFParser()


@mcp.tool
def parse_pdf_to_markdown(
    pdf_path: str,
    output_dir: str = "./output",
    lang_list: list[str] = ["ch"],
    backend: str = "pipeline",
    parse_method: str = "auto",
    formula_enable: bool = True,
    table_enable: bool = True,
    start_page_id: int = 0,
    end_page_id: int = 99999,
    return_images: bool = True,
) -> str:
    """将PDF文件解析为Markdown格式。

    上传PDF到解析服务，返回Markdown内容和图片数据。
    
    Args:
        pdf_path: PDF文件的绝对路径（必需）
        output_dir: 输出目录（默认: ./output）
        lang_list: 语言列表（默认: ['ch']）
        backend: 后端类型（默认: pipeline）
        parse_method: 解析方法（默认: auto）
        formula_enable: 是否启用公式识别（默认: true）
        table_enable: 是否启用表格识别（默认: true）
        start_page_id: 起始页码（默认: 0）
        end_page_id: 结束页码（默认: 99999）
        return_images: 是否返回图片（默认: true）
    
    Returns:
        解析结果的摘要信息，包含Markdown文件路径和图片文件路径
    """
    result = pdf_parser.parse_pdf(
        pdf_path=pdf_path,
        output_dir=output_dir,
        lang_list=lang_list,
        backend=backend,
        parse_method=parse_method,
        formula_enable=formula_enable,
        table_enable=table_enable,
        return_images=return_images,
        start_page_id=start_page_id,
        end_page_id=end_page_id,
    )
    
    images_info = ""
    if result.get('images'):
        images_info = f"\n图片文件: {', '.join(result['images'])}"
    
    return f"""PDF解析成功！

Markdown文件: {result['markdown_file']}{images_info}"""


if __name__ == "__main__":
    mcp.run()