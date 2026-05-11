from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from media_extract.runner import extract_media_result

mcp = FastMCP("media-extract")


def _workspace_root() -> Path:
    return Path(os.environ.get("MEDIA_EXTRACT_WORKSPACE", os.getcwd())).resolve()


def _resolve_under_workspace(file_path: str) -> Path:
    root = _workspace_root()
    p = Path(file_path)
    if not p.is_absolute():
        p = (root / p).resolve()
    else:
        p = p.resolve()
    root_r = root.resolve()
    if p != root_r:
        try:
            p.relative_to(root_r)
        except ValueError as e:
            raise ValueError(
                f"file_path 必须位于 MEDIA_EXTRACT_WORKSPACE 目录之下。当前工作区根: {root_r}"
            ) from e
    return p


@mcp.tool()
def extract_file(
    file_path: str,
    ocr: bool = False,
    password: str | None = None,
    output_format: str = "text",
) -> str:
    """从 DOCX / PPTX / PDF / 常见图片提取内容。file_path 建议为相对工作区根的路径；PDF 可传 password。output_format: text 或 json（UDR）。"""
    fmt = output_format if output_format in ("text", "json") else "text"
    try:
        path = _resolve_under_workspace(file_path)
    except ValueError as e:
        return json.dumps({"error": {"code": "FORBIDDEN", "message": str(e)}}, ensure_ascii=False)

    ok, payload = extract_media_result(
        path,
        password=password,
        ocr=ocr,
        validate=True,
        schema_path=None,
        out_format=fmt,
    )
    return payload.rstrip("\n") if ok else payload.rstrip("\n")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
