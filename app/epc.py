import random
import base64

class EPC:
    DefaultHeader = 0x35
    DefaultManager = 759936
    MaxHeader = 0xFF
    MaxManager = 0xFFFFFFF
    MaxClass = 0xFFFFFF
    MaxSerial = 0xFFFFFFFFF

    def __init__(self, header=None, manager=None, class_=None, serial=None):
        self.header = header if header is not None else self.DefaultHeader
        self.manager = manager if manager is not None else self.DefaultManager
        self.class_ = class_ if class_ is not None else random.randint(0, self.MaxClass)
        self.serial = serial if serial is not None else random.randint(0, self.MaxSerial)

    def hex(self):
        return f"{self.header:02X}{self.manager:07X}{self.class_:06X}{self.serial:09X}"

    def b64(self):
        hex_string = self.hex()
        binary_data = bytes.fromhex(hex_string)
        return base64.b64encode(binary_data).decode('utf-8')
