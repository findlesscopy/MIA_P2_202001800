import struct

class Journaling:
    def __init__(self):
        self.estado = -1
        self.operation = ''
        self.type = -1
        self.path = ''
        self.date = 0
        self.content = ''
        self.id_propietario = ''
        self.size = 0

    def __bytes__(self):
        return (struct.pack("<i", self.estado) +
                self.operation.encode('utf-8').ljust(10, b'\x00') +
                struct.pack("<c", bytes([self.type])) +
                self.path.encode('utf-8').ljust(100, b'\x00') +
                struct.pack("<d", self.date) +
                self.content.encode('utf-8').ljust(60, b'\x00') +
                struct.pack("<c", bytes([self.id_propietario])) +
                struct.pack("<i", self.size))