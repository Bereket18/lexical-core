"""JavaScript (ES2020+) lexical profile."""
from .base import LanguageProfile

KEYWORDS = frozenset(
    {
        "break", "case", "catch", "class", "const", "continue", "debugger",
        "default", "delete", "do", "else", "export", "extends", "finally",
        "for", "function", "if", "import", "in", "instanceof", "let", "new",
        "return", "static", "super", "switch", "this", "throw", "try",
        "typeof", "var", "void", "while", "with", "yield", "async", "await",
        "true", "false", "null", "undefined", "of", "get", "set",
    }
)

OPERATORS = (
    "===", "!==", "**=", "...", "<<=", ">>=", ">>>=", ">>>",
    "=>", "??=", "&&=", "||=", "?.", "??",
    "==", "!=", "<=", ">=", "&&", "||", "++", "--", "**", "<<", ">>",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", "^", "~", "?", ":",
)

DELIMITERS = frozenset({"(", ")", "[", "]", "{", "}", ",", ".", ";"})

JAVASCRIPT = LanguageProfile(
    name="javascript",
    keywords=KEYWORDS,
    operators=OPERATORS,
    delimiters=DELIMITERS,
    line_comment="//",
    block_comment=("/*", "*/"),
    string_quotes=("'", '"', "`"),
    triple_quotes=(),
)
