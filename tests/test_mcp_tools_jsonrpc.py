from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_mcp_tools_jsonrpc():
    r = client.get("/mcp/tools")
    assert r.status_code == 200
    body = r.json()
    assert body.get("jsonrpc") == "2.0"
    assert "methods" in body
    names = [m["name"] for m in body["methods"]]
    assert "ListDevices" in names
    assert "GetDevice" in names
    assert "UpdateDevice" in names
