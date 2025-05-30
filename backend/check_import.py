import sys
import os

print("DEBUG: check_import.py started")
try:
    # Add the parent directory to sys.path to allow relative imports
    # Assuming the script is at /app/backend/check_import.py and backend package is at /app/backend
    # We need to add /app to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    print(f"DEBUG: sys.path updated: {sys.path}")

    from backend import app
    print("DEBUG: Successfully imported backend.app")
except ImportError as e:
    print(f"DEBUG: ImportError: {e}")
except Exception as e:
    print(f"DEBUG: An unexpected error occurred during import: {e}")

print("DEBUG: check_import.py finished") 