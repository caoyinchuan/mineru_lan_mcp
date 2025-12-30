"""测试客户端 - 调用 MCP PDF Parser 服务"""

import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from pathlib import Path

async def test_parse_pdf():
    """测试PDF解析功能"""
    # 获取测试文件的绝对路径
    pdf_path = Path(__file__).parent / "test_file.pdf"
    
    print(f"测试文件路径: {pdf_path}")
    print(f"文件存在: {pdf_path.exists()}")
    print()
    
    # 创建stdio transport
    transport = StdioTransport(
        command="uv",
        args=["run", "python", "-m", "mineru_lan_mcp.server"],
        cwd=str(Path(__file__).parent.parent)
    )
    
    # 连接到MCP服务器
    async with Client(transport) as client:
        # 列出可用工具
        tools = await client.list_tools()
        print(f"可用工具: {[tool.name for tool in tools]}")
        print()
        
        # 调用parse_pdf_to_markdown工具
        print("开始解析PDF...")
        result = await client.call_tool("parse_pdf_to_markdown", {
            "pdf_path": str(pdf_path),
            "lang_list": ["ch"],
            "backend": "pipeline",
            "parse_method": "auto",
            "formula_enable": True,
            "table_enable": True
        })
        
        print("\n" + "=" * 60)
        print("解析结果:")
        print("=" * 60)
        print(result.content[0].text)
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_parse_pdf())