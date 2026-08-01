"""Registry of all supported language profiles.

Adding a new language: write a new `*_profile.py` module exporting a
`LanguageProfile` instance, then add one line here. Nothing else in the
codebase needs to change.
"""
from .python_profile import PYTHON
from .cpp_profile import CPP
from .java_profile import JAVA
from .javascript_profile import JAVASCRIPT

PROFILES = {
    "python": PYTHON,
    "cpp": CPP,
    "java": JAVA,
    "javascript": JAVASCRIPT,
}

__all__ = ["PROFILES", "PYTHON", "CPP", "JAVA", "JAVASCRIPT"]
