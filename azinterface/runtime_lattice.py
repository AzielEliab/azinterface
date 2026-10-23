"""Runtime dual-lattice parity (AZRT-DUAL-LATTICE-1.0), additive.

These recompute the aziel-runtime lattice rules byte for byte so AZInterface
can check a runtime receipt offline. ``azinterface.receipts`` keeps its own
single-chain formula unchanged; this module does not replace it.
Same rules and the same 3 pinned vectors as AZ-OS ``azos/runtime_lattice.py``.

    primary           = H(canon({document, prev}))
    offline secondary = H(canon({primary: document_hash, username}))
    online secondary  = H(canon({offline: false, prev, primary}))
    tiebreak.hash     = H(canon({chain: "tiebreak", prev, primary, secondary, username}))

The tiebreak helper is optional and additive. It does not replace primary or
secondary. Key order after canonical sort is chain, prev, primary, secondary,
username. H is SHA-256 of that UTF-8 JSON.

Sealed, not signed. Not marked live.

Author: Aziel Eliab.
"""

from __future__ import annotations

from azinterface.receipts import ZERO as GENESIS, canon, sha256_text

SPEC = "AZRT-DUAL-LATTICE-1.0"
TIEBREAK_SPEC = "LATTICE-TIEBREAK-1.0"


def runtime_primary(document_hash: str, prev: str | None = None) -> str:
    return sha256_text(canon({"document": document_hash, "prev": prev or GENESIS}))


def runtime_offline_secondary(document_hash: str, username: str) -> str:
    return sha256_text(canon({"primary": document_hash, "username": str(username)}))


def runtime_online_secondary(primary: str, prev: str | None = None) -> str:
    return sha256_text(canon({"offline": False, "prev": prev or GENESIS, "primary": primary}))


def runtime_tiebreak(prev: str | None, primary: str, secondary: str, username: str) -> str:
    """Optional third chain. Hash the tiebreak object as given."""
    return sha256_text(
        canon(
            {
                "chain": "tiebreak",
                "prev": prev or GENESIS,
                "primary": primary,
                "secondary": secondary,
                "username": str(username),
            }
        )
    )
