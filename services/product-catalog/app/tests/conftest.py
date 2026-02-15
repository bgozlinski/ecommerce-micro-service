import os
import sys


def _ensure_project_root_on_syspath():
    # tests/ -> service root is the parent directory
    service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if service_root not in sys.path:
        sys.path.insert(0, service_root)


_ensure_project_root_on_syspath()
