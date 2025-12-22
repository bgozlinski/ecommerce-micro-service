import subprocess
import sys
from pathlib import Path



def find_service_dirs() -> list[str]:
    root = Path('../services')
    service_dirs = []

    for service_path in root.iterdir():
        if service_path.is_dir() and not service_path.name.startswith('.'):
            if (service_path / 'pyproject.toml').exists():
                if (service_path / 'tests').exists():
                    service_dirs.append(str(service_path))

    return service_dirs


def run_test():
    service_dirs = find_service_dirs()

    for test_dir in service_dirs:
        print(f"Running tests in {test_dir}")
        subprocess.run(["poetry", "run", "pytest", '-v'], cwd=test_dir, capture_output=False)
        print()

if __name__ == "__main__":
    run_test()