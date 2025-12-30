# MinerU Lan MCP

使用部署在局域网内的mineru-api，来解析PDF文件，将其转换为Markdown格式。


## 功能特性

- 将 PDF 解析为 Markdown 格式
- 提取并保存图片
- 支持表格识别
- 支持公式识别
- 支持分页解析

## 环境要求

- Python 3.8+
- uv (推荐) 或 pip

## 安装

```bash
# 使用 uv 安装依赖
uv sync
```
## 部署mineru-api
可以在本机或局域网任何一台电脑上操作
```bash
# 安装mineru
pip install -U mineru
# 运行mineru-api
export MINERU_MODEL_SOURCE=modelscope
mineru-api --host 0.0.0.0 --port 10880
```
## 配置

1. 复制环境变量示例文件：

```bash
copy .env.example .env
```

2. 编辑 `.env` 文件，配置 API 地址：

```env
API_BASE_URL=http://172.25.2.133:10880
UPLOAD_TIMEOUT=300
```

## 使用方法

### 作为 MCP 服务运行

```bash
# 使用 uv
uv run PATH_TO_YOUR_PROJECT/mineru_lan_mcp/mineru_lan_mcp/server.py
```
### MCP Server Configuration
```json
{
    "mineru-lan-mcp": {
      "description": "tranform pdf to markdown",
      "command": "uv",
      "args": [
        "run",
        "Path_to_your_project/mineru_lan_mcp/mineru_lan_mcp/server.py"
      ]
    }
}
```

### 测试客户端

```bash
uv run PATH_TO_YOUR_PROJECT/test/test_client.py
```

### MCP 工具参数

**工具名称**: `parse_pdf_to_markdown`

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| pdf_path | string | 是 | - | PDF 文件的绝对路径 |
| output_dir | string | 否 | ./output | 输出目录 |
| lang_list | array | 否 | ["ch"] | 语言列表 |
| backend | string | 否 | pipeline | 后端类型 |
| parse_method | string | 否 | auto | 解析方法 |
| formula_enable | boolean | 否 | true | 是否启用公式识别 |
| table_enable | boolean | 否 | true | 是否启用表格识别 |
| start_page_id | integer | 否 | 0 | 起始页码 |
| end_page_id | integer | 否 | 99999 | 结束页码 |
| return_images | boolean | 否 | true | 是否返回图片 |

### 返回结果

```
PDF解析成功！

Markdown文件路径: output/test_file.md
输出目录: output
图片文件: output/images/image1.jpg, output/images/image2.jpg
```

## 项目结构

```
.
├── mcp_pdf_parser/
│   ├── __init__.py
│   ├── server.py       # MCP 服务器主程序
│   ├── pdf_parser.py   # PDF 解析核心逻辑
│   ├── file_handler.py # 文件处理模块
│   └── config.py       # 配置管理
├── requirements.txt
├── .env.example
├── test_client.py
└── README.md
```

## 注意事项

- 确保 PDF 文件存在且可读
- 输出目录会自动创建
- 图片保存在输出目录的 `images` 子目录中