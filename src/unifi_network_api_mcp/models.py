"""Pydantic models for UniFi Network API."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class PaginatedResponse(BaseModel):
    """Base model for paginated API responses."""
    
    offset: int = Field(description="Current offset")
    limit: int = Field(description="Number of items per page")
    count: int = Field(description="Number of items in current page")
    totalCount: int = Field(description="Total number of items")
    data: List[Dict[str, Any]] = Field(description="List of items")


class ApplicationInfo(BaseModel):
    """Application information response."""
    
    applicationVersion: str = Field(description="UniFi Network application version")


class Site(BaseModel):
    """Site information."""
    
    id: str = Field(description="Site UUID")
    internalReference: Optional[str] = Field(None, description="Internal reference")
    name: str = Field(description="Site name")


class DeviceState(str, Enum):
    """Device state enum."""
    
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    PENDING = "PENDING"
    DISCONNECTED = "DISCONNECTED"
    UPGRADING = "UPGRADING"
    PROVISIONING = "PROVISIONING"
    HEARTBEAT_MISSED = "HEARTBEAT_MISSED"
    ISOLATED = "ISOLATED"


class DeviceFeature(str, Enum):
    """Device feature enum."""
    
    SWITCHING = "switching"
    ACCESS_POINT = "accessPoint"
    GATEWAY = "gateway"


class DeviceInterface(str, Enum):
    """Device interface enum."""
    
    PORTS = "ports"
    RADIOS = "radios"


class PoEStandard(str, Enum):
    """PoE standard enum."""
    
    POE_802_3AF = "802.3af"
    POE_802_3AT = "802.3at"
    POE_802_3BT = "802.3bt"
    POE_PASSIVE = "passive"


class PortState(str, Enum):
    """Port state enum."""
    
    UP = "UP"
    DOWN = "DOWN"


class PortConnector(str, Enum):
    """Port connector type enum."""
    
    RJ45 = "RJ45"
    SFP = "SFP"
    SFP_PLUS = "SFP+"


class WLANStandard(str, Enum):
    """WLAN standard enum."""
    
    IEEE_802_11A = "802.11a"
    IEEE_802_11B = "802.11b"
    IEEE_802_11G = "802.11g"
    IEEE_802_11N = "802.11n"
    IEEE_802_11AC = "802.11ac"
    IEEE_802_11AX = "802.11ax"


class ClientType(str, Enum):
    """Client type enum."""
    
    WIRED = "WIRED"
    WIRELESS = "WIRELESS"
    VPN = "VPN"
    TELEPORT = "TELEPORT"


class ClientAccessType(str, Enum):
    """Client access type enum."""
    
    DEFAULT = "DEFAULT"
    GUEST = "GUEST"
    HOTSPOT = "HOTSPOT"


class DeviceAction(str, Enum):
    """Device action enum."""
    
    RESTART = "RESTART"


class PortAction(str, Enum):
    """Port action enum."""
    
    POWER_CYCLE = "POWER_CYCLE"


class ClientAction(str, Enum):
    """Client action enum."""
    
    AUTHORIZE_GUEST_ACCESS = "AUTHORIZE_GUEST_ACCESS"
    UNAUTHORIZE_GUEST_ACCESS = "UNAUTHORIZE_GUEST_ACCESS"


# Device models
class PoEInfo(BaseModel):
    """PoE information for a port."""
    
    standard: PoEStandard
    type: int
    enabled: bool
    state: PortState


class Port(BaseModel):
    """Device port information."""
    
    idx: int = Field(description="Port index")
    state: PortState
    connector: PortConnector
    maxSpeedMbps: int = Field(description="Maximum speed in Mbps")
    speedMbps: Optional[int] = Field(None, description="Current speed in Mbps")
    poe: Optional[PoEInfo] = None


class Radio(BaseModel):
    """Device radio information."""
    
    wlanStandard: WLANStandard
    frequencyGHz: float = Field(description="Frequency band (2.4 or 5)")
    channelWidthMHz: int = Field(description="Channel width in MHz")
    channel: Optional[int] = Field(None, description="Channel number")


class DeviceInterfaces(BaseModel):
    """Device interfaces."""
    
    ports: Optional[List[Port]] = None
    radios: Optional[List[Radio]] = None


class DeviceUplink(BaseModel):
    """Device uplink information."""
    
    deviceId: str = Field(description="Uplink device UUID")


class DeviceFeatures(BaseModel):
    """Device features."""
    
    switching: Optional[Dict[str, Any]] = None
    accessPoint: Optional[Dict[str, Any]] = None


class Device(BaseModel):
    """Device information."""
    
    id: str = Field(description="Device UUID")
    name: str = Field(description="Device name")
    model: str = Field(description="Device model")
    macAddress: str = Field(description="MAC address")
    ipAddress: Optional[str] = Field(None, description="IP address")
    state: DeviceState
    features: Optional[Union[List[DeviceFeature], DeviceFeatures]] = None
    interfaces: Optional[Union[List[DeviceInterface], DeviceInterfaces]] = None


class DeviceDetails(Device):
    """Detailed device information."""
    
    supported: bool = Field(description="Whether device is supported")
    firmwareVersion: Optional[str] = None
    firmwareUpdatable: Optional[bool] = None
    adoptedAt: Optional[datetime] = None
    provisionedAt: Optional[datetime] = None
    configurationId: Optional[str] = None
    uplink: Optional[DeviceUplink] = None
    features: Optional[DeviceFeatures] = None
    interfaces: Optional[DeviceInterfaces] = None


class DeviceStatistics(BaseModel):
    """Device statistics."""
    
    uptimeSec: int = Field(description="Uptime in seconds")
    lastHeartbeatAt: datetime
    nextHeartbeatAt: datetime
    loadAverage1Min: float
    loadAverage5Min: float
    loadAverage15Min: float
    cpuUtilizationPct: float
    memoryUtilizationPct: float
    uplink: Optional[Dict[str, Any]] = None
    interfaces: Optional[Dict[str, Any]] = None


# Client models
class ClientAccess(BaseModel):
    """Client access information."""
    
    type: ClientAccessType
    authorized: Optional[bool] = None


class Client(BaseModel):
    """Client information."""
    
    id: str = Field(description="Client UUID")
    name: Optional[str] = None
    connectedAt: datetime
    ipAddress: Optional[str] = None
    access: ClientAccess
    type: ClientType


class WiredClient(Client):
    """Wired client information."""
    
    type: Literal[ClientType.WIRED] = ClientType.WIRED
    macAddress: str
    uplinkDeviceId: str


class WirelessClient(Client):
    """Wireless client information."""
    
    type: Literal[ClientType.WIRELESS] = ClientType.WIRELESS
    macAddress: str
    uplinkDeviceId: str
    signalStrength: Optional[int] = None
    ssid: Optional[str] = None


# Hotspot voucher models
class Voucher(BaseModel):
    """Hotspot voucher information."""
    
    id: str = Field(description="Voucher UUID")
    createdAt: datetime
    name: str = Field(description="Voucher note")
    code: int = Field(description="Voucher code")
    authorizedGuestLimit: int = Field(description="Number of guests allowed")
    authorizedGuestCount: int = Field(description="Number of guests authorized")
    activatedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    expired: bool
    timeLimitMinutes: int
    dataUsageLimitMBytes: Optional[int] = None
    rxRateLimitKbps: Optional[int] = None
    txRateLimitKbps: Optional[int] = None


class CreateVoucherRequest(BaseModel):
    """Request to create hotspot vouchers."""
    
    count: int = Field(1, ge=1, le=1000, description="Number of vouchers to create")
    name: str = Field(description="Voucher note")
    authorizedGuestLimit: int = Field(1, ge=1, description="Number of guests per voucher")
    timeLimitMinutes: int = Field(ge=1, le=1000000, description="Time limit in minutes")
    dataUsageLimitMBytes: Optional[int] = Field(None, ge=1, le=1048576)
    rxRateLimitKbps: Optional[int] = Field(None, ge=2, le=100000)
    txRateLimitKbps: Optional[int] = Field(None, ge=2, le=100000)


class CreateVoucherResponse(BaseModel):
    """Response from creating vouchers."""
    
    vouchers: List[Voucher]


class DeleteVoucherResponse(BaseModel):
    """Response from deleting vouchers."""
    
    vouchersDeleted: int


# Action request models
class DeviceActionRequest(BaseModel):
    """Request to perform device action."""
    
    action: DeviceAction


class PortActionRequest(BaseModel):
    """Request to perform port action."""
    
    action: PortAction


class AuthorizeGuestRequest(BaseModel):
    """Request to authorize guest access."""
    
    action: Literal[ClientAction.AUTHORIZE_GUEST_ACCESS] = ClientAction.AUTHORIZE_GUEST_ACCESS
    timeLimitMinutes: Optional[int] = Field(None, ge=1, le=1000000)
    dataUsageLimitMBytes: Optional[int] = Field(None, ge=1, le=1048576)
    rxRateLimitKbps: Optional[int] = Field(None, ge=2, le=100000)
    txRateLimitKbps: Optional[int] = Field(None, ge=2, le=100000)


class UnauthorizeGuestRequest(BaseModel):
    """Request to unauthorize guest access."""
    
    action: Literal[ClientAction.UNAUTHORIZE_GUEST_ACCESS] = ClientAction.UNAUTHORIZE_GUEST_ACCESS


# Result models for MCP
class SitesResult(BaseModel):
    """Result from listing sites."""
    
    sites: List[Site]
    totalCount: int


class DevicesResult(BaseModel):
    """Result from listing devices."""
    
    devices: List[Device]
    totalCount: int


class ClientsResult(BaseModel):
    """Result from listing clients."""
    
    clients: List[Client]
    totalCount: int


class VouchersResult(BaseModel):
    """Result from listing vouchers."""
    
    vouchers: List[Voucher]
    totalCount: int