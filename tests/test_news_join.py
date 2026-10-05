"""AZNews and 4DMap join only when a stored story is read back as a pin."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from azinterface.engine import Engine
from azinterface.pipeline import pipeline_arch
from azinterface.plain import human_lines
from azinterface.receipts import Ledger
from azinterface.suite import Suite
from azinterface.suite_page import suite_html
from azinterface.ui import make_server
from azinterface.web_page import home_html

STORY = {
    "headline": "Harbor notice",
    "body": "The harbor master posted a written notice about the morning tide.",
}
HONEST = {
    "4dmap": "This row is in the catalog. 4DMap can stand alone. AZNews can stand alone. A pin counts only after the same item is read back.",
    "azmail": "This row is in the catalog. Mail send does not run on the public worker.",
    "aznet": "This row is in the catalog. The packet path is not live. The alternative internet is not live. Device-to-device packet carriers stay NOT-READY. WARN-5 stands.",
    "azos": "This row is in the catalog. The public worker does not run a kernel. Boot does not run on the public worker.",
}


def _suite(tmp_path: Path) -> Suite:
    return Suite(
        refresh=False,
        vendor=tmp_path / "vendor",
        catalog=[
            {"name": "4DMap", "slug": "4dmap", "bucket": "plain", "ui_cmd": "4dmap ui", "fraggate_status": "live", "door": "fraggate"},
            {"name": "ShadowLock", "slug": "shadowlock", "bucket": "lock", "ui_cmd": "shadowlock ui", "fraggate_status": "live", "door": "fraggate"},
        ],
    )


def test_catalog_statuses_stay_honest_and_the_count_stays_33() -> None:
    cited = {
        row["slug"]: row["status"]
        for domain in pipeline_arch()["domain_map"]
        for row in domain["softwares"]
    }
    assert len(cited) == 33
    assert pipeline_arch()["software_count"] == 33
    assert "aznews" not in cited
    for slug, status in HONEST.items():
        assert cited[slug] == status
        assert "live" not in status.lower().replace("not live", "")
    cycle = Engine(Ledger()).page_cycle_status()
    assert cycle["site_state"] == "OFF"
    assert cycle["pipeline"]["software_count"] == 33


def test_news_and_map_stay_standalone_until_a_story_lands(tmp_path: Path) -> None:
    suite = _suite(tmp_path)
    linked = suite.shadow_link({"slug": "shadowlock", "label": "North desk", "input": "intake/batch"})
    assert linked["ok"] is True
    alone = suite.news_view()
    assert alone["join_live"] is False
    assert alone["joined"] is False
    assert alone["aznews_standalone"] is True
    assert alone["fourdmap_standalone"] is True
    assert alone["running_map"] is False
    assert alone["catalog_status"] == HONEST["4dmap"]
    assert alone["shadow_links"] == 1
    assert alone["pins"] == []
    assert alone["status"] == "No news item has landed as a pin."
    assert "live" not in alone["catalog_status"].lower()

    saved = suite.add_news(dict(STORY))
    assert saved["ok"] is True
    assert saved["join_live"] is False
    assert saved["pins"] == []
    assert saved["item"]["headline"] == STORY["headline"]
    assert saved["item"]["body"] == STORY["body"]
    assert saved["item"]["pinned_at"] is None
    assert suite.shadow_links()["count"] == 1

    for payload in (
        {},
        {"headline": "test", "body": "test"},
        {"headline": "Hi", "body": "too short"},
        {"headline": "Harbor notice today", "body": "Harbor notice today"},
        {"headline": "placeholder", "body": "This is only a placeholder."},
    ):
        refused = suite.add_news(payload)
        assert refused["ok"] is False
        assert refused["join_live"] is False
        assert refused["pins"] == []

    missing = suite.pin_news({"id": "nw-missing"})
    assert missing["ok"] is False
    assert missing["join_live"] is False

    landed = suite.pin_news({"id": saved["item"]["id"]})
    assert landed["ok"] is True
    assert landed["join_live"] is True
    assert landed["joined"] is True
    assert landed["running_map"] is False
    assert landed["catalog_status"] == HONEST["4dmap"]
    assert landed["pin"]["headline"] == STORY["headline"]
    assert landed["pin"]["body"] == STORY["body"]
    assert landed["pin"]["pinned_at"]
    assert landed["status"] == "A news item landed as a pin."
    again = suite.news_view()
    assert again["pins"][0]["headline"] == STORY["headline"]
    assert again["pins"][0]["body"] == STORY["body"]
    assert again["shadow_links"] == 1
    assert human_lines(again) == human_lines(
        {
            "ok": True,
            "display": {
                "title": "News pin",
                "summary": "A news item landed as a pin.",
                "fields": [{"label": "join_live", "value": True}],
            },
        }
    )

    other = suite.add_news(
        {
            "headline": "Second notice",
            "body": "A second written notice stays in AZNews and is not pinned.",
        }
    )
    assert other["ok"] is True
    assert other["join_live"] is True
    unpinned = next(item for item in other["items"] if item["id"] == other["item"]["id"])
    assert unpinned["pinned_at"] is None

    cleared = suite.unpin_news({"id": saved["item"]["id"]})
    assert cleared["ok"] is True
    assert cleared["join_live"] is False
    assert cleared["pins"] == []
    kept = next(item for item in cleared["items"] if item["id"] == saved["item"]["id"])
    assert kept["headline"] == STORY["headline"]
    assert kept["pinned_at"] is None
    assert suite.shadow_links()["count"] == 1


def test_pin_on_save_still_requires_the_read_back(tmp_path: Path) -> None:
    suite = _suite(tmp_path)
    body = dict(STORY)
    body["pin"] = True
    landed = suite.add_news(body)
    assert landed["join_live"] is True
    assert landed["pin"]["body"] == STORY["body"]
    stored = json.loads((tmp_path / "vendor" / "aznews.json").read_text(encoding="utf-8"))
    assert stored["items"][0]["headline"] == STORY["headline"]
    assert stored["items"][0]["pinned_at"]


def test_http_door_keeps_sentences_json_and_an_off_site(tmp_path: Path, monkeypatch) -> None:
    suite = _suite(tmp_path)
    monkeypatch.setattr("azinterface.ui.SUITE", suite)
    httpd = make_server("127.0.0.1", 0)
    port = int(httpd.server_address[1])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    try:
        home = urlopen(Request(base + "/", headers={"Accept": "text/html"})).read().decode()
        assert "Softwares 42 is the runtime catalog." in home
        assert "The domain count stays 33." in home
        assert "The packet path is not live." in home
        assert "The alternative internet is not live." in home
        assert "Still missing:" in home
        assert "WARN-5 stands." in home
        assert "Mail send does not run on the public worker." in home
        assert "The public worker does not run a kernel." in home
        assert "Boot does not run on the public worker." in home
        assert "AZNews can stand alone." in home
        assert "4DMap can stand alone." in home
        assert "Internet is not live." not in home
        assert "AZNews is live." not in home
        assert "4DMap is live" not in home

        desk = suite_html(port=port, vendor=str(tmp_path))
        worker = home_html(views=0, downloads=0, github={"stars": 0})
        for page in (desk, worker):
            assert "AZNews can stand alone." in page
            assert "Mail send does not run on the public worker." in page
            assert "WARN-5 stands." in page
            assert "Softwares 42 is the runtime catalog." in page
            assert "Internet is not live." not in page
            assert "AZNews is live." not in page

        html = urlopen(Request(base + "/suite/4dmap", headers={"Accept": "text/html"})).read().decode()
        assert "places cards on the clock" in html
        assert "does not invent marks" in html
        assert "No news item has landed as a pin." in html
        assert not html.lstrip().startswith("{")

        news_page = urlopen(Request(base + "/suite/4dmap/news", headers={"Accept": "text/html"})).read().decode()
        assert "AZNews stands on its own." in news_page
        assert "4DMap stands on its own." in news_page
        assert "The join stays unmarked until a news item lands as a pin." in news_page
        assert "AZNews is live." not in news_page
        assert not news_page.lstrip().startswith("{")

        before = json.loads(urlopen(base + "/v1/health").read().decode())
        assert before["site_state"] == "OFF"
        idle = json.loads(
            urlopen(Request(base + "/suite/4dmap", headers={"Accept": "application/json"})).read().decode()
        )
        assert idle["join_live"] is False
        assert idle["running_map"] is False

        saved = _post(base + "/suite/4dmap/news", STORY)
        assert saved["join_live"] is False
        assert saved["item"]["headline"] == STORY["headline"]
        landed = _post(base + "/suite/4dmap/pin", {"id": saved["item"]["id"]})
        assert landed["join_live"] is True
        assert landed["pin"]["headline"] == STORY["headline"]
        assert landed["pin"]["body"] == STORY["body"]
        read_back = json.loads(urlopen(base + "/suite/4dmap/pins").read().decode())
        assert read_back["pins"][0]["body"] == STORY["body"]
        after = json.loads(urlopen(base + "/v1/health").read().decode())
        assert after["site_state"] == "OFF"
        cycle = json.loads(urlopen(base + "/v1/page_cycle_status").read().decode())
        assert cycle["pipeline"]["software_count"] == 33
        assert "aznews" not in cycle["pipeline"]["softwares"]
    finally:
        httpd.shutdown()
        httpd.server_close()
        suite.stop()


def _post(url: str, body: dict) -> dict:
    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    return json.loads(urlopen(req).read().decode())
