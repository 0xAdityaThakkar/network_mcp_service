from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_mcp_methods():
    r = client.get("/mcp/methods")
    assert r.status_code == 200
    body = r.json()
    assert "methods" in body
    assert any(m["name"] == "ListDevices" for m in body["methods"]) 
