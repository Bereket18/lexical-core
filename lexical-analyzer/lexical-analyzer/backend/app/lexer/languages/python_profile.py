"""Python 3 lexical profile."""
from .base import LanguageProfile

KEYWORDS = frozenset(
    {
        "False", "None", "True", "and", "as", "assert", "async", "await",
        "break", "class", "continue", "def", "del", "elif", "else", "except",
        "finally", "for", "from", "global", "if", "import", "in", "is",
        "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
        "while", "with", "yield", "match", "case",
    }
)

# Longest-first ordering is enforced again in LanguageProfile.__post_init__,
# but listing them this way keeps the source readable.
OPERATORS = (
    "**=", "//=", ">>=", "<<=",
    "->", ":=", "==", "!=", "<=", ">=", "<<", ">>", "**", "//",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "@=",
    "+", "-", "*", "/", "%", "=", "<", ">", "&", "|", "^", "~", "@",
)

DELIMITERS = frozenset({"(", ")", "[", "]", "{", "}", ",", ":", ".", ";"})

PYTHON = LanguageProfile(
    name="python",
    keywords=KEYWORDS,
    operators=OPERATORS,
    delimiters=DELIMITERS,
    line_comment="#",
    block_comment=None,
    string_quotes=("'", '"'),
    triple_quotes=('"""', "'''"),
)
