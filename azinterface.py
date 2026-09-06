"""Shim so `python azinterface.py` matches sibling Aziel Eliab products."""

from azinterface.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
