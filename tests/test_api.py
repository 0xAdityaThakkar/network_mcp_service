import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_list_all():
    r = client.get("/devices")
    assert r.status_code == 200
    body = r.json()
    assert "total" in body and "items" in body
    assert body["total"] == len(body["items"]) >= 1


def test_filter_status():
    r = client.get("/devices", params={"status": "online"})
    assert r.status_code == 200
    body = r.json()
    for it in body["items"]:
        assert it["status"] == "online"


def test_filter_tag():
    r = client.get("/devices", params={"tag": "edge"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert any("router-1" == it["hostname"] for it in body["items"]) 
