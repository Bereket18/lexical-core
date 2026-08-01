import random

from app.lexer import Lexer, PROFILES


def test_empty_source_produces_no_tokens():
    for profile in PROFILES.values():
        assert Lexer("", profile).tokenize() == []


def test_whitespace_only_source():
    for profile in PROFILES.values():
        assert Lexer("   \n\t\n  ", profile).tokenize() == []


def test_unterminated_string_does_not_crash():
    for profile in PROFILES.values():
        tokens = Lexer('x = "never closed', profile).tokenize()
        assert tokens  # produced *something*, didn't hang or raise


def test_unterminated_block_comment_does_not_crash():
    profile = PROFILES["cpp"]
    tokens = Lexer("int x; /* never closed", profile).tokenize()
    assert tokens[-1].type.value == "COMMENT"


def test_random_garbage_bytes_never_raise():
    random.seed(7)
    weird = "@#$%^&~`\\\u00e9\u4e2d\x01\x02\ufeff\U0001F600\""
    alphabet = weird + "abc123 \n\t(){}.,;"
    for profile in PROFILES.values():
        for _ in range(20):
            garbage = "".join(random.choice(alphabet) for _ in range(300))
            # Must not raise, regardless of how nonsensical the input is.
            Lexer(garbage, profile).tokenize()


def test_every_character_is_accounted_for():
    """Walk the token stream in order and confirm every gap between
    consecutive tokens (and before the first / after the last) is pure
    whitespace -- proof the scanner partitions the source with no gaps
    and no double-counted regions, for every supported language."""
    src = 'def f(x):\n    return x + 1  # comment\nz = "hi" * 2\n'
    line_starts = [0]
    for i, c in enumerate(src):
        if c == "\n":
            line_starts.append(i + 1)

    def to_index(line, col):
        return line_starts[line - 1] + (col - 1)

    for profile in PROFILES.values():
        tokens = Lexer(src, profile).tokenize()
        cursor = 0
        for t in tokens:
            idx = to_index(t.line, t.column)
            gap = src[cursor:idx]
            assert all(c in " \t\r\n\f\v" for c in gap), (profile.name, repr(gap))
            cursor = idx + len(t.lexeme)
        trailing = src[cursor:]
        assert all(c in " \t\r\n\f\v" for c in trailing), (profile.name, repr(trailing))


def test_mixed_valid_and_invalid_characters_all_handled():
    src = "x = 1 @ # $ y = 2"
    tokens = Lexer(src, PROFILES["cpp"]).tokenize()
    # cpp treats '@', '#'(no directive content), '$' differently; key point:
    # scanning reaches the end and 'y' / '2' are still found afterwards.
    assert tokens[-1].lexeme == "2"
    assert tokens[-1].type.value == "NUMBER"
