import time
from .epc import EPC

class TagEvent:
    def __init__(self, epc):
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.hostname = "r700-emulator"
        self.eventType = "tagInventory"
        self.tagInventoryEvent = {
            "epc": epc.b64(),
            "epcHex": epc.hex(),
            "antennaPort": 1,
            "antennaName": "Antenna 1"
        }

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "eventType": self.eventType,
            "tagInventoryEvent": self.tagInventoryEvent
        }
