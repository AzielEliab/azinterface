"""cite.json names AZCoherence and Plain A–Z peers."""

from azinterface.cite import cite_document


def test_cite_names_azcoherence_and_plain_peers() -> None:
    cite = cite_document()
    assert cite["author"] == "Aziel Eliab"
    assert cite["identity"] == "Aziel Eliab only"
    assert cite["azcoherence_slug"] == "azcoherence"
    assert "azcoherence" in cite["azcoherence"].lower()
    assert "azcoherence-download-tracker" in cite["azcoherence_worker"]
    assert cite["azcoherence_download"].endswith("/download")
    assert "azcoherence" in cite["note"]
    assert "FragGate is THE single door" in cite["note"]
    names = [p["name"] for p in cite["peers"]]
    assert names == ["AZ-CLCE", "AZCoherence", "AZHub"]
    assert all(p["bucket"] == "plain" for p in cite["peers"])
    coherence = next(p for p in cite["peers"] if p["slug"] == "azcoherence")
    assert coherence["spec"] == "AZC-WP-0.1"
    assert coherence["not"] == "AKM-TRIAD"
    assert "fraggate/describe?slug=azcoherence" in coherence["fraggate_describe"]
    assert "fraggate/call" in coherence["fraggate_call"]
    assert "plain A–Z" in cite["sort_law"]
    assert cite["catalog_software"].endswith("/v1/software")
