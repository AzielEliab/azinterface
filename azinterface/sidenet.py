"""Parallel side-net entry for a signed AZInterface update.

This is the connectivity call. It uses the same adopt path as app open and
``azinterface update``. It does not open a radio, does not GET the public mesh,
and does not treat membership flags as delivery. Paid satellite relay stays HELD.

Author: Aziel Eliab. SPDX-License-Identifier: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

SPEC = "AZINTERFACE-SIDENET-1.0"


def signed_update(root: Path | str, *, hooks: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Run the signed update check. Carrier hardware stays absent."""
    from azinterface.update_apply import on_connectivity

    result = on_connectivity(root, hooks)
    result["sidenet"] = SPEC
    result["radio_phy"] = False
    result["second_device"] = False
    result["hardware"] = False
    result["satellite_relay"] = "HELD"
    result["membership_only"] = True
    result["live"] = False
    result["booted"] = False
    result["carriers_present"] = []
    return result


def status(root: Path | str) -> dict[str, Any]:
    """Read-only. Does not apply and does not fetch."""
    from azinterface.update_apply import trust_view

    view = trust_view(root)
    view["sidenet"] = SPEC
    view["radio_phy"] = False
    view["second_device"] = False
    view["hardware"] = False
    view["satellite_relay"] = "HELD"
    view["membership_only"] = True
    view["live"] = False
    view["carriers_present"] = []
    return view
