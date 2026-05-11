from __future__ import annotations

import argparse
import sys
from pathlib import Path

from media_extract.runner import extract_media_result


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="media-extract", description="本地 DOCX/PPTX/PDF/图片提取为文本或 UDR JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ex = sub.add_parser("extract", help="从单个文件提取")
    p_ex.add_argument("path", type=Path, help="本地文件路径")
    p_ex.add_argument("--password", default=None, help="PDF 密码")
    p_ex.add_argument("--ocr", action="store_true", help="图片 OCR（需 pytesseract + Tesseract）")
    p_ex.add_argument("--no-validate", action="store_true", help="跳过 JSON Schema 校验")
    p_ex.add_argument("--schema", type=Path, default=None, help="自定义 Schema 路径")
    p_ex.add_argument("--format", choices=("json", "text"), default="json", help="输出格式")

    args = parser.parse_args(argv)
    if args.command == "extract":
        ok, payload = extract_media_result(
            args.path,
            password=args.password,
            ocr=args.ocr,
            validate=not args.no_validate,
            schema_path=args.schema,
            out_format=args.format,
        )
        sys.stdout.write(payload)
        return 0 if ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
