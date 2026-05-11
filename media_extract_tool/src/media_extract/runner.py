from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from media_extract.extractors import extract_docx, extract_image, extract_pdf, extract_pptx
from media_extract.udr import udr_text_concat, validate_udr


def _error_json(code: str, message: str, **details: Any) -> str:
    return json.dumps({"error": {"code": code, "message": message, "details": details}}, ensure_ascii=False)


def extract_media_result(
    path: Path,
    *,
    password: str | None,
    ocr: bool,
    validate: bool,
    schema_path: Path | None,
    out_format: str,
) -> tuple[bool, str]:
    """
    返回 (ok, payload)。
    ok 为 True 时 payload 为纯文本或 JSON 字符串；False 时为错误 JSON 字符串。
    """
    if not path.is_file():
        return False, _error_json("NOT_FOUND", "路径不是可读文件", path=str(path))

    suffix = path.suffix.lower()
    source_uri = path.resolve().as_posix()

    if suffix == ".ppt":
        return False, _error_json(
            "UNSUPPORTED_MEDIA_TYPE",
            "旧版 .ppt 不支持，请另存为 .pptx。",
        )

    try:
        if suffix == ".docx":
            udr = extract_docx(path, source_uri)
        elif suffix == ".pptx":
            udr = extract_pptx(path, source_uri)
        elif suffix == ".pdf":
            udr = extract_pdf(path, source_uri, password=password)
        elif suffix in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"):
            udr = extract_image(path, source_uri, ocr=ocr)
        else:
            return False, _error_json(
                "UNSUPPORTED_MEDIA_TYPE",
                f"不支持的扩展名: {suffix}",
                supported=[".docx", ".pptx", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"],
            )
    except ValueError as e:
        code = str(e)
        if code == "PDF_PASSWORD_REQUIRED":
            return False, _error_json("PDF_PASSWORD_REQUIRED", "该 PDF 需要密码。", hint="传入 password 参数。")
        if code == "PDF_PASSWORD_INVALID":
            return False, _error_json("PDF_PASSWORD_INVALID", "PDF 密码不正确。")
        return False, _error_json("VALIDATION_FAILED", str(e))
    except Exception as e:
        return False, _error_json("INTERNAL_ERROR", f"提取失败: {e!s}")

    if validate:
        try:
            validate_udr(udr, schema_path=schema_path)
        except FileNotFoundError as e:
            return False, _error_json("VALIDATION_FAILED", str(e))
        except Exception as e:
            return False, _error_json("VALIDATION_FAILED", f"UDR 未通过 JSON Schema: {e!s}")

    if out_format == "text":
        return True, udr_text_concat(udr.get("blocks", [])) + "\n"
    return True, json.dumps(udr, ensure_ascii=False, indent=2) + "\n"
