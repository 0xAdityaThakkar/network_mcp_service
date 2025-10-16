from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_device():
    envelope = {"id": "g1", "method": "GetDevice", "params": {"id": "dev1"}}
    r = client.post("/mcp", json=envelope)
    assert r.status_code == 200
    body = r.json()
    assert body.get("id") == "g1"
    assert body.get("result") is not None
    assert body["result"]["item"]["id"] == "dev1"


def test_update_device():
    # update the hostname for dev3
    envelope = {"id": "u1", "method": "UpdateDevice", "params": {"id": "dev3", "patch": {"hostname": "ap-1-updated"}}}
    r = client.post("/mcp", json=envelope)
    assert r.status_code == 200
    body = r.json()
    assert body.get("id") == "u1"
    assert body.get("result") is not None
    assert body["result"]["item"]["hostname"] == "ap-1-updated"


def test_jsonrpc_field():
    # use JSON-RPC 2.0 style
    envelope = {"jsonrpc": "2.0", "id": "j1", "method": "GetDevice", "params": {"id": "dev2"}}
    r = client.post("/mcp", json=envelope)
    assert r.status_code == 200
    body = r.json()
    assert body.get("jsonrpc") == "2.0"
    assert body.get("id") == "j1"
    assert body.get("result") is not None
