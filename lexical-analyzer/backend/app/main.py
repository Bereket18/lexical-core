"""FastAPI application: the backend half of frontend <-> backend <-> file
handler.

Two endpoints do all the work:
    POST /tokenize       - JSON body {source, language, skip_comments}
    POST /tokenize-file   - multipart file upload (+ optional language)

Both funnel into the same `_run_lexer` helper, which is the only place that
talks to the lexer package, so the two endpoints can never drift out of sync
with each other.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .file_handler import FileExtractionError, extract_text
from .lexer import PROFILES, Lexer, detect_language

app = FastAPI(
    title="Lexical Analyzer API",
    description="Tokenizes source code across multiple languages with line/column tracking.",
    version="1.0.0",
)

# Local development CORS: wide open so the static frontend (opened straight
# from disk, or served by any dev server) can call this API without setup
# friction. Tighten allow_origins before deploying this anywhere public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenizeRequest(BaseModel):
    source: str = Field(..., description="Raw source code to tokenize")
    language: str = Field(
        "auto",
        description="One of 'auto', 'python', 'cpp', 'java', 'javascript'",
    )
    skip_comments: bool = Field(
        False, description="If true, COMMENT tokens are discarded rather than returned"
    )


class TokenOut(BaseModel):
    lexeme: str
    token_type: str
    line: int
    column: int


class TokenizeResponse(BaseModel):
    language: str
    token_count: int
    error_count: int
    tokens: List[TokenOut]
    source: Optional[str] = None  # echoed back so the frontend can display
    # exactly what was tokenized -- most useful after a .docx extraction,
    # where the user has no other way to see what text was pulled out.


def _run_lexer(
    source: str,
    language: str,
    skip_comments: bool,
    filename: Optional[str] = None,
) -> TokenizeResponse:
    if language == "auto" or language not in PROFILES:
        language = detect_language(source, filename)
    profile = PROFILES[language]
    tokens = Lexer(source, profile, skip_comments=skip_comments).tokenize()
    error_count = sum(1 for t in tokens if t.type.value == "ERROR")
    return TokenizeResponse(
        language=language,
        token_count=len(tokens),
        error_count=error_count,
        tokens=[TokenOut(**t.to_dict()) for t in tokens],
        source=source,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/languages")
def languages():
    return {"supported": sorted(PROFILES.keys())}


@app.post("/tokenize", response_model=TokenizeResponse)
def tokenize(req: TokenizeRequest):
    if req.source == "":
        # Empty input is not an error -- it just has zero tokens. Don't
        # punish the user with an HTTP error for clearing the editor.
        return _run_lexer("", req.language, req.skip_comments)
    return _run_lexer(req.source, req.language, req.skip_comments)


@app.post("/tokenize-file", response_model=TokenizeResponse)
async def tokenize_file(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    skip_comments: bool = Form(False),
):
    raw = await file.read()
    try:
        text = extract_text(file.filename, raw)
    except FileExtractionError as exc:
        # File handler errors are real user errors (bad/corrupt file), not
        # server bugs -- a clean 400 with a message, never a 500 or crash.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _run_lexer(text, language, skip_comments, filename=file.filename)
