from . import server
from typing import Any

def main() -> Any:
    """Main entry point for the package."""
    return server.cli_main()

# Optionally expose other important items at package level
__all__ = ['main', 'server'] 