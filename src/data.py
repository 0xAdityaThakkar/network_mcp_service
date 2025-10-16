from typing import List
from .models import Device, DeviceStatus
from ipaddress import ip_address


SAMPLE_DEVICES = [
    Device(
        id="dev1",
        hostname="switch-1",
        ip=ip_address("192.168.1.10"),
        vendor="Cisco",
        model="Nexus9000",
        location="datacenter-1",
        status=DeviceStatus.online,
        tags=["leaf", "core"],
    ),
    Device(
        id="dev2",
        hostname="router-1",
        ip=ip_address("10.0.0.1"),
        vendor="Juniper",
        model="MX480",
        location="datacenter-2",
        status=DeviceStatus.maintenance,
        tags=["edge"],
    ),
    Device(
        id="dev3",
        hostname="ap-1",
        ip=ip_address("172.16.0.5"),
        vendor="Ubiquiti",
        model="UniFi-AC",
        location="branch-1",
        status=DeviceStatus.offline,
        tags=["wireless"],
    ),
]


def list_devices() -> List[Device]:
    """Return sample devices (in real app this would query a DB)."""
    return SAMPLE_DEVICES


def get_device_by_id(device_id: str) -> Device | None:
    for d in SAMPLE_DEVICES:
        if d.id == device_id:
            return d
    return None


def update_device(device_id: str, patch: dict) -> Device | None:
    """Apply a shallow patch (only top-level keys) to a device and return it.

    This is intentionally simple for the sample app. In a real app you'd validate
    and persist changes.
    """
    d = get_device_by_id(device_id)
    if not d:
        return None

    # apply allowed fields only
    for k, v in patch.items():
        if hasattr(d, k):
            setattr(d, k, v)
    return d
