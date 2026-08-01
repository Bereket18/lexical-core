"""C++ lexical profile (core language; not a full preprocessor)."""
from .base import LanguageProfile

KEYWORDS = frozenset(
    {
        "alignas", "alignof", "and", "asm", "auto", "bool", "break", "case",
        "catch", "char", "char16_t", "char32_t", "class", "const",
        "constexpr", "const_cast", "continue", "decltype", "default",
        "delete", "do", "double", "dynamic_cast", "else", "enum", "explicit",
        "export", "extern", "false", "final", "float", "for", "friend",
        "goto", "if", "inline", "int", "long", "mutable", "namespace", "new",
        "noexcept", "not", "nullptr", "operator", "or", "override", "private",
        "protected", "public", "register", "reinterpret_cast", "return",
        "short", "signed", "sizeof", "static", "static_assert", "static_cast",
        "struct", "switch", "template", "this", "thread_local", "throw",
        "true", "try", "typedef", "typeid", "typename", "union", "unsigned",
        "using", "virtual", "void", "volatile", "wchar_t", "while",
    }
)

OPERATORS = (
    "<<=", ">>=", "->*", "...",
    "::", "->", "++", "--", "&&", "||", "==", "!=", "<=", ">=", "<<", ">>",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", "^", "~", "?",
)

DELIMITERS = frozenset({"(", ")", "[", "]", "{", "}", ",", ":", ".", ";"})

CPP = LanguageProfile(
    name="cpp",
    keywords=KEYWORDS,
    operators=OPERATORS,
    delimiters=DELIMITERS,
    line_comment="//",
    block_comment=("/*", "*/"),
    preprocessor_prefix="#",
    string_quotes=("'", '"'),
    triple_quotes=(),
)
