"""Pydantic models for UniFi Network API."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, model_validator


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
    IEEE_802_11BE = "802.11be"


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


# Enum values reported by the controller grow with new hardware (e.g. 802.11be
# radios), so response fields accept unknown strings instead of failing the
# whole response.
DeviceStateValue = Union[DeviceState, str]
PoEStandardValue = Union[PoEStandard, str]
PortStateValue = Union[PortState, str]
PortConnectorValue = Union[PortConnector, str]
WLANStandardValue = Union[WLANStandard, str]
ClientAccessTypeValue = Union[ClientAccessType, str]


# Device models
class PoEInfo(BaseModel):
    """PoE information for a port."""

    standard: PoEStandardValue
    type: int
    enabled: bool
    state: PortStateValue


class Port(BaseModel):
    """Device port information."""

    idx: int = Field(description="Port index")
    state: PortStateValue
    connector: PortConnectorValue
    maxSpeedMbps: int = Field(description="Maximum speed in Mbps")
    speedMbps: Optional[int] = Field(None, description="Current speed in Mbps")
    poe: Optional[PoEInfo] = None


class Radio(BaseModel):
    """Device radio information."""

    wlanStandard: WLANStandardValue
    frequencyGHz: float = Field(description="Frequency band (2.4, 5 or 6)")
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
    state: DeviceStateValue
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
    """Device statistics.

    Telemetry fields are optional: low-end devices (e.g. USW Flex Mini) don't
    report load averages, and offline devices may omit most fields.
    """

    uptimeSec: Optional[int] = Field(None, description="Uptime in seconds")
    lastHeartbeatAt: Optional[datetime] = None
    nextHeartbeatAt: Optional[datetime] = None
    loadAverage1Min: Optional[float] = None
    loadAverage5Min: Optional[float] = None
    loadAverage15Min: Optional[float] = None
    cpuUtilizationPct: Optional[float] = None
    memoryUtilizationPct: Optional[float] = None
    uplink: Optional[Dict[str, Any]] = None
    interfaces: Optional[Dict[str, Any]] = None


# Client models
class ClientAccess(BaseModel):
    """Client access information."""
    
    type: ClientAccessTypeValue
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
    uplinkPortIdx: Optional[int] = Field(None, description="Port index on the uplink switch (client_details only)")


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


# Network configuration models
REDACTED = "<redacted>"
SECRET_FIELDS = {"passphrase", "password", "presharedKey", "sharedSecret", "privateKey", "utm_token"}


def _is_secret(key: str) -> bool:
    # The classic API prefixes every secret field with "x_" (x_passphrase, x_wireguard_private_key, ...)
    return key in SECRET_FIELDS or key.startswith("x_")


def redact_secrets(value: Any) -> Any:
    """Replace secret values (Wi-Fi passphrases, shared secrets, private keys) so they never reach the MCP client."""
    if isinstance(value, dict):
        return {k: REDACTED if _is_secret(k) and v else redact_secrets(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_secrets(v) for v in value]
    return value


class Redacted(BaseModel):
    """Base for models carrying raw configuration; secrets are redacted on validation."""
    
    @model_validator(mode="before")
    @classmethod
    def _redact(cls, data: Any) -> Any:
        return redact_secrets(data)


class ConfigObject(Redacted):
    """Base for configuration objects.
    
    Only the commonly used fields are typed; everything else the controller returns
    is passed through so new firmware fields don't break validation. Secrets are redacted.
    """
    
    model_config = ConfigDict(extra="allow")


class ObjectMetadata(BaseModel):
    """Where a configuration object came from."""
    
    model_config = ConfigDict(extra="allow")
    
    origin: Optional[str] = Field(None, description="SYSTEM_DEFINED or USER_DEFINED")
    configurable: Optional[bool] = None


class Network(ConfigObject):
    """Network (LAN/VLAN) configuration. Details include IPv4/IPv6 and DHCP settings."""
    
    id: str = Field(description="Network UUID")
    name: str
    enabled: Optional[bool] = None
    management: Optional[str] = Field(None, description="e.g. GATEWAY, SWITCH, UNMANAGED")
    vlanId: Optional[int] = None
    default: Optional[bool] = None
    zoneId: Optional[str] = Field(None, description="Firewall zone UUID")
    metadata: Optional[ObjectMetadata] = None


class WifiBroadcast(ConfigObject):
    """WiFi network (SSID) configuration. Passphrases are redacted."""
    
    id: str = Field(description="WiFi broadcast UUID")
    name: str = Field(description="SSID")
    type: Optional[str] = Field(None, description="e.g. STANDARD, IOT_OPTIMIZED")
    enabled: Optional[bool] = None
    network: Optional[Dict[str, Any]] = Field(None, description="Network the SSID is bridged to")
    securityConfiguration: Optional[Dict[str, Any]] = None
    metadata: Optional[ObjectMetadata] = None


class FirewallZone(ConfigObject):
    """Firewall zone."""
    
    id: str = Field(description="Zone UUID")
    name: str
    networkIds: List[str] = Field(default_factory=list, description="Network UUIDs in this zone")
    metadata: Optional[ObjectMetadata] = None


class FirewallPolicy(ConfigObject):
    """Zone-based firewall policy."""
    
    id: str = Field(description="Policy UUID")
    name: str
    enabled: Optional[bool] = None
    index: Optional[int] = Field(None, description="Evaluation order (lower runs first)")
    action: Optional[Dict[str, Any]] = Field(None, description="ALLOW/BLOCK/REJECT and options")
    source: Optional[Dict[str, Any]] = Field(None, description="Source zone and traffic filter")
    destination: Optional[Dict[str, Any]] = Field(None, description="Destination zone and traffic filter")
    ipProtocolScope: Optional[Dict[str, Any]] = None
    loggingEnabled: Optional[bool] = None
    metadata: Optional[ObjectMetadata] = None


class PortForward(ConfigObject):
    """Port forwarding rule (from the classic Network API, field names as returned)."""
    
    id: str = Field(validation_alias="_id", description="Rule ID")
    name: Optional[str] = None
    enabled: Optional[bool] = None
    proto: Optional[str] = Field(None, description="tcp, udp or tcp_udp")
    pfwd_interface: Optional[str] = Field(None, description="WAN interface(s) the rule listens on")
    dst_port: Optional[str] = Field(None, description="External port(s)")
    fwd: Optional[str] = Field(None, description="Internal IP address forwarded to")
    fwd_port: Optional[str] = Field(None, description="Internal port(s)")
    src_limiting_enabled: Optional[bool] = Field(None, description="Whether source addresses are restricted")
    log: Optional[bool] = None


class ClassicConfigObject(ConfigObject):
    """Configuration object from the classic Network API (snake_case fields, passed through as returned).
    
    Classic IDs differ from integration API IDs for the same object; match on name.
    """
    
    id: str = Field(validation_alias="_id", description="Classic API ID")
    name: Optional[str] = None


class SwitchPortConfig(BaseModel):
    """Switch port VLAN and PoE configuration."""
    
    idx: int = Field(description="Port index")
    name: Optional[str] = None
    up: Optional[bool] = None
    enabled: Optional[bool] = None
    speedMbps: Optional[int] = None
    isUplink: Optional[bool] = None
    overridden: bool = Field(description="False means the port uses the switch's default port profile")
    portProfile: Optional[str] = Field(None, description="Port profile name, if one is assigned")
    forward: Optional[str] = Field(None, description="all, native, customize or disabled")
    nativeNetwork: Optional[str] = Field(None, description="Native (untagged) network; null when not overridden")
    taggedVlanMgmt: Optional[str] = Field(None, description="auto (all VLANs tagged), block_all or custom")
    taggedNetworks: Optional[List[str]] = Field(None, description="Tagged networks when taggedVlanMgmt is custom")
    excludedNetworks: Optional[List[str]] = Field(None, description="Networks excluded from tagging")
    poeMode: Optional[str] = Field(None, description="auto, off, pasv24, passthrough; null if the port has no PoE")
    poePowerW: Optional[float] = None
    portSecurityEnabled: Optional[bool] = None


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


class NetworksResult(BaseModel):
    """Result from listing networks."""
    
    networks: List[Network]
    totalCount: int


class WifiBroadcastsResult(BaseModel):
    """Result from listing WiFi broadcasts."""
    
    wifiBroadcasts: List[WifiBroadcast]
    totalCount: int


class FirewallZonesResult(BaseModel):
    """Result from listing firewall zones."""
    
    zones: List[FirewallZone]
    totalCount: int


class FirewallPoliciesResult(BaseModel):
    """Result from listing firewall policies."""
    
    policies: List[FirewallPolicy]
    totalCount: int


class PortForwardsResult(BaseModel):
    """Result from listing port forwarding rules."""
    
    portForwards: List[PortForward]
    totalCount: int


class TrafficMatchingListsResult(Redacted):
    """Result from listing traffic matching lists (firewall match objects)."""
    
    trafficMatchingLists: List[Dict[str, Any]]
    totalCount: int


class NetworkServicesResult(Redacted):
    """Per-network DHCP/DNS/multicast settings plus the site-wide multicast and DNS settings."""
    
    networks: List[ClassicConfigObject] = Field(description="LAN and VPN networks (WANs excluded)")
    mdns: Optional[Dict[str, Any]] = Field(None, description="Site-wide mDNS reflector settings")
    igmpSnooping: Optional[Dict[str, Any]] = Field(None, description="Site-wide IGMP snooping settings")
    dnsOverHttps: Optional[Dict[str, Any]] = Field(None, description="Gateway DNS-over-HTTPS settings")


class WifiAdvancedSettingsResult(Redacted):
    """Classic WiFi settings per SSID, with network and AP group names resolved."""
    
    wifiNetworks: List[ClassicConfigObject]
    apGroups: List[Dict[str, Any]]


class VpnResult(Redacted):
    """VPN servers, VPN client networks and Teleport."""
    
    servers: List[Dict[str, Any]] = Field(description="VPN servers with the firewall zone they belong to")
    clientNetworks: List[ClassicConfigObject] = Field(description="Networks assigned to VPN clients (subnet, DNS, zone)")
    teleport: Optional[Dict[str, Any]] = Field(None, description="Teleport enabled flag and client subnet")
    siteToSiteMagicVpnEnabled: Optional[bool] = None


class ThreatManagementResult(Redacted):
    """IDS/IPS, DNS/ad filtering and content filtering settings."""
    
    ips: Optional[Dict[str, Any]] = Field(None, description="IDS/IPS mode, categories, ad blocking, DNS filtering, honeypot")
    ipsSuppression: Optional[Dict[str, Any]] = Field(None, description="Suppressed alerts and allow-listed traffic")
    contentFiltering: Any = Field(None, description="Content filtering profiles")
    dpi: Optional[Dict[str, Any]] = Field(None, description="Deep packet inspection settings")


class SwitchPortsResult(Redacted):
    """Per-port configuration of a switch (or gateway's built-in switch)."""
    
    deviceId: str
    deviceName: Optional[str] = None
    model: Optional[str] = None
    ports: List[SwitchPortConfig]
    portProfiles: List[Dict[str, Any]] = Field(description="Port profiles defined on the site")