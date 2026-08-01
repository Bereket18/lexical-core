"""The scanning engine.

This file is written once and is language-agnostic: it never special-cases
Python, C++, Java, or JavaScript by name. Everything language-specific is
read from the LanguageProfile passed into the constructor. This is what
lets one well-tested algorithm serve every supported language, and what
makes adding a fifth language a one-file change (see languages/__init__.py).

Core algorithm at every position, in priority order:
    1. whitespace             -> skip, track line/column
    2. line comment           -> consume to end of line
    3. block comment          -> consume to closing marker (or EOF)
    4. preprocessor directive -> consume to end of line (honors trailing
                                  backslash-newline continuation, as in
                                  multi-line #define macros)
    5. triple-quoted string   -> consume to closing marker (or EOF)
    6. quoted string          -> consume to closing quote (or end of line)
    7. number literal         -> longest valid numeric literal
    8. identifier / keyword   -> longest identifier, then keyword lookup
    9. operator                -> longest matching operator (maximal munch)
   10. delimiter                -> single matching punctuation character
   11. anything else            -> ERROR token of length 1, then continue

Step 11 is the contract that guarantees the engine never crashes: every
character in the input is consumed by exactly one of these eleven rules, so
the loop always terminates having classified the entire source.
"""
from __future__ import annotations

import re

from .languages.base import LanguageProfile
from .token_types import Token, TokenType

# One generic numeric-literal grammar shared by every language profile.
# Alternatives are ordered so the more specific pattern is tried first --
# Python's `re` module returns the first alternative that matches at a
# position, not the longest, so ordering here is load-bearing:
#   1. radix-prefixed integers (0x.., 0b.., 0o..)
#   2. digits '.' digits  (with optional exponent)   e.g. 3.14, 3.14e-10
#   3. '.' digits         (with optional exponent)   e.g. .5
#   4. digits             (with optional exponent)   e.g. 42, 1_000, 6e23
NUMBER_RE = re.compile(
    r"""
    0[xX][0-9a-fA-F_]+
    | 0[bB][01_]+
    | 0[oO][0-7_]+
    | \d[\d_]*\.\d[\d_]*(?:[eE][+-]?\d+)?
    | \.\d[\d_]*(?:[eE][+-]?\d+)?
    | \d[\d_]*(?:[eE][+-]?\d+)?
    """,
    re.VERBOSE,
)


