import os
import sys

# Put backend/ (the parent of this tests/ directory) on sys.path so
# `from app... import ...` resolves no matter where pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
