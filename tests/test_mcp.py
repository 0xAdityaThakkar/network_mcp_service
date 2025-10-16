from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_mcp_list_devices():
    envelope = {"id": "1", "method": "ListDevices", "params": {"status": "online"}}
    r = client.post("/mcp", json=envelope)
    assert r.status_code == 200
    body = r.json()
    assert body.get("id") == "1"
    assert body.get("result") is not None
    assert body["result"]["total"] >= 0


def test_mcp_invalid_params():
    envelope = {"id": "2", "method": "ListDevices", "params": {"limit": -5}}
    r = client.post("/mcp", json=envelope)
    # invalid params should return 400
    assert r.status_code == 400
