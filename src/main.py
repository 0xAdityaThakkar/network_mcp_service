from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import uvicorn
from .models import (
    Device,
    DeviceStatus,
    MCPEnvelope,
    MCPListDevicesParams,
    MCPResponseEnvelope,
    MCPResult,
    GetDeviceParams,
    UpdateDeviceParams,
    GetDeviceResult,
)
from .data import list_devices, get_device_by_id, update_device
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:8000",
]

app = FastAPI(title="Network MCP Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ListResponse(BaseModel):
    total: int
    items: List[Device]


def filter_devices(
    status: Optional[DeviceStatus] = None,
    vendor: Optional[str] = None,
    location: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Device]:
    """Return filtered devices from the data layer."""
    devices = list_devices()

    def matches(d: Device) -> bool:
        if status and d.status != status:
            return False
        if vendor and (d.vendor is None or vendor.lower() not in d.vendor.lower()):
            return False
        if location and (d.location is None or location.lower() not in d.location.lower()):
            return False
        if tag and tag not in d.tags:
            return False
        if q:
            ql = q.lower()
            if ql not in d.hostname.lower() and (d.model is None or ql not in d.model.lower()):
                return False
        return True

    return [d for d in devices if matches(d)]


@app.get("/devices", response_model=ListResponse)
def get_devices(
    status: Optional[DeviceStatus] = Query(None, description="Filter by device status"),
    vendor: Optional[str] = Query(None, description="Filter by vendor name"),
    location: Optional[str] = Query(None, description="Filter by location"),
    tag: Optional[str] = Query(None, description="Filter by tag (single)"),
    q: Optional[str] = Query(None, description="Full-text search across hostname, model"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List devices with filters and pagination. Returns JSON with total count and items."""
    filtered = filter_devices(status=status, vendor=vendor, location=location, tag=tag, q=q)
    total = len(filtered)
    items = filtered[offset : offset + limit]
    return ListResponse(total=total, items=items)


@app.post("/mcp", response_model=MCPResponseEnvelope)
def mcp_endpoint(envelope: MCPEnvelope):
    """Minimal MCP endpoint. Supports method 'ListDevices' with params similar to the REST API.

    Envelope format (JSON):
      { "id": "req1", "method": "ListDevices", "params": { ... } }
    """
    # JSON-RPC 2.0: if envelope.jsonrpc == '2.0' treat as JSON-RPC; respond using same jsonrpc field
    is_jsonrpc = envelope.jsonrpc == "2.0"

    if envelope.method == "ListDevices":
        params = {}
        if envelope.params:
            params = envelope.params

        try:
            # validate/parse params with pydantic helper model
            parsed = MCPListDevicesParams(**params)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"invalid params: {e}")

        filtered = filter_devices(
            status=parsed.status,
            vendor=parsed.vendor,
            location=parsed.location,
            tag=parsed.tag,
            q=parsed.q,
        )
        total = len(filtered)
        items = filtered[parsed.offset : parsed.offset + parsed.limit]
        result = MCPResult(total=total, items=items)
        resp = MCPResponseEnvelope(id=envelope.id, result=result.dict())
        if is_jsonrpc:
            resp.jsonrpc = "2.0"
        return resp

    if envelope.method == "GetDevice":
        try:
            params = GetDeviceParams(**(envelope.params or {}))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"invalid params: {e}")

        d = get_device_by_id(params.id)
        result = GetDeviceResult(item=d)
        resp = MCPResponseEnvelope(id=envelope.id, result=result.dict())
        if is_jsonrpc:
            resp.jsonrpc = "2.0"
        return resp

    if envelope.method == "UpdateDevice":
        try:
            params = UpdateDeviceParams(**(envelope.params or {}))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"invalid params: {e}")

        d = update_device(params.id, params.patch)
        if not d:
            return MCPResponseEnvelope(id=envelope.id, error={"code": 404, "message": "Device not found"})
        resp = MCPResponseEnvelope(id=envelope.id, result={"item": d.dict()})
        if is_jsonrpc:
            resp.jsonrpc = "2.0"
        return resp

    # unknown method
    return MCPResponseEnvelope(id=envelope.id, error={"code": -32601, "message": "Method not found"})


@app.get("/list-tools")
def mcp_methods():
    """Return a small discovery document describing supported MCP methods and their params."""
    return {
        "methods": [
            {
                "name": "ListDevices",
                "description": "List devices with filters and pagination",
                "params": {
                    "status": "online|offline|maintenance",
                    "vendor": "string (substring, case-insensitive)",
                    "location": "string (substring, case-insensitive)",
                    "tag": "string (single tag exact match)",
                    "q": "string (search hostname/model)",
                    "limit": "int (1..1000)",
                    "offset": "int (>=0)",
                },
            }
            ,
            {
                "name": "GetDevice",
                "description": "Fetch a single device by id",
                "params": {"id": "string (device id)"},
            },
            {
                "name": "UpdateDevice",
                "description": "Apply a shallow patch to a device",
                "params": {"id": "string (device id)", "patch": "object (fields to update)"},
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)