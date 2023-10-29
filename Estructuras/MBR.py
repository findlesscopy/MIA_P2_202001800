import struct

class Particion:
    def __init__(self):
        self.part_status = '0' # 1 = activa, 0 = inactiva, D = eliminada
        self.part_type = 'P' # P = primaria, E = extendida, L = logica
        self.part_fit = 'WF'
        self.part_start = 0
        self.part_size = 0
        self.part_name = ''

    def __bytes__(self):
        return (self.part_status.encode('utf-8') +
                self.part_type.encode('utf-8') +
                self.part_fit.encode('utf-8') +
                struct.pack("<i", self.part_start) +
                struct.pack("<i", self.part_size) +
                self.part_name.ljust(16, '\0').encode('utf-8'))
    
    def __setstate__(self, data):
        self.part_status = data[:1].decode('utf-8')
        self.part_type = data[1:2].decode('utf-8')
        self.part_fit = data[2:4].decode('utf-8')
        self.part_start = struct.unpack("<i", data[4:8])[0]
        self.part_size = struct.unpack("<i", data[8:12])[0]
        self.part_name = data[12:28].decode('utf-8').rstrip('\0')

class MBR:
    def __init__(self):
        self.mbr_tamano = 0
        self.mbr_fecha_creacion = 0
        self.mbr_disk_signature = 0
        self.disk_fit = 'FF'  # Valor por defecto: First Fit
        self.mbr_Partition_1 = Particion()
        self.mbr_Partition_2 = Particion()
        self.mbr_Partition_3 = Particion()
        self.mbr_Partition_4 = Particion()

    def __bytes__(self):
        return (struct.pack("<i", self.mbr_tamano) +
                struct.pack("<i", self.mbr_fecha_creacion) +
                struct.pack("<i", self.mbr_disk_signature) +
                self.disk_fit.encode('utf-8') +
                bytes(self.mbr_Partition_1) +
                bytes(self.mbr_Partition_2) +
                bytes(self.mbr_Partition_3) +
                bytes(self.mbr_Partition_4))