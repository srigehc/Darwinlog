from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional

@dataclass
class NormalizedEvent:
    timestamp: datetime
    source: str                 # SYSTEM | HL7 | SBX | OHMEDA
    subsystem: str
    severity: str               # INFO | WARNING | ERROR | ALARM
    event_type: str             # STATE | METRIC | MESSAGE | ALARM | USER_ACTION
    message: str
    context: Dict
    raw: Optional[str] = None