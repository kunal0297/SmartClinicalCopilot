"""Pytest configuration for the backend test suite.

Ensures the ``backend`` package directory is importable so the tests can use
bare imports (``from trie_engine import TrieEngine``) and provides a safe,
self-contained default environment (SQLite, no external services).
"""

import os
import sys

# Make the backend directory importable for bare-name imports in tests.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Default to a throwaway SQLite database for tests.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")
os.environ.setdefault("ENVIRONMENT", "test")

# The app resolves the rules directory and demo_patients.json relative to the
# current working directory, so run tests from the project root.
os.chdir(REPO_ROOT)
