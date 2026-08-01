# Demo Script (≈4–5 minutes)

A suggested run-through for the live demo / recorded video deliverable.

1. **Open with the gap, not the tool.** "Most lexical analyzers only handle
   one language. We were told the hidden test set spans *multiple*
   languages, so ours auto-detects Python, C++, Java, and JavaScript and
   switches grammars automatically."

2. **Show the architecture diagram** (`docs/` or the README) for ~20
   seconds: frontend ↔ backend ↔ file handler ↔ lexical engine.

3. **Live: paste Python code**, leave language on "Auto-detect", hit
   Convert.
   - Point out the **detected: python** label.
   - Point out **live syntax highlighting** in the editor matching the
     results table.
   - Scroll the results table: Lexeme / Token Type / Line / Column.

4. **Live: switch to C++ via "Load sample"**, hit Convert again.
   - Point out `#include <iostream>` becomes one clean `PREPROCESSOR`
     token, not three `ERROR` tokens — call out that this was a real bug
     you caught and fixed during testing (judges love hearing about a
     caught bug more than a clean success story).

5. **Live: type garbage into the editor** — e.g. `int x = \`@#;` — hit
   Convert.
   - Show the `ERROR` tokens highlighted in red, and that the app keeps
     running. "Never crashes" isn't a slide, it's a live demonstration.

6. **Live: upload a `.docx` file** containing a code snippet.
   - Show the extracted text appearing in the editor, then the token
     table populating from it.

7. **Close with the test suite.** Run `pytest -v` on screen for 10
   seconds — a green run across 35+ tests covering all four languages,
   line/column tracking, and crash-resistance is worth more than any
   slide claiming "high accuracy."

8. **One sentence on architecture.** "The scanner itself never changes
   between languages — only the data profile it's given does. Adding a
   fifth language is a one-file change, not a rewrite."
