import struct

class Transition:
    def __init__(self):
        self.partition = 0
        self.start = 0
        self.end = 0
        self.before = 0
        self.after = 0

    def __bytes__(self):
        return struct.pack("<5i", self.partition, self.start, self.end, self.before, self.after)