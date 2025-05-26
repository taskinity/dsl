#!/usr/bin/env python3

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import and run the CLI
from dialogchain.cli import main

if __name__ == "__main__":
    sys.exit(main())
