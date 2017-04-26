import json


CMD_INITIALIZE = "INITIALIZE"
CMD_BROADCAST = "BROADCAST"
CMD_UPDATE = "UPDATE"


class Message:
    def __init__(self, cmd, data):
        self.cmd = cmd
        self.data = data

    def to_string(self):
        return json.dumps({"cmd": self.cmd,
                           "data": self.data})
