#!/usr/bin/env python3
"""Cosmos 3 Super Reasoner hello-world on Token Factory. See ROADMAP §5.4."""

import sys

from apprentice.cli import main

if __name__ == "__main__":
    argv = ["hello-reasoner", *sys.argv[1:]]
    raise SystemExit(main(argv))
