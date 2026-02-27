import subprocess
from pathlib import Path
import argparse

def _find_all_docker_files() -> list[Path]:
    services_root = Path('../services')
    infrastructure_root = Path('../infrastructure')
    frontend_root = Path('../frontend')
    docker_files = []

    if infrastructure_root.is_dir():
        docker_files.append(infrastructure_root)

    for service_path in services_root.iterdir():
        if service_path.is_dir() and not service_path.name.startswith('.'):
            docker_files.append(service_path)

    if frontend_root.is_dir():
        docker_files.append(frontend_root)

    return docker_files

def run_containers():
    docker_files = _find_all_docker_files()
    for docker_file in docker_files:
        print(f"Starting container from {docker_file}")
        subprocess.run(["docker-compose", "up", "-d", "--build"], cwd=docker_file, capture_output=False)
        print()

def stop_containers():
    docker_files = _find_all_docker_files()
    for docker_file in reversed(docker_files):
        print(f"Stopping container from {docker_file}")
        subprocess.run(["docker-compose", "down"], cwd=docker_file, capture_output=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--up', action='store_true')
    parser.add_argument('--down', action='store_true')
    parser.add_argument('--restart', action='store_true')

    args = parser.parse_args()

    if args.restart:
        stop_containers()
        run_containers()
    elif args.up:
        run_containers()
    elif args.down:
        stop_containers()
    else:
        parser.print_help()
