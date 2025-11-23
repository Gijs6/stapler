import argparse
import sys

from colorama import init

from .config import load_config
from .core.engine import build_site
from .server import serve

init()


def main():
    parser = argparse.ArgumentParser(
        description="Stapler - A flexible static site generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="build",
        choices=["build", "serve"],
        help="Command to run (default: build)",
    )

    parser.add_argument(
        "-c",
        "--config",
        default="stapler.toml",
        help="Path to configuration file (default: stapler.toml)",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port for development server (default: 8000)",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__

        print(f"Stapler {__version__}")
        sys.exit(0)

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    if args.command == "serve":
        serve(config, args.port)
    else:
        build_site(config)


if __name__ == "__main__":
    main()
