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

本仓库已写好 **`.cursor/mcp.json`**（`type: stdio`，指向本机 venv 与 `MEDIA_EXTRACT_WORKSPACE`）。请 **重新加载窗口**（命令面板：`Developer: Reload Window`）或重启 Cursor，然后在 **设置 → MCP** 中确认出现 **`media-extract`**。

若列表里没有该服务器，可把 `.cursor/mcp.json` 里的 `mcpServers` 段落合并到用户目录 **`%USERPROFILE%\.cursor\mcp.json`**（与官方文档一致）。

工具名：**`extract_file`**。`file_path` 须落在 **`MEDIA_EXTRACT_WORKSPACE`** 之下（相对工作区根或该目录内的绝对路径）。可选参数：`ocr`、`password`、`output_format`（`text` | `json`）。

克隆本仓库到其它机器后，请编辑 `.cursor/mcp.json` 中的 `command` / `cwd` / `MEDIA_EXTRACT_WORKSPACE` 为本地路径。

## 支持格式

`.docx`、`.pptx`、`.pdf`、`.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` `.tif` `.tiff`。不支持旧版 `.ppt`。

## 上传到 GitHub

本仓库根目录已 `git init` 且默认分支为 `main`。在 GitHub 新建空仓库后执行（替换为你的用户名与仓库名）：

```powershell
cd "d:\GAME DESIGN\skills"
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

若已存在 `origin`，改用 `git remote set-url origin ...`。
