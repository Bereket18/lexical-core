"""File handling for uploaded source files.

Per the assignment brief, uploads can be .txt, .py, .cpp, or .docx (we also
accept .java/.js/etc. for convenience, since they're handled identically to
.txt). This module's only job is: given raw bytes and a filename, return
the plain-text source. It deliberately knows nothing about tokenizing.

Robustness matters here as much as in the scanner: a corrupted .docx or a
file with stray binary bytes must produce a clean error or a best-effort
decode -- never an unhandled exception that takes the API down.
"""
from __future__ import annotations

import io

from docx import Document  # python-docx


class FileExtractionError(Exception):
    """Raised when a file genuinely cannot be turned into text."""


def extract_text(filename: str | None, raw: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".docx"):
        return _extract_docx(raw)
    return _decode_text(raw)


def _extract_docx(raw: bytes) -> str:
    try:
        document = Document(io.BytesIO(raw))
    except Exception as exc:  # python-docx raises a variety of exceptions
        raise FileExtractionError(f"not a valid .docx file ({exc})") from exc
    paragraphs = [p.text for p in document.paragraphs]
    # Tables can also hold source code pasted into a Word doc; include them.
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    paragraphs.append(cell.text)
    return "\n".join(paragraphs)


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    # Last resort: never raise -- replace undecodable bytes instead of
    # crashing the request. This keeps the "never crash" guarantee end-to-end,
    # not just inside the scanner.
    return raw.decode("utf-8", errors="replace")
