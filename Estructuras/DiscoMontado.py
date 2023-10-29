
class ParticionMontada:
    def __init__(self):
        self.letra = ''
        self.estado = '0'
        self.nombre = ''

class DiscoMontado:
    def __init__(self):
        self.path = ''
        self.estado = '0'
        self.particiones = [ParticionMontada() for _ in range(26)]