"""Initialization file for the Local Server API package."""

__version__ = "1.0.0"

# This allows for easier relative imports when treating 'src' as a package.
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))