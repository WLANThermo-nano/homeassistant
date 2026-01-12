from typing import Any, Dict, List, Optional

class WlanthermoData:
    def __init__(self, raw: Dict[str, Any]):
        # Always create new objects for each update to ensure sensors update
        import copy
        self.channels = [Channel(copy.deepcopy(c)) for c in raw.get("channel", [])]
        self.pitmasters = [Pitmaster(copy.deepcopy(p)) for p in raw.get("pitmaster", {}).get("pm", [])]
        self.system = SystemInfo(copy.deepcopy(raw.get("system", {})))
        
"""Data models for WLANThermo BBQ /data endpoint."""
from typing import Any, Dict, List, Optional

class SystemInfo:
    def __init__(self, data: Dict[str, Any]):
        self.time: int = int(data.get("time", 0))
        self.unit: str = str(data.get("unit", "C"))
        self.soc: Optional[int] = int(data["soc"]) if "soc" in data else None
        self.charge: Optional[bool] = bool(data["charge"]) if "charge" in data else None
        self.rssi: int = int(data.get("rssi", 0))
        self.online: int = int(data.get("online", 0))

class Channel:
    def __init__(self, data: Dict[str, Any]):
        self.number: int = int(data.get("number", 0))
        self.name: str = str(data.get("name", ""))
        self.typ: int = int(data.get("typ", 0))
        self.temp: float = float(data.get("temp", 0.0))
        self.min: float = float(data.get("min", 0.0))
        self.max: float = float(data.get("max", 0.0))
        self.alarm: int = int(data.get("alarm", 0))
        self.color: str = str(data.get("color", "#000000"))
        self.fixed: bool = bool(data.get("fixed", False))
        self.connected: bool = bool(data.get("connected", False))

class Pitmaster:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = int(data.get("id", 0))
        self.channel: int = int(data.get("channel", 0))
        self.pid: int = int(data.get("pid", 0))
        self.value: int = int(data.get("value", 0))
        self.set: float = float(data.get("set", 0.0))
        self.typ: str = str(data.get("typ", "off"))
        self.set_color: str = str(data.get("set_color", "#000000"))
        self.value_color: str = str(data.get("value_color", "#000000"))

class PitmasterType:
    def __init__(self, types: List[str]):
        self.types = types

# --- /settings models ---
class DeviceInfo:
    def __init__(self, data: Dict[str, Any]):
        self.device: str = str(data.get("device", ""))
        self.serial: str = str(data.get("serial", ""))
        self.cpu: str = str(data.get("cpu", ""))
        self.flash_size: int = int(data.get("flash_size", 0))
        self.hw_version: str = str(data.get("hw_version", ""))
        self.sw_version: str = str(data.get("sw_version", ""))
        self.api_version: str = str(data.get("api_version", ""))
        self.language: str = str(data.get("language", ""))

class SystemSettings:
    def __init__(self, data: Dict[str, Any]):
        self.time: int = int(data.get("time", 0))
        self.unit: str = str(data.get("unit", "C"))
        self.ap: str = str(data.get("ap", ""))
        self.host: str = str(data.get("host", ""))
        self.language: str = str(data.get("language", ""))
        self.version: str = str(data.get("version", ""))
        self.getupdate: str = str(data.get("getupdate", "false"))
        self.hwversion: str = str(data.get("hwversion", ""))

class SensorType:
    def __init__(self, data: Dict[str, Any]):
        self.type: int = int(data.get("type", 0))
        self.name: str = str(data.get("name", ""))
        self.fixed: bool = bool(data.get("fixed", False))

class FeatureSet:
    def __init__(self, data: Dict[str, Any]):
        self.bluetooth: bool = bool(data.get("bluetooth", False))
        self.pitmaster: bool = bool(data.get("pitmaster", False))

class PIDConfig:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = str(data.get("name", ""))
        self.id: int = int(data.get("id", 0))
        self.aktor: int = int(data.get("aktor", 0))
        self.Kp: float = float(data.get("Kp", 0.0))
        self.Ki: float = float(data.get("Ki", 0.0))
        self.Kd: float = float(data.get("Kd", 0.0))
        self.DCmmin: int = int(data.get("DCmmin", 0))
        self.DCmmax: int = int(data.get("DCmmax", 0))
        self.opl: bool = bool(data.get("opl", False))
        self.SPmin: int = int(data.get("SPmin", 0))
        self.SPmax: int = int(data.get("SPmax", 0))
        self.link: int = int(data.get("link", 0))
        self.tune: bool = bool(data.get("tune", False))
        self.jp: int = int(data.get("jp", 0))

class DisplayInfo:
    def __init__(self, data: Dict[str, Any]):
        self.updname: str = str(data.get("updname", ""))
        self.orientation: int = int(data.get("orientation", 0))

class IotSettings:
    def __init__(self, data: Dict[str, Any]):
        self.CLon: bool = bool(data.get("CLon", False))
        self.CLtoken: str = str(data.get("CLtoken", ""))
        self.CLint: int = int(data.get("CLint", 0))
        self.CLurl: str = str(data.get("CLurl", ""))
        self.CLlink: str = str(data.get("CLurl", "")) + "?api_token=" + str(data.get("CLtoken", ""))

class NotesExt:
    def __init__(self, data: Dict[str, Any]):
        self.on: int = int(data.get("on", 0))
        self.token: str = str(data.get("token", ""))
        self.id: str = str(data.get("id", ""))
        self.repeat: int = int(data.get("repeat", 1))
        self.service: int = int(data.get("service", 0))
        self.services: list = data.get("services", [])

class Notes:
    def __init__(self, data: Dict[str, Any]):
        self.fcm: list = data.get("fcm", [])
        self.ext: NotesExt = NotesExt(data.get("ext", {}))

class SettingsData:
    def __init__(self, raw: Dict[str, Any]):
        self.device = DeviceInfo(raw.get("device", {}))
        self.system = SystemSettings(raw.get("system", {}))
        self.hardware = raw.get("hardware", [])
        self.api = raw.get("api", {})
        self.sensors = [SensorType(s) for s in raw.get("sensors", [])]
        self.features = FeatureSet(raw.get("features", {}))
        self.pid = [PIDConfig(p) for p in raw.get("pid", [])]
        self.aktor = raw.get("aktor", [])
        self.display = DisplayInfo(raw.get("display", {}))
        self.iot = IotSettings(raw.get("iot", {}))
        self.notes = Notes(raw.get("notes", {}))

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "SettingsData":
        return cls(data)
