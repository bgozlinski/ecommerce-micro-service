import os
import sys


def _ensure_project_root_on_syspath():
    """
    Ensure the Product Catalog service root (containing the `app` package)
    is present on sys.path so imports like `from app.main import app` work
    regardless of how pytest/poetry initializes sys.path.
    """
    # tests/ -> service_root = parent directory
    service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if service_root not in sys.path:
        sys.path.insert(0, service_root)


_ensure_project_root_on_syspath()