class Lexer:
    """Tokenizes `source` according to `profile`.

    skip_comments: if True, COMMENT tokens are discarded instead of being
    emitted (mirroring how whitespace is always discarded). Strings are
    always emitted as STRING tokens -- they carry semantic content that
    whitespace and comments don't.
    """

    def __init__(self, source: str, profile: LanguageProfile, skip_comments: bool = False):
        self.source = source
        self.profile = profile
        self.skip_comments = skip_comments
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source)
        self.tokens: list[Token] = []
        # True only when nothing but whitespace has been seen since the
        # last newline (or the start of the file). A '#' is only a
        # preprocessor directive when it's the first thing on its line --
        # `x = 1 # not a directive` must not swallow the rest of the line.
        self.at_line_start = True

    # -- low-level cursor helpers -----------------------------------------

    def _advance(self, n: int = 1) -> None:
        """Move the cursor forward n characters, keeping line/column exact."""
        end = min(self.pos + n, self.length)
        while self.pos < end:
            ch = self.source[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

    # -- the main loop ------------------------------------------------------

    def tokenize(self) -> list[Token]:
        while self.pos < self.length:
            ch = self.source[self.pos]

            # 1. whitespace -- skipped, but still advances line/column
            if ch in " \t\r\n\f\v":
                if ch == "\n":
                    self.at_line_start = True
                self._advance()
                continue

            start_line, start_col = self.line, self.column
            # Capture line-start status for THIS token, then reset it --
            # whatever we consume below is non-whitespace, so by definition
            # we're no longer at the start of the line for anything after it.
            at_line_start = self.at_line_start
            self.at_line_start = False

            # 2. line comment
            lc = self.profile.line_comment
            if lc and self.source.startswith(lc, self.pos):
                self._consume_line_comment(lc, start_line, start_col)
                continue

            # 3. block comment
            bc = self.profile.block_comment
            if bc and self.source.startswith(bc[0], self.pos):
                self._consume_block_comment(bc, start_line, start_col)
                continue

            # 4. preprocessor directive (e.g. #include, #define in C/C++) --
            #    only at the true start of a line, optionally after whitespace
            pp = self.profile.preprocessor_prefix
            if pp and at_line_start and self.source.startswith(pp, self.pos):
                self._consume_preprocessor(start_line, start_col)
                continue

            # 5. triple-quoted string (checked before single-quote strings
            #    so a leading triple-quote is never mistaken for an empty
            #    string followed by a stray quote)
            triple = self._match_prefix(self.profile.triple_quotes)
            if triple:
                self._consume_delimited(triple, triple, start_line, start_col, TokenType.STRING)
                continue

            # 6. quoted string
            if ch in self.profile.string_quotes:
                self._consume_string(ch, start_line, start_col)
                continue

            # 7. number
            m = NUMBER_RE.match(self.source, self.pos)
            if m:
                lexeme = m.group(0)
                self._advance(len(lexeme))
                self.tokens.append(Token(TokenType.NUMBER, lexeme, start_line, start_col))
                continue

            # 8. identifier / keyword
            if self.profile.identifier_start.match(ch):
                self._consume_identifier(start_line, start_col)
                continue

            # 9. operator (profile.operators is sorted longest-first, so
            #    this loop naturally implements maximal munch: "==" wins
            #    over "=", "**=" wins over "**" wins over "*", etc.)
            matched_op = self._match_prefix(self.profile.operators)
            if matched_op:
                self._advance(len(matched_op))
                self.tokens.append(Token(TokenType.OPERATOR, matched_op, start_line, start_col))
                continue

            # 10. delimiter
            if ch in self.profile.delimiters:
                self._advance()
                self.tokens.append(Token(TokenType.DELIMITER, ch, start_line, start_col))
                continue

            # 11. anything else: never crash. Emit one ERROR token for the
            #     single offending character and keep scanning from the
            #     very next character.
            self._advance()
            self.tokens.append(Token(TokenType.ERROR, ch, start_line, start_col))

        return self.tokens

    # -- helpers --------------------------------------------------------

    def _match_prefix(self, candidates: tuple) -> str | None:
        """Return the first candidate (already longest-first) starting at
        the cursor, or None. Used for both operators and triple-quotes."""
        for candidate in candidates:
            if self.source.startswith(candidate, self.pos):
                return candidate
        return None

    def _consume_preprocessor(self, line: int, col: int) -> None:
        """Consume a preprocessor directive (#include, #define, ...) to the
        end of the logical line. A trailing backslash immediately before a
        newline continues the directive onto the next physical line, which
        is how multi-line #define macros are written in real C/C++ code."""
        start = self.pos
        while self.pos < self.length:
            if self.source[self.pos] == "\n":
                break
            if self.source[self.pos] == "\\" and self.source.startswith("\\\n", self.pos):
                self._advance(2)  # skip the backslash-newline, keep consuming
                continue
            if self.source[self.pos] == "\\" and self.source.startswith("\\\r\n", self.pos):
                self._advance(3)
                continue
            self._advance()
        lexeme = self.source[start:self.pos]
        self.tokens.append(Token(TokenType.PREPROCESSOR, lexeme, line, col))

    def _consume_line_comment(self, marker: str, line: int, col: int) -> None:
        start = self.pos
        self._advance(len(marker))
        while self.pos < self.length and self.source[self.pos] != "\n":
            self._advance()
        if not self.skip_comments:
            lexeme = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.COMMENT, lexeme, line, col))

    def _consume_block_comment(self, markers: tuple, line: int, col: int) -> None:
        start_marker, end_marker = markers
        start = self.pos
        self._advance(len(start_marker))
        # Gracefully handle an unterminated block comment: just run to EOF
        # instead of raising. This is exactly the kind of malformed input
        # the "never crash" requirement is testing for.
        while self.pos < self.length and not self.source.startswith(end_marker, self.pos):
            self._advance()
        if self.pos < self.length:
            self._advance(len(end_marker))
        if not self.skip_comments:
            lexeme = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.COMMENT, lexeme, line, col))

    def _consume_delimited(self, start_marker: str, end_marker: str, line: int, col: int, ttype: TokenType) -> None:
        """Consume a triple-quoted (or otherwise multi-char-delimited)
        literal, honoring backslash escapes, up to the closing marker or
        EOF -- whichever comes first."""
        start = self.pos
        self._advance(len(start_marker))
        while self.pos < self.length and not self.source.startswith(end_marker, self.pos):
            if self.source[self.pos] == "\\" and self.pos + 1 < self.length:
                self._advance(2)
            else:
                self._advance()
        if self.pos < self.length:
            self._advance(len(end_marker))
        lexeme = self.source[start:self.pos]
        self.tokens.append(Token(ttype, lexeme, line, col))

    def _consume_string(self, quote: str, line: int, col: int) -> None:
        start = self.pos
        self._advance()  # opening quote
        while self.pos < self.length:
            ch = self.source[self.pos]
            if ch == "\\" and self.pos + 1 < self.length:
                self._advance(2)
                continue
            if ch == quote:
                self._advance()
                break
            if ch == "\n":
                # Unterminated single-line string: stop here rather than
                # swallowing the rest of the file. Never crash.
                break
            self._advance()
        lexeme = self.source[start:self.pos]
        self.tokens.append(Token(TokenType.STRING, lexeme, line, col))

    def _consume_identifier(self, line: int, col: int) -> None:
        start = self.pos
        self._advance()
        while self.pos < self.length and self.profile.identifier_continue.match(self.source[self.pos]):
            self._advance()
        lexeme = self.source[start:self.pos]
        ttype = TokenType.KEYWORD if lexeme in self.profile.keywords else TokenType.IDENTIFIER
        self.tokens.append(Token(ttype, lexeme, line, col))
