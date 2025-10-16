# network_mcp_service

A minimal MCP (Model Communication Protocol) server for network devices. It exposes an HTTP JSON API to list devices with filtering and pagination.

Quick start

1. Create a Python virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the server locally:

```bash
uvicorn src.main:app --reload --port 5000
```

3. Example requests:

- List devices: GET http://127.0.0.1:8000/devices
- Filter by status: GET /devices?status=online
- Filter by vendor: GET /devices?vendor=Cisco
- Search: GET /devices?q=nexus

API docs are available at http://127.0.0.1:8000/docs

MCP endpoint

This service exposes a minimal MCP-compatible endpoint at POST /mcp. The endpoint accepts a small JSON envelope:

Request example:

```json
{ "id": "req1", "method": "ListDevices", "params": { "status": "online", "limit": 10 } }
```

Response example:

```json
{ "id": "req1", "result": { "total": 2, "items": [ /* array of devices */ ] } }
```

Unknown methods return an error envelope like:

```json
{ "id": "req1", "error": { "code": -32601, "message": "Method not found" } }
```

Discovery

Clients can discover supported MCP methods at GET /mcp/methods which returns a JSON document describing each method and its parameters. Example:

```json
{ "methods": [ { "name": "ListDevices", "description": "List devices with filters and pagination", "params": { ... } } ] }
```

Notes

- The examples assume the server runs on port 8000. In the smoke tests I used port 8001 to avoid conflicts: `uvicorn src.main:app --port 8001`.
# network_mcp_service
