from app.lexer import Lexer, PROFILES

PY = PROFILES["python"]


def tokenize(src, **kw):
    return Lexer(src, PY, **kw).tokenize()


def types(tokens):
    return [t.type.value for t in tokens]


def lexemes(tokens):
    return [t.lexeme for t in tokens]


def test_keywords_recognized():
    tokens = tokenize("if x and y: return False")
    assert "KEYWORD" in types(tokens)
    keyword_lexemes = [t.lexeme for t in tokens if t.type.value == "KEYWORD"]
    assert keyword_lexemes == ["if", "and", "return", "False"]


def test_identifiers_vs_keywords():
    # "iffy" must not be mistaken for the keyword "if"
    tokens = tokenize("iffy = 1")
    assert tokens[0].type.value == "IDENTIFIER"
    assert tokens[0].lexeme == "iffy"


def test_operators_maximal_munch():
    tokens = tokenize("a **= b // c == d")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert ops == ["**=", "//", "=="]


def test_walrus_and_arrow_operators():
    tokens = tokenize("if (n := len(a)) > 0: pass")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert ":=" in ops
    assert ">" in ops


def test_numbers_all_forms():
    tokens = tokenize("1 3.14 .5 1_000 0x1F 0b101 0o17 6.022e23")
    nums = [t.lexeme for t in tokens if t.type.value == "NUMBER"]
    assert nums == ["1", "3.14", ".5", "1_000", "0x1F", "0b101", "0o17", "6.022e23"]


def test_delimiters():
    tokens = tokenize("f(a, b)")
    delims = [t.lexeme for t in tokens if t.type.value == "DELIMITER"]
    assert delims == ["(", ",", ")"]


def test_string_with_escaped_quote():
    tokens = tokenize(r'x = "she said \"hi\""')
    strings = [t for t in tokens if t.type.value == "STRING"]
    assert len(strings) == 1
    assert strings[0].lexeme == r'"she said \"hi\""'


def test_triple_quoted_string_spans_lines():
    src = 'x = """line one\nline two"""\ny = 1'
    tokens = tokenize(src)
    triple = [t for t in tokens if t.type.value == "STRING"][0]
    assert "line one" in triple.lexeme and "line two" in triple.lexeme
    # token after the multi-line string must report the correct new line number
    y_token = [t for t in tokens if t.lexeme == "y"][0]
    assert y_token.line == 3


def test_comment_to_end_of_line():
    tokens = tokenize("x = 1  # trailing comment\ny = 2")
    comments = [t for t in tokens if t.type.value == "COMMENT"]
    assert comments[0].lexeme == "# trailing comment"


def test_skip_comments_flag_discards_comment_tokens():
    tokens = tokenize("x = 1  # comment", skip_comments=True)
    assert "COMMENT" not in types(tokens)


def test_error_token_for_unrecognized_character():
    tokens = tokenize("x = @")
    error = [t for t in tokens if t.type.value == "ERROR"]
    # '@' is a valid operator in Python (decorator / matmul), so it should
    # NOT be an error here -- this also verifies '@' is context-sensitive
    # across language profiles (see test_lexer_cpp.py for the contrast).
    assert error == []
    assert "@" in lexemes(tokens)


def test_truly_invalid_character_still_becomes_error():
    tokens = tokenize("x = `")
    errors = [t for t in tokens if t.type.value == "ERROR"]
    assert len(errors) == 1
    assert errors[0].lexeme == "`"


def test_line_and_column_tracking():
    src = "a = 1\nb = 2\n  c = 3"
    tokens = tokenize(src)
    positions = [(t.lexeme, t.line, t.column) for t in tokens]
    assert ("a", 1, 1) in positions
    assert ("b", 2, 1) in positions
    assert ("c", 3, 3) in positions  # two leading spaces -> column 3
