from typing import Optional, List, Any, Dict
from pydantic import BaseModel, IPvAnyAddress, conint
from enum import Enum


class DeviceStatus(str, Enum):
    online = "online"
    offline = "offline"
    maintenance = "maintenance"


class Device(BaseModel):
    id: str
    hostname: str
    ip: IPvAnyAddress
    vendor: Optional[str]
    model: Optional[str]
    location: Optional[str]
    status: DeviceStatus
    tags: List[str] = []


# MCP envelope: a minimal, JSON-RPC-like wrapper used by MCP clients
class MCPEnvelope(BaseModel):
    # JSON-RPC 2.0 compatible fields (jsonrpc must be '2.0' when used as JSON-RPC)
    jsonrpc: Optional[str] = None
    id: Optional[str]
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPListDevicesParams(BaseModel):
    status: Optional[DeviceStatus] = None
    vendor: Optional[str] = None
    location: Optional[str] = None
    tag: Optional[str] = None
    q: Optional[str] = None
    # enforce the same bounds as the REST API
    limit: Optional[conint(ge=1, le=1000)] = 100
    offset: Optional[conint(ge=0)] = 0


class MCPResult(BaseModel):
    total: int
    items: List[Device]


class MCPResponseEnvelope(BaseModel):
    jsonrpc: Optional[str] = None
    id: Optional[str]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


# GetDevice / UpdateDevice models
class GetDeviceParams(BaseModel):
    id: str


class UpdateDeviceParams(BaseModel):
    id: str
    patch: Dict[str, Any]


class GetDeviceResult(BaseModel):
    item: Optional[Device]
