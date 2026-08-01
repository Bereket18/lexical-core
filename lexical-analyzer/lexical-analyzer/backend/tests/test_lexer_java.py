from app.lexer import Lexer, PROFILES

JAVA = PROFILES["java"]


def tokenize(src, **kw):
    return Lexer(src, JAVA, **kw).tokenize()


def test_annotation_at_symbol_is_a_delimiter_in_java():
    # Contrast again: '@' is neither an operator (Python) nor an error
    # (C++) in Java -- it's a delimiter introducing an annotation.
    tokens = tokenize("@Override\npublic void run() {}")
    at_token = tokens[0]
    assert at_token.lexeme == "@"
    assert at_token.type.value == "DELIMITER"
    assert all(t.type.value != "ERROR" for t in tokens)


def test_unsigned_right_shift_maximal_munch():
    tokens = tokenize("int x = a >>> b;")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert ">>>" in ops
    assert ">>" not in ops
    assert ">" not in ops


def test_hex_literal_and_string_concatenation():
    tokens = tokenize('int x = 0x1F; String s = "v: " + x;')
    nums = [t.lexeme for t in tokens if t.type.value == "NUMBER"]
    strs = [t.lexeme for t in tokens if t.type.value == "STRING"]
    assert nums == ["0x1F"]
    assert strs == ['"v: "']


def test_keyword_set_includes_modern_java():
    tokens = tokenize("var x = 1; record Point(int x, int y) {}")
    keywords = [t.lexeme for t in tokens if t.type.value == "KEYWORD"]
    assert "var" in keywords
    assert "record" in keywords
