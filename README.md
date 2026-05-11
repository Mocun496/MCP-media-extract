# media-extract

从本机 **DOCX、PPTX、PDF、常见图片** 抽取纯文本或 **UDR JSON**（带 Schema 校验）。支持 **命令行** 与 **Cursor MCP**。

## 安装

```powershell
cd media_extract_tool
python -m venv .venv
.\.venv\Scripts\pip install -U pip
.\.venv\Scripts\pip install -e .
```

图片 OCR（可选）：

```powershell
.\.venv\Scripts\pip install pytesseract
```

并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)（Windows 可用 winget：`winget install UB-Mannheim.TesseractOCR`）。

## 命令行

在**本仓库根目录**（与 `media_extract_tool` 同级）执行：

```powershell
.\media_extract_tool\.venv\Scripts\python -m media_extract extract "相对或绝对路径\文件.docx" --format text
```

常用参数：

- `--format json`：输出完整 UDR（JSON）
- `--ocr`：对图片做 OCR（需 pytesseract + Tesseract）
- `--password 密码`：加密 PDF
- `--no-validate`：跳过 Schema 校验（调试用）

## Cursor MCP

1. 在 Cursor **设置 → MCP** 中新增服务器（stdio），示例（请把路径改成你的本机绝对路径）：

```json
{
  "mcpServers": {
    "media-extract": {
      "command": "D:/GAME DESIGN/skills/media_extract_tool/.venv/Scripts/python.exe",
      "args": ["-m", "media_extract.mcp_server"],
      "cwd": "D:/GAME DESIGN/skills",
      "env": {
        "MEDIA_EXTRACT_WORKSPACE": "D:/GAME DESIGN/skills"
      }
    }
  }
}
```

2. 重启 Cursor 或重载 MCP。工具名：**`extract_file`**。  
3. **`file_path`** 必须为 **`MEDIA_EXTRACT_WORKSPACE` 目录下的相对路径**（或落在该目录内的绝对路径），否则会被拒绝，避免任意读盘。

参数与 CLI 类似：`ocr`、`password`、`output_format`（`text` | `json`）。

## 支持格式

`.docx`、`.pptx`、`.pdf`、`.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` `.tif` `.tiff`。不支持旧版 `.ppt`。
