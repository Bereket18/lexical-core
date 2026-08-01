# Token Specification

This is deliverable #2: the exact rule applied for every token category,
for every supported language. The scanner (`backend/app/lexer/scanner.py`)
implements these rules generically; this document describes *what* each
rule matches, language by language.

## Scanning order (why it matters)

At every cursor position the scanner tries rules in this fixed priority
order and stops at the first match. This ordering is what makes "maximal
munch" correct -- e.g. trying `===` before `==` before `=`, or trying a
preprocessor directive before falling back to a bare `#` being an error.

| Priority | Rule | 
|---|---|
| 1 | Whitespace (skipped) |
| 2 | Line comment |
| 3 | Block comment |
| 4 | Preprocessor directive (C/C++ only, must be first token on the line) |
| 5 | Triple-quoted string (Python only) |
| 6 | Quoted string |
| 7 | Number literal |
| 8 | Identifier / keyword |
| 9 | Operator (longest match first) |
| 10 | Delimiter |
| 11 | **Anything else → `ERROR`**, consume one character, continue |

---

## NUMBER (shared across all languages)

One regular expression handles numeric literals for every language, since
the formats are nearly identical across Python/C++/Java/JavaScript:

```regex
0[xX][0-9a-fA-F_]+              # hex:      0x1F, 0xFF_FF
| 0[bB][01_]+                   # binary:   0b1010
| 0[oO][0-7_]+                  # octal:    0o17
| \d[\d_]*\.\d[\d_]*(?:[eE][+-]?\d+)?   # decimal float: 3.14, 6.022e23
| \.\d[\d_]*(?:[eE][+-]?\d+)?           # leading-dot float: .5
| \d[\d_]*(?:[eE][+-]?\d+)?             # integer (with optional exponent): 42, 1_000, 6e23
```

Alternatives are ordered most-specific-first because Python's `re` engine
returns the first matching alternative at a position, not the longest.

## IDENTIFIER / KEYWORD

- **Identifier start:** `[A-Za-z_]`
- **Identifier continue:** `[A-Za-z0-9_]*`
- A matched identifier is reclassified as `KEYWORD` if it's an exact,
  case-sensitive member of that language's reserved-word set; otherwise
  it's `IDENTIFIER`.

| Language | Keyword set size | Examples |
|---|---|---|
| Python | 37 | `def, if, elif, while, return, lambda, async, match, case` |
| C++ | 60+ | `class, template, constexpr, nullptr, static_cast, namespace` |
| Java | 50+ | `class, interface, extends, implements, synchronized, var, record` |
| JavaScript | 45+ | `function, const, let, async, await, typeof, of, get, set` |

(Full lists are in `backend/app/lexer/languages/*_profile.py` — they're
data, not logic, so extending them is a one-line change.)

## OPERATOR (maximal munch, longest-first)

Each language has its own operator table, pre-sorted longest-string-first
so the scanner always tries `===` before `==` before `=`, etc.

| Language | Sample multi-char operators (longest-first within each family) |
|---|---|
| Python | `**=  //=  ->  :=  ==  !=  <=  >=  <<  >>  **  //  +=  -=  ...` |
| C++ | `<<=  >>=  ->*  ::  ->  ++  --  &&  ||  ==  !=  <=  >=  <<  >>  ...` |
| Java | `<<=  >>=  >>>=  >>>  <<  >>  ++  --  &&  ||  ==  !=  <=  >=  ...` |
| JavaScript | `===  !==  **=  ...  =>  ??=  &&=  ||=  ?.  ??  ==  !=  &&  ||  ++  --  ...` |

`@` is a deliberate cross-language demonstration of context sensitivity:

| Language | What `@` becomes | Why |
|---|---|---|
| Python | `OPERATOR` | decorator syntax / matrix-multiply operator |
| Java | `DELIMITER` | introduces an annotation, e.g. `@Override` |
| C++, JavaScript | `ERROR` | not part of either grammar |

## STRING

- **Single/double-quoted:** scan from the opening quote to the matching
  closing quote, honoring `\` as an escape character (the escaped
  character is always consumed, even if it's the quote itself). If a raw
  newline is hit before the closing quote, the string ends there rather
  than swallowing the rest of the file (unterminated string, doesn't
  crash).
- **Triple-quoted (Python `'''`/`"""`):** same escaping rule, but newlines
  inside are allowed and don't terminate the string — only the matching
  triple-quote sequence does (or EOF, if unterminated).
- **Template literals (JavaScript `` ` ``):** treated as an ordinary quoted
  string. `${...}` interpolation is not parsed into sub-tokens — the whole
  literal, including any embedded expression, is one `STRING` token. (A
  known, documented simplification — see *Limitations* in the README.)

## COMMENT

| Language | Line comment | Block comment |
|---|---|---|
| Python | `#` | — (none) |
| C++ | `//` | `/* ... */` |
| Java | `//` | `/* ... */` |
| JavaScript | `//` | `/* ... */` |

An unterminated block comment runs to end-of-file rather than raising.

## PREPROCESSOR (C++ only — bonus category)

Any line whose first non-whitespace character is `#` is treated as a
single `PREPROCESSOR` token, e.g. `#include <iostream>`. A trailing `\`
immediately before a newline continues the directive onto the next line
(needed for realistic multi-line `#define` macros). This prevents real
C++ files — which almost always start with `#include` — from being
misclassified as full of `ERROR` tokens.

## DELIMITER

| Language | Delimiter set |
|---|---|
| Python | `( ) [ ] { } , : . ;` |
| C++ | `( ) [ ] { } , : . ;` |
| Java | `( ) [ ] { } , . ; @` |
| JavaScript | `( ) [ ] { } , . ;` |

## ERROR

Any character that doesn't satisfy any rule above — for example `` ` ``,
`$`, or `#` in a language with no preprocessor and no `#` line-comment —
becomes a single-character `ERROR` token. The scanner always advances by
exactly one character afterward, guaranteeing it terminates and never
re-reads the same invalid character twice.
