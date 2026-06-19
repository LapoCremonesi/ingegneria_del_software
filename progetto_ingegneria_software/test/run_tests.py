#!/usr/bin/env python3
"""
Esegue tutti i test del progetto Smart Home.

Usage:
    python test/run_tests.py          # esegue tutti i test
    python test/run_tests.py -v       # modalità verbosa
    python -m unittest test/test_domain.py  # test singolo file
"""

import sys
import unittest


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.discover("test", pattern="test_*.py"))

    verbosity = 2 if "-v" in sys.argv else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
