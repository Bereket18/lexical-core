"""API tests.

These exercise the actual HTTP endpoints via FastAPI's TestClient, on top
of (not instead of) the unit tests for the lexer itself. Requires the full
requirements.txt to be installed -- run `pip install -r requirements.txt`
first if these fail to import.
"""
import io

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")
TestClient = fastapi_testclient.TestClient

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_languages_endpoint_lists_all_four():
    resp = client.get("/languages")
    assert resp.status_code == 200
    assert set(resp.json()["supported"]) == {"python", "cpp", "java", "javascript"}


def test_tokenize_explicit_language():
    resp = client.post(
        "/tokenize",
        json={"source": "x = 1 + 2", "language": "python"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["language"] == "python"
    assert body["error_count"] == 0
    assert [t["token_type"] for t in body["tokens"]] == [
        "IDENTIFIER", "OPERATOR", "NUMBER", "OPERATOR", "NUMBER",
    ]


def test_tokenize_auto_detect():
    resp = client.post(
        "/tokenize",
        json={"source": '#include <iostream>\nint main(){return 0;}', "language": "auto"},
    )
    assert resp.status_code == 200
    assert resp.json()["language"] == "cpp"


def test_tokenize_never_errors_on_garbage():
    resp = client.post("/tokenize", json={"source": "@@@###$$$```", "language": "python"})
    assert resp.status_code == 200  # the API must not 500, even on garbage


def test_tokenize_empty_source():
    resp = client.post("/tokenize", json={"source": "", "language": "python"})
    assert resp.status_code == 200
    assert resp.json()["token_count"] == 0


def test_tokenize_file_txt_upload():
    content = b"int x = 42;\n"
    resp = client.post(
        "/tokenize-file",
        files={"file": ("snippet.cpp", io.BytesIO(content), "text/plain")},
        data={"language": "auto"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["language"] == "cpp"
    assert body["source"] == "int x = 42;\n"


def test_tokenize_file_corrupt_docx_returns_400_not_500():
    resp = client.post(
        "/tokenize-file",
        files={"file": ("bad.docx", io.BytesIO(b"not a real docx"), "application/octet-stream")},
        data={"language": "auto"},
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


def test_tokenize_file_real_docx_roundtrip():
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.add_paragraph("def add(a, b):")
    doc.add_paragraph("    return a + b")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    resp = client.post(
        "/tokenize-file",
        files={"file": ("snippet.docx", buf, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={"language": "python"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["error_count"] == 0
    assert "def" in [t["lexeme"] for t in body["tokens"]]
