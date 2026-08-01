from app.lexer import Lexer, PROFILES

CPP = PROFILES["cpp"]


def tokenize(src, **kw):
    return Lexer(src, CPP, **kw).tokenize()


def test_preprocessor_directive_is_not_an_error():
    tokens = tokenize('#include <iostream>\nint x = 0;')
    assert tokens[0].type.value == "PREPROCESSOR"
    assert tokens[0].lexeme == "#include <iostream>"
    assert all(t.type.value != "ERROR" for t in tokens)


def test_multiline_define_with_continuation():
    src = "#define MAX(a, b) \\\n    ((a) > (b) ? (a) : (b))\nint y;"
    tokens = tokenize(src)
    directive = tokens[0]
    assert directive.type.value == "PREPROCESSOR"
    assert "MAX" in directive.lexeme and "((a) > (b)" in directive.lexeme
    # the line after the (2-line) directive must report line 3 correctly
    y_token = [t for t in tokens if t.lexeme == "y"][0]
    assert y_token.line == 3


def test_scope_resolution_and_arrow_operators():
    tokens = tokenize("std::cout; ptr->field; a <=> b;")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert "::" in ops
    assert "->" in ops


def test_block_comment():
    tokens = tokenize("int x; /* multi\nline comment */ int y;")
    comments = [t for t in tokens if t.type.value == "COMMENT"]
    assert len(comments) == 1
    assert "multi" in comments[0].lexeme and "line comment" in comments[0].lexeme


def test_at_symbol_is_an_error_in_cpp():
    # Contrast with Python, where '@' is a valid operator. Same character,
    # different classification -- driven entirely by the language profile.
    tokens = tokenize("int x = @;")
    errors = [t for t in tokens if t.type.value == "ERROR"]
    assert len(errors) == 1
    assert errors[0].lexeme == "@"


def test_increment_decrement_not_split():
    tokens = tokenize("x++; y--;")
    ops = [t.lexeme for t in tokens if t.type.value == "OPERATOR"]
    assert ops == ["++", "--"]
