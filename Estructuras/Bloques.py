import struct

class Content:
    def __init__(self):
        self.b_name = '\x00' * 12
        self.b_inodo = -1

    def __bytes__(self):
        return (self.b_name.ljust(12, '\0').encode('utf-8') +
                struct.pack("<i", self.b_inodo))

class BloquesCarpetas:
    def __init__(self):
        self.b_content = [Content() for _ in range(4)]

    def __bytes__(self):
        return b"".join(bytes(c) for c in self.b_content)

class BloquesArchivos:
    def __init__(self):
        self.b_content = '\x00' * 64

    def __bytes__(self):
        return self.b_content.ljust(64, '\0').encode('utf-8')
    
class BloquesApuntadores:
    def __init__(self):
        self.b_pointers = [-1] * 16

    def __bytes__(self):
        return struct.pack("<16i", *self.b_pointers)