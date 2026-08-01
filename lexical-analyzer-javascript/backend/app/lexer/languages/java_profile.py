"""Java lexical profile."""
from .base import LanguageProfile

KEYWORDS = frozenset(
    {
        "abstract", "assert", "boolean", "break", "byte", "case", "catch",
        "char", "class", "const", "continue", "default", "do", "double",
        "else", "enum", "extends", "final", "finally", "float", "for",
        "goto", "if", "implements", "import", "instanceof", "int",
        "interface", "long", "native", "new", "package", "private",
        "protected", "public", "return", "short", "static", "strictfp",
        "super", "switch", "synchronized", "this", "throw", "throws",
        "transient", "try", "void", "volatile", "while", "true", "false",
        "null", "var", "record", "sealed", "yield",
    }
)

OPERATORS = (
    "<<=", ">>=", ">>>=", ">>>",
    "<<", ">>", "++", "--", "&&", "||", "==", "!=", "<=", ">=",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", "^", "~", "?", ":",
)

DELIMITERS = frozenset({"(", ")", "[", "]", "{", "}", ",", ".", ";", "@"})

JAVA = LanguageProfile(
    name="java",
    keywords=KEYWORDS,
    operators=OPERATORS,
    delimiters=DELIMITERS,
    line_comment="//",
    block_comment=("/*", "*/"),
    string_quotes=("'", '"'),
    triple_quotes=(),
)
