from app.lexer import Lexer, PROFILES

JS = PROFILES["javascript"]


def tokenize(src, **kw):
    return Lexer(src, JS, **kw).tokenize()


def test_strict_equality_maximal_munch():
    tokens = tokenize("a === b !== c")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert ops == ["===", "!=="]


def test_arrow_function_and_nullish_coalescing():
    tokens = tokenize("const f = (x) => x ?? 0;")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert "=>" in ops
    assert "??" in ops


def test_optional_chaining_not_split_into_question_and_dot():
    tokens = tokenize("a?.b")
    ops_and_delims = [t.lexeme for t in tokens if t.type.value in ("OPERATOR", "DELIMITER")]
    assert "?." in ops_and_delims
    assert "?" not in ops_and_delims


def test_template_literal_is_a_single_string_token():
    tokens = tokenize("let msg = `hello ${name}!`;")
    strings = [t for t in tokens if t.type.value == "STRING"]
    assert len(strings) == 1
    assert strings[0].lexeme == "`hello ${name}!`"


def test_spread_operator():
    tokens = tokenize("f(...args)")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert "..." in ops
