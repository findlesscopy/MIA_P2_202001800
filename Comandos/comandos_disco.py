import os
import random
import sys
import time
from Estructuras.MBR import *
from Estructuras.EBR import *
from Estructuras.SuperBloque import *
from Estructuras.Inodos import *
from Estructuras.Bloques import *
from Estructuras.Journaling import *
from utils import *

from Global.Global import particiones_montadas

# Comando MKDISK
def cmd_mkdisk(size, path, fit, unit):
    disco = MBR()
    #print("DEBE TENER UN FIT: "+fit)
    try:
        if unit == 'K':
            total_size = 1024 * size
        elif unit == 'M':
            total_size = 1024 * 1024 * size
        else:
            print("Error: Unidad no válida")
            salida.append("ERROR: Unidad no válida")
            return
        if size <= 0:
            print("\tERROR: El parámetro size del comando MKDISK debe ser mayor a 0")
            salida.append("ERROR: El parámetro size del comando MKDISK debe ser mayor a 0")
            return

        fit = fit
        disco.mbr_tamano = total_size
        disco.mbr_fecha_creacion = int(time.time())
        disco.disk_fit = fit
        disco.mbr_disk_signature = random.randint(100, 9999)

        if os.path.exists(path):
            print("\tERROR: Disco ya existente en la ruta: "+path)
            salida.append("ERROR: Disco ya existente en la ruta: "+path)
            return
        folder_path = os.path.dirname(path)
        os.makedirs(folder_path, exist_ok=True)

        disco.mbr_Partition_1 = Particion()
        disco.mbr_Partition_2 = Particion()
        disco.mbr_Partition_3 = Particion()
        disco.mbr_Partition_4 = Particion()

        if path.startswith("\""):
            path = path[1:-1]

        if not path.endswith(".dsk"):
            print("\tERROR: Extensión de archivo no válida para la creación del Disco.")
            salida.append("ERROR: Extensión de archivo no válida para la creación del Disco.")
            return

        try:
            with open(path, "w+b") as file:
                file.write(b"\x00")
                file.seek(total_size - 1)
                file.write(b"\x00")
                file.seek(0)
                file.write(bytes(disco))
            print("\t>>>> MKDISK: Disco creado exitosamente <<<<")
            salida.append(">>>> MKDISK: Disco creado exitosamente <<<<")
            return
        except Exception as e:
            print(e)
            print("\tERROR: Error al crear el disco en la ruta: "+path)
            salida.append("ERROR: Error al crear el disco en la ruta: "+path)
            return
    except ValueError:
        print("\tERROR: El parámetro size del comando MKDISK debe ser un número entero")
        salida.append("ERROR: El parámetro size del comando MKDISK debe ser un número entero")
        return


# Comando RMDISK
def cmd_rmdisk(path):
    if path:
        try:
            if os.path.isfile(path):
                if not path.endswith(".dsk"):
                    print("\tERROR: Extensión de archivo no válida para la eliminación del Disco.")
                    salida.append("ERROR: Extensión de archivo no válida para la eliminación del Disco.")
                    return 
                
                os.remove(path)
                print("\t> RMDISK: Disco eliminado exitosamente") 
                salida.append(">>>> RMDISK: Disco eliminado exitosamente <<<<")
                return
            else:
                print("\tERROR: El disco no existe en la ruta indicada.")
                salida.append("ERROR: El disco no existe en la ruta indicada.")
                return 
        except Exception as e:
            print("\tERROR: Error al intentar eliminar el disco: "+str(e)) 
            salida.append("ERROR: Error al intentar eliminar el disco: "+str(e))
            return

# Comando FDISK
def cmd_fdisk(size, path, name, unit, type, fit, delete, add):
    #parametros obligatorios size, path, name
    if size is None:
        print("\t> FDISK: No se encuentra en parámetro size.")
        salida.append("ERROR: No se encuentra en parámetro size.")
        return
    elif path is None:
        print("\t> FDISK: No se encuentra en parámetro path.")
        salida.append("ERROR: No se encuentra en parámetro path.")
        return
    elif name is None:
        print("\t> FDISK: No se encuentra en parámetro name.")
        salida.append("ERROR: No se encuentra en parámetro name.")
        return
    else:
        if delete != None:
            eliminarParticion(name, path)
            #print("Eliminar particion")
        elif add != None:
            #agregarParticion(add, name, path, unit)
            print("\t> FDISK: Se modifico el espacio")
            salida.append(">>>> FDISK: Se modifico el espacio <<<<")
            return
        else:
            crearParticion(size, path, name, unit, type, fit)
            #print("Crear particion")

def crearParticion(size, path, name, unit, type, fit):
    if size <= 0:
        print("\tERROR: El parámetro size del comando FDISK debe ser mayor a 0")
        salida.append("ERROR: El parámetro size del comando FDISK debe ser mayor a 0")
        return
    
    if unit == "B":
        size = size
    elif unit == "K":
        size = size * 1024
    elif unit == "M":
        size = size * 1024 * 1024
    
    if type not in ["P", "E", "L"]:
        print("\tERROR: El parámetro type del comando FDISK debe ser P, E o L")
        salida.append("ERROR: El parámetro type del comando FDISK debe ser P, E o L")
        return
    
    if fit not in ["BF", "FF", "WF"]:
        print("\tERROR: El parámetro fit del comando FDISK debe ser BF, FF o WF")
        salida.append("ERROR: El parámetro fit del comando FDISK debe ser BF, FF o WF")
        return
    
    if path.startswith("\""):
        path = path[1:-1]

    if not path.endswith(".dsk"):
        print("\tERROR: Extensión de archivo no válida para la creación del Disco.")
        salida.append("ERROR: Extensión de archivo no válida para la creación del Disco.")
        return
    
    if not os.path.exists(path):
        print("\tERROR: No existe el disco en la ruta: "+path)
        salida.append("ERROR: No existe el disco en la ruta: "+path)
        return
    
    try:
        mbr = MBR()
        ebr = EBR()
        logica_ebr = EBR()
        with open(path, "rb") as file:
            mbr_data = file.read()
            mbr.mbr_tamano = struct.unpack("<i", mbr_data[0:4])[0]
            mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
            mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
            mbr.disk_fit = mbr_data[12:14].decode("utf-8")

            partition_size = struct.calcsize("<iii16s")*4
            partition_data = mbr_data[14:14 + partition_size]
            mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
            mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
            mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
            mbr.mbr_Partition_4.__setstate__(partition_data[84:112])
    except Exception as e:
        print(e)

    particiones = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
    
    tmp_size_deleted = []
    existe_extendida = False
    tmp_nombres = []
    for particion in particiones:
        tmp_nombres.append(particion.part_name)
        if(particion.part_status == 'D'):
            tmp_size_deleted.append(particion.part_size)
        if(particion.part_type == 'E'):
            existe_extendida = True
    if name in tmp_nombres:
        print("\tERROR: Ya existe una partición con el nombre: "+name)
        salida.append("ERROR: Ya existe una partición con el nombre: "+name)
        return
    if type == 'P':
        print("\t> FDISK: Creando partición primaria...")
        salida.append(">>>> FDISK: Creando partición primaria... <<<<")
    elif type == 'E':
        print("\t> FDISK: Creando partición extendida...")
        salida.append(">>>> FDISK: Creando partición extendida... <<<<")

    elif type == 'L':
        print("\t> FDISK: Creando partición lógica...")
        salida.append(">>>> FDISK: Creando partición lógica... <<<<")


    # Particiones Primarias
    size_mbr = 14 + (struct.calcsize("<iii16s")*4)
    if mbr.disk_fit == "FF":
        tmp_size = size_mbr
        for particion in particiones:
            if type == 'P':
                # si la particion ya existe, solamente sumar el tamaño
                if particion.part_status == '1':
                    tmp_size += particion.part_size
                # si la particion no existe, crearla
                elif particion.part_status == '0':
                    particion.part_status = '1'
                    particion.part_type = type
                    particion.part_fit = fit
                    particion.part_size = size
                    particion.part_name = name
                    particion.part_start = tmp_size
                    break
                # si la particion ha sido eliminada, crear la particion en el primer espacio libre
                elif particion.part_status == 'D':
                    tmp_size_deleted = tmp_size_deleted[0]
                    if tmp_size_deleted >= size:
                        particion.part_status = '1'
                        particion.part_type = type
                        particion.part_fit = fit
                        particion.part_size = size
                        particion.part_name = name
                        particion.part_start = tmp_size
                        tmp_size += size
                        break
                    else:
                        print("\tERROR: No hay espacio suficiente para crear la partición.")
                        salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                        return
                    
            elif type == 'E':
                if existe_extendida:
                    print("\tERROR: No se puede crear una partición extendida, porque ya existe una.")
                    salida.append("ERROR: No se puede crear una partición extendida, porque ya existe una.")
                    return
                if particion.part_status == '1':
                    tmp_size += particion.part_size

                # si la particion no existe, crearla y crear un EBR
                elif particion.part_status == '0':
                    
                    particion.part_status = '1'
                    particion.part_type = type
                    particion.part_fit = fit
                    particion.part_size = size
                    particion.part_name = name
                    particion.part_start = tmp_size

                    # crear EBR de la particion extendida
                    ebr.part_status = '0'
                    ebr.part_fit = 'WF'
                    ebr.part_start = tmp_size
                    ebr.part_size = 0
                    ebr.part_next = 1234
                    ebr.part_name = "null"
                    break
                # si la particion ha sido eliminada, crear la particion en el primer espacio libre
                elif particion.part_status == 'D':
                    tmp_size_deleted = tmp_size_deleted[0]
                    if tmp_size_deleted >= size:
                        particion.part_status = '1'
                        particion.part_type = type
                        particion.part_fit = fit
                        particion.part_size = size
                        particion.part_name = name
                        particion.part_start = tmp_size
                        tmp_size += size

                        ebr.part_status = '0'
                        ebr.part_fit = 'WF'
                        ebr.part_start = tmp_size
                        ebr.part_size = 0
                        ebr.part_next = 1234
                        ebr.part_name = "null"
                        break
                    else:
                        print("\tERROR: No hay espacio suficiente para crear la partición.")
                        salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                        return

            elif type == 'L':
                existe_extendida = False
                for particion in particiones:
                    if particion.part_type == 'E':
                        existe_extendida = True
                        particionLogica(particion, path, size, name, mbr.disk_fit, fit)
                        return
                if not existe_extendida:
                    print("\tERROR: No existe una partición extendida para crear la partición lógica.")
                    salida.append("ERROR: No existe una partición extendida para crear la partición lógica.")
                    return


    elif mbr.disk_fit == "BF":
        tmp_size = size_mbr
        for particion in particiones:
            if type == 'P':
                # si la particion ya existe, solamente sumar el tamaño
                if particion.part_status == '1':
                    tmp_size += particion.part_size
                # si la particion no existe, crearla
                elif particion.part_status == '0':
                    particion.part_status = '1'
                    particion.part_type = type
                    particion.part_fit = fit
                    particion.part_size = size
                    particion.part_name = name
                    particion.part_start = tmp_size
                    break
                # si la particion ha sido eliminada, crear la particion en el tamaño mas pequeño
                elif particion.part_status == 'D':
                    tmp_size_deleted.sort()
                    tmp_size_deleted = tmp_size_deleted[0]
                    if tmp_size_deleted >= size:
                        particion.part_status = '1'
                        particion.part_type = type
                        particion.part_fit = fit
                        particion.part_size = size
                        particion.part_name = name
                        particion.part_start = tmp_size
                        break
                    else:
                        print("\tERROR: No hay espacio suficiente para crear la partición.")
                        salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                        return
            elif type == 'E':
                if existe_extendida:
                    print("\tERROR: No se puede crear una partición extendida, porque ya existe una.")
                    salida.append("ERROR: No se puede crear una partición extendida, porque ya existe una.")
                    return
                if particion.part_status == '1':
                    tmp_size += particion.part_size
                # si la particion no existe, crearla y crear un EBR
                elif particion.part_status == '0':
                    particion.part_status = '1'
                    particion.part_type = type
                    particion.part_fit = fit
                    particion.part_size = size
                    particion.part_name = name
                    particion.part_start = tmp_size

                    # crear EBR de la particion extendida
                    ebr.part_status = '0'
                    ebr.part_fit = 'WF'
                    ebr.part_start = tmp_size
                    ebr.part_size = 0
                    ebr.part_next = 1234
                    ebr.part_name = "null"
                    break
                    
            elif type == 'L':
                existe_extendida = False
                for particion in particiones:
                    if particion.part_type == 'E':
                        existe_extendida = True
                        particionLogica(particion, path, size, name, mbr.disk_fit, fit)
                        return
                if not existe_extendida:
                    print("\tERROR: No existe una partición extendida para crear la partición lógica.")
                    salida.append("ERROR: No existe una partición extendida para crear la partición lógica.")
                    return
                        
    elif mbr.disk_fit == "WF":
        tmp_size = size_mbr
        for particion in particiones:
            if type == 'P':
                # si la particion ya existe, solamente sumar el tamaño
                if particion.part_status == '1':
                    tmp_size += particion.part_size
                # si la particion no existe, crearla
                elif particion.part_status == '0':
                    particion.part_status = '1'
                    particion.part_type = type
                    particion.part_fit = fit
                    particion.part_size = size
                    particion.part_name = name
                    particion.part_start = tmp_size
                    tmp_size += size
                    break
                # si la particion ha sido eliminada, crear la particion en el tamaño mas grande
                elif particion.part_status == 'D':
                    tmp_size_deleted.sort(reverse=True)
                    tmp_size_deleted = tmp_size_deleted[0]
                    if tmp_size_deleted >= size:
                        particion.part_status = '1'
                        particion.part_type = type
                        particion.part_fit = fit
                        particion.part_size = size
                        particion.part_name = name
                        particion.part_start = tmp_size
                        tmp_size += size
                        break
                    else:
                        print("\tERROR: No hay espacio suficiente para crear la partición.")
                        salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                        return    
            elif type == 'E':
                if existe_extendida:
                    print("\tERROR: No se puede crear una partición extendida, porque ya existe una.")
                    salida.append("ERROR: No se puede crear una partición extendida, porque ya existe una.")
                    return
                if particion.part_status == '1':
                    tmp_size += particion.part_size

                # si la particion no existe, crearla y crear un EBR
                elif particion.part_status == '0':
                    
                    particion.part_status = '1'
                    particion.part_type = type
                    particion.part_fit = fit
                    particion.part_size = size
                    particion.part_name = name
                    particion.part_start = tmp_size

                    # crear EBR de la particion extendida
                    ebr.part_status = '0'
                    ebr.part_fit = 'WF'
                    ebr.part_start = tmp_size
                    ebr.part_size = 0
                    ebr.part_next = 1234
                    ebr.part_name = 'null'
                    break
                # si la particion ha sido eliminada, crear la particion en el tamaño mas grande
                elif particion.part_status == 'D':
                    tmp_size_deleted.sort(reverse=True)
                    tmp_size_deleted = tmp_size_deleted[0]
                    if tmp_size_deleted >= size:
                        particion.part_status = '1'
                        particion.part_type = type
                        particion.part_fit = fit
                        particion.part_size = size
                        particion.part_name = name
                        particion.part_start = tmp_size

                        ebr.part_status = '0'
                        ebr.part_fit = 'WF'
                        ebr.part_start = tmp_size
                        ebr.part_size = 0
                        ebr.part_next = 1234
                        ebr.part_name = "null"
                        break
                    else:
                        print("\tERROR: No hay espacio suficiente para crear la partición.")
                        salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                        return     
                    
            elif type == 'L':
                existe_extendida = False
                for particion in particiones:
                    if particion.part_type == 'E':
                        existe_extendida = True
                        particionLogica(particion, path, size, name, mbr.disk_fit, fit)
                        return
                if not existe_extendida:
                    print("\tERROR: No existe una partición extendida para crear la partición lógica.")
                    salida.append("ERROR: No existe una partición extendida para crear la partición lógica.")
                    return
    # escribir los cambios en el archivo
    try:
        with open(path, "rb+") as file:
            file.write(mbr.__bytes__())
            if type == 'P':
                print("\t> FDISK: Partición primaria creada exitosamente")
                salida.append(">>>> FDISK: Partición primaria creada exitosamente <<<<")
                return
            if type == 'E':
                file.seek(ebr.part_start)
                file.write(ebr.__bytes__())
                print("\t> FDISK: Partición extendida creada exitosamente")
                salida.append(">>>> FDISK: Partición extendida creada exitosamente <<<<")
                return
    except Exception as e:
        print(e)
        print("\tERROR: Error al crear la partición en el disco: "+path)
        salida.append("ERROR: Error al crear la partición en el disco: "+path)
        return
    
    
    
def particionLogica(particion, path, size, name, fit_disco, fit):
    
    ebr_list = leer_ebr_desde_archivo(path, particion.part_start)
    
    size_deleted_partitions = []
    tmp_size = particion.part_start
    nombres = []
    escribir_extra = False
    for particion_logica in ebr_list:
        if particion_logica.part_status == 'D':
            size_deleted_partitions.append(particion_logica.part_size)
        else:
            nombres.append(particion_logica.part_name)
    if name in nombres:
        print("\tERROR: Ya existe una partición con el nombre: "+name)
        salida.append("ERROR: Ya existe una partición con el nombre: "+name)
        return
    logica = EBR()
    tmp = EBR()
    if fit_disco == "FF":
        # Crea la particion en el primer espacio Libre
        for particion_logica in ebr_list:
            if particion_logica.part_status == '0':
                escribir_extra = True
                logica.part_status = '1'
                logica.part_fit = fit
                logica.part_start = tmp_size
                logica.part_size = size
                logica.part_next = tmp_size + size
                logica.part_name = name

               
                tmp.part_status = '0'
                tmp.part_fit = 'WF'
                tmp.part_start = logica.part_next
                tmp.part_size = 0
                tmp.part_next = 1234
                tmp.part_name = ''
                break
            elif particion_logica.part_status == '1':
                tmp_size += particion_logica.part_size
            elif particion_logica.part_status == 'D':
                size_deleted_partitions = size_deleted_partitions[0]
                if size_deleted_partitions >= size:
                    logica.part_status = '1'
                    logica.part_fit = fit
                    logica.part_start = tmp_size
                    logica.part_size = size
                    logica.part_next = tmp_size + size
                    logica.part_name = name
                    break
                else:
                    print("\tERROR: No hay espacio suficiente para crear la partición.")
                    salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                    return
    elif fit_disco == "BF":
        for particion_logica in ebr_list:
            if particion_logica.part_status == '0':
                escribir_extra  = True
                logica.part_status = '1'
                logica.part_fit = fit
                logica.part_start = tmp_size
                logica.part_size = size
                logica.part_next = tmp_size + size
                logica.part_name = name

                tmp.part_status = '0'
                tmp.part_fit = 'WF'
                tmp.part_start = logica.part_next
                tmp.part_size = 0
                tmp.part_next = 1234
                tmp.part_name = ''
                break
            elif particion_logica.part_status == '1':
                tmp_size += particion_logica.part_size
            elif particion_logica.part_status == 'D':
                size_deleted_partitions.sort()
                size_deleted_partitions = size_deleted_partitions[0]
                if size_deleted_partitions >= size:
                    logica.part_status = '1'
                    logica.part_fit = fit
                    logica.part_start = tmp_size
                    logica.part_size = size
                    logica.part_next = tmp_size + size
                    logica.part_name = name
                    break
                else:
                    print("\tERROR: No hay espacio suficiente para crear la partición.")
                    salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                    return
    elif fit_disco == "WF":
        for particion_logica in ebr_list:
            if particion_logica.part_status == '0':
                escribir_extra = True

                logica.part_status = '1'
                logica.part_fit = fit
                logica.part_start = tmp_size
                logica.part_size = size
                logica.part_next = tmp_size + size
                logica.part_name = name

                tmp.part_status = '0'
                tmp.part_fit = 'WF'
                tmp.part_start = logica.part_next
                tmp.part_size = 0
                tmp.part_next = 1234
                tmp.part_name = ''
                break
            elif particion_logica.part_status == '1':
                tmp_size += particion_logica.part_size
            elif particion_logica.part_status == 'D':
                size_deleted_partitions.sort(reverse=True)
                size_deleted_partitions = size_deleted_partitions[0]
                if size_deleted_partitions >= size:
                    logica.part_status = '1'
                    logica.part_fit = fit
                    logica.part_start = tmp_size
                    logica.part_size = size
                    logica.part_next = tmp_size + size
                    logica.part_name = name
                    break
                else:
                    print("\tERROR: No hay espacio suficiente para crear la partición.")
                    salida.append("ERROR: No hay espacio suficiente para crear la partición.")
                    return

    try:
        with open(path, "rb+") as file:
            file.seek(tmp_size)
            file.write(logica.__bytes__())
            if escribir_extra:
                file.seek(tmp_size + size)
                file.write(tmp.__bytes__())
            print("\t> FDISK","Partición logica", name, "creada exitosamente")
            salida.append(">>>> FDISK: Partición logica "+name+" creada exitosamente <<<<")
            return
    except Exception as e:
        print(e)
        print("\tError: Error al crear la partición en el disco: "+path)
        salida.append("Error: Error al crear la partición en el disco: "+path)
        return
    

def imprimirMBR(path):
    mbr = MBR()
    ebr = EBR()
    try:
        with open(path, "rb") as file:
            mbr_data = file.read()
            mbr.mbr_tamano = struct.unpack("<i", mbr_data[:4])[0]
            mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
            mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
            mbr.disk_fit = mbr_data[12:14].decode('utf-8')

            partition_size = struct.calcsize("<iii16s")*4
            partition_data = mbr_data[14:14 + partition_size]
            mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
            mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
            mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
            mbr.mbr_Partition_4.__setstate__(partition_data[84:112])

            # Si hay EBR en cualquiera de las particiones leerlos
            if mbr.mbr_Partition_1.part_type == 'E':
                file.seek(mbr.mbr_Partition_1.part_start)
                ebr_data = file.read()
                ebr.__setstate__(ebr_data)
            if mbr.mbr_Partition_2.part_type == 'E':
                file.seek(mbr.mbr_Partition_2.part_start)
                ebr_data = file.read()
                ebr.__setstate__(ebr_data)
            if mbr.mbr_Partition_3.part_type == 'E':
                file.seek(mbr.mbr_Partition_3.part_start)
                ebr_data = file.read()
                ebr.__setstate__(ebr_data)
            if mbr.mbr_Partition_4.part_type == 'E':
                file.seek(mbr.mbr_Partition_4.part_start)
                ebr_data = file.read()
                ebr.__setstate__(ebr_data)



    except Exception as e:
        print(e)

    print("Tamaño: "+str(mbr.mbr_tamano))
    print("Fecha: "+str(mbr.mbr_fecha_creacion))
    print("Signature: "+str(mbr.mbr_disk_signature))
    print("Fit: "+str(mbr.disk_fit))
    print("Particion 1:")
    print("\tStatus: "+str(mbr.mbr_Partition_1.part_status))
    print("\tType: "+str(mbr.mbr_Partition_1.part_type))
    print("\tFit: "+str(mbr.mbr_Partition_1.part_fit))
    print("\tStart: "+str(mbr.mbr_Partition_1.part_start))
    print("\tSize: "+str(mbr.mbr_Partition_1.part_size))
    print("\tName: "+str(mbr.mbr_Partition_1.part_name))
    print("Particion 2:")
    print("\tStatus: "+str(mbr.mbr_Partition_2.part_status))
    print("\tType: "+str(mbr.mbr_Partition_2.part_type))
    print("\tFit: "+str(mbr.mbr_Partition_2.part_fit))
    print("\tStart: "+str(mbr.mbr_Partition_2.part_start))
    print("\tSize: "+str(mbr.mbr_Partition_2.part_size))
    print("\tName: "+str(mbr.mbr_Partition_2.part_name))
    print("Particion 3:")
    print("\tStatus: "+str(mbr.mbr_Partition_3.part_status))
    print("\tType: "+str(mbr.mbr_Partition_3.part_type))
    print("\tFit: "+str(mbr.mbr_Partition_3.part_fit))
    print("\tStart: "+str(mbr.mbr_Partition_3.part_start))
    print("\tSize: "+str(mbr.mbr_Partition_3.part_size))
    print("\tName: "+str(mbr.mbr_Partition_3.part_name))
    print("Particion 4:")
    print("\tStatus: "+str(mbr.mbr_Partition_4.part_status))
    print("\tType: "+str(mbr.mbr_Partition_4.part_type))
    print("\tFit: "+str(mbr.mbr_Partition_4.part_fit))
    print("\tStart: "+str(mbr.mbr_Partition_4.part_start))
    print("\tSize: "+str(mbr.mbr_Partition_4.part_size))
    print("\tName: "+str(mbr.mbr_Partition_4.part_name))


def leer_ebr_desde_archivo(path, inicio):
    tmp_size = inicio
    ebr_list = []
    with open(path, "rb+") as file:
        while True:
            file.seek(tmp_size)
            ebr_data = file.read()  # Leer EBR
            ebr = EBR()
            ebr_list.append(ebr)
            ebr.__setstate__(ebr_data)
            if ebr.part_next == 1234:
                break
            tmp_size = ebr.part_next
    return ebr_list

def leer_particiones_desde_archivo(path):
    try:
        mbr = MBR()
        with open(path, "rb") as file:
            mbr_data = file.read()
            mbr.mbr_tamano = struct.unpack("<i", mbr_data[0:4])[0]
            mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
            mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
            mbr.disk_fit = mbr_data[12:14].decode("utf-8")

            partition_size = struct.calcsize("<iii16s")*4
            partition_data = mbr_data[14:14 + partition_size]
            mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
            mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
            mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
            mbr.mbr_Partition_4.__setstate__(partition_data[84:112])
    except Exception as e:
        print(e)

    particiones = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]

    return particiones

def eliminarParticion(name, path):

    try:
        mbr = MBR()
        with open(path, "rb") as file:
            mbr_data = file.read()
            mbr.mbr_tamano = struct.unpack("<i", mbr_data[0:4])[0]
            mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
            mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
            mbr.disk_fit = mbr_data[12:14].decode("utf-8")

            partition_size = struct.calcsize("<iii16s")*4
            partition_data = mbr_data[14:14 + partition_size]
            mbr.mbr_Partition_1.__setstate__(partition_data[0:28]) 
            mbr.mbr_Partition_2.__setstate__(partition_data[28:56]) 
            mbr.mbr_Partition_3.__setstate__(partition_data[56:84]) 
            mbr.mbr_Partition_4.__setstate__(partition_data[84:112])
    except Exception as e:
        print(e)

    particiones = [mbr.mbr_Partition_1, mbr.mbr_Partition_2, mbr.mbr_Partition_3, mbr.mbr_Partition_4]
    
    lista_nombres = []
    inicio_extendida = 0
    for particion in particiones:
        lista_nombres.append(particion.part_name)
        if particion.part_type == 'E':
            inicio_extendida = particion.part_start

    if name not in lista_nombres:
        eliminarLogicas(path,inicio_extendida, name)
    else:
        punto_partida = 0
        tamanio = 0
        for particion in particiones:
            if particion.part_name == name:
                particion.part_status = 'D'
                particion.part_type = particion.part_type
                particion.part_fit = particion.part_fit
                particion.part_start = particion.part_start
                particion.part_size = particion.part_size
                particion.part_name = particion.part_name
                punto_partida = particion.part_start
                tamanio = particion.part_size
                break

        try:
            with open(path, "rb+") as file:
                file.write(mbr.__bytes__())
                file.seek(punto_partida)
                file.write(b'\x00'*tamanio)
                print("\t> FDISK: Partición eliminada exitosamente")
                salida.append(">>>> FDISK: Partición eliminada exitosamente <<<<")
                return
        except Exception as e:
            print(e)
            print("\tERROR: Error al eliminar la partición en el disco: "+path)
            salida.append("ERROR: Error al eliminar la partición en el disco: "+path)
            return

def eliminarLogicas(path, inicio, name):
    ebr_list = leer_ebr_desde_archivo(path, inicio)

    lista_nombres = []
    for ebr in ebr_list:
        lista_nombres.append(ebr.part_name)

    if name not in lista_nombres:
        print("\tERROR: No existe una partición con el nombre: "+name)
        salida.append("ERROR: No existe una partición con el nombre: "+name)
        return

    for ebr in ebr_list:
        if ebr.part_name == name:
            ebr.part_status = 'D'
            ebr.part_fit = ebr.part_fit
            ebr.part_start = ebr.part_start
            ebr.part_size = ebr.part_size
            ebr.part_next = ebr.part_start + ebr.part_size
            ebr.part_name = ebr.part_name
            break
    try:
        with open(path, "rb+") as file:
            for ebr in ebr_list:
                file.seek(ebr.part_start)
                file.write(ebr.__bytes__())
                file.write(b'\x00'*ebr.part_size)
            print("\t> FDISK: Partición Logica eliminada exitosamente")
            salida.append(">>>> FDISK: Partición Logica eliminada exitosamente <<<<")
            return
    except Exception as e:
        print(e)
        print("\tERROR: Error al eliminar la partición en el disco: "+path)
        salida.append("ERROR: Error al eliminar la partición en el disco: "+path)
        return
    
def cmd_mount(path, name):
    print("\t> MOUNT: Montando partición...")
    salida.append(">>>> MOUNT: Montando partición... <<<<")
    particiones = leer_particiones_desde_archivo(path)
    lista_nombres = []
    index = 0
    for particion in particiones:
        index += 1
        if particion.part_name == name:
            break
    for particion in particiones:
        lista_nombres.append(particion.part_name)

    if name not in lista_nombres:
        print("\tERROR: No existe una partición con el nombre: "+name)
        salida.append("ERROR: No existe una partición con el nombre: "+name)
        return
    else:
        nombre_disco = os.path.splitext(os.path.basename(path))[0]
        carnet = '00'
        id = carnet + str(index) + nombre_disco 
        
        if id in particiones_montadas:
            print("\tERROR: La partición ya se encuentra montada.")
            salida.append("ERROR: La partición ya se encuentra montada.")
            return
        else:
            dict = {'id': id, 'path': path, 'name': name}
            particiones_montadas.append(dict)
            print("\t> MOUNT: Partición montada exitosamente.")
            salida.append(">>>> MOUNT: Partición montada exitosamente. <<<<")
            print("\t> MOUNT: Particiones montadas de momento: ")
            salida.append(">>>> MOUNT: Particiones montadas de momento: <<<<")
            for i in particiones_montadas:
                for key in i:
                    print("\t\t"+key+": "+i[key])
                    salida.append("\t\t"+key+": "+i[key])
                    
                print("\t\t------------------------")
                salida.append("\t\t------------------------")

def cmd_unmount(id):
    print("\t> UNMOUNT: Desmontando partición...")
    salida.append(">>>> UNMOUNT: Desmontando partición... <<<<")
    aux_nombres = []
    particion_actual = None
    for particion in particiones_montadas:
        aux_nombres.append(particion.get('id'))
    
    for particion in particiones_montadas:
        if particion.get('id') == id:
            particion_actual = particion
            break

    if id not in aux_nombres:
        print("\tERROR: No existe una partición montada con el id: "+id)
        salida.append("ERROR: No existe una partición montada con el id: "+id)
        return
    else:
        particiones_montadas.remove(particion_actual)
        print("\t> UNMOUNT: Partición desmontada exitosamente.")
        salida.append(">>>> UNMOUNT: Partición desmontada exitosamente. <<<<")
        print("\t> UNMOUNT: Particiones montadas de momento: ")
        salida.append(">>>> UNMOUNT: Particiones montadas de momento: <<<<")
        for i in particiones_montadas:
                for key in i:
                    print("\t\t"+key+": "+i[key])
                    salida.append("\t\t"+key+": "+i[key])
                    
                print("\t\t------------------------")
                salida.append("\t\t------------------------")

def leer_mbr_desde_archivo(path):
    mbr = MBR()
    try:

        with open(path, "rb") as file:
            mbr_data = file.read()
            mbr.mbr_tamano = struct.unpack("<i", mbr_data[0:4])[0]
            mbr.mbr_fecha_creacion = struct.unpack("<i", mbr_data[4:8])[0]
            mbr.mbr_disk_signature = struct.unpack("<i", mbr_data[8:12])[0]
            mbr.disk_fit = mbr_data[12:14].decode("utf-8")
    except Exception as e:
        print(e)

    return mbr

def cmd_mkfs(id, type, fs):
    
    print("\t> MKFS: Formateando partición...")
    salida.append(">>>> MKFS: Formateando partición... <<<<")
    print("\t> MKFS: Tipo de formateo: "+fs)
    salida.append(">>>> MKFS: Tipo de formateo: "+fs+" <<<<")
    
    path_disco = ''
    nombre_particion = ''
    for i in particiones_montadas:
        if i['id'] == id:
            path_disco = i['path']
            nombre_particion = i['name']
            break
    
    if path_disco == '':
        print("\tERROR: No existe una partición montada con el id: "+id)
        return
    
    particiones = leer_particiones_desde_archivo(path_disco)

    size_particion = 0
    part = None
    for particion in particiones:
        if particion.part_name == nombre_particion:
            size_particion = particion.part_size
            part = particion
            break

    n = 0
    size_super_bloque = struct.calcsize("<iiiiiddiiiiiiiiii")
    size_inodos = struct.calcsize("<iiiddd15ici")
    size_bloques_archivo = len(bytes(BloquesArchivos()))
    size_journaling = sys.getsizeof(Journaling())

    if fs == "2FS":
        n = (size_particion - size_super_bloque) // (4 + size_inodos + 3*size_bloques_archivo)
    elif fs == "3FS":
        n = (size_particion - size_super_bloque) // (4 + size_inodos + 3*size_bloques_archivo + size_journaling)

    super = SuperBloque()
    super.s_inodes_count = super.s_free_inodes_count = n
    super.s_blocks_count = super.s_free_blocks_count = 3*n
    super.s_mtime = int(time.time())
    super.s_umtime = int(time.time())
    super.s_mnt_count = 1


    if fs == "2FS":
        super.s_filesystem_type = 2
        ext2(super, part, n, path_disco)
        print("\t> MKFS: Formateo ext2 exitoso.")
        salida.append(">>>> MKFS: Formateo ext2 exitoso. <<<<")
    elif fs == "3FS":
        super.s_filesystem_type = 3
        #ext3(super, part, n, path_disco)
        print("\t> MKFS: Formateo ext3 exitoso.")
        salida.append(">>>> MKFS: Formateo ext3 exitoso. <<<<")

    # Size(Particion) - Size(SuperBloque)
    # 4 + Size(Inodo) + 3*Size(Bloque)

def ext2(super, particion, n, path):
    size_super_bloque = struct.calcsize("<iiiiiddiiiiiiiiii")
    size_inodos = struct.calcsize("<iiiddd15ici")
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))

    super.s_bm_inode_start = particion.part_start + size_super_bloque 
    super.s_bm_block_start = super.s_bm_inode_start + n
    super.s_inode_start = super.s_bm_block_start + (3 * n)
    super.s_block_start = super.s_bm_inode_start + (n * size_inodos)

    # Escribir SuperBloque
    try:
        with open(path, "rb+") as bfile:
            bfile.seek(particion.part_start)
            bfile.write(bytes(super))

            zero = b'0'
            bfile.seek(super.s_bm_inode_start)
            bfile.write(zero*n)

            bfile.seek(super.s_bm_block_start)
            bfile.write(zero * (3 * n))

            inode = Inodos()
            bfile.seek(super.s_inode_start)
            for _ in range(n):
                bfile.write(bytes(inode))

            folder = BloquesCarpetas()
            bfile.seek(super.s_block_start)
            for _ in range(3 * n):
                bfile.write(bytes(folder))

    except Exception as e:
        print(e)
        print("\tERROR: Error al escribir el super bloque en el disco: "+path)
        salida.append("ERROR: Error al escribir el super bloque en el disco: "+path)
        return
    
    try:
        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))
        with open(path, "rb") as archivo:
            archivo.seek(particion.part_start)
            archivo.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[:4])[0]
        super_tmp.s_inodes_count = struct.unpack("<i", recuperado[4:8])[0]
        super_tmp.s_blocks_count = struct.unpack("<i", recuperado[8:12])[0]
        super_tmp.s_free_blocks_count = struct.unpack("<i", recuperado[12:16])[0]
        super_tmp.s_free_inodes_count = struct.unpack("<i", recuperado[16:20])[0]
        super_tmp.s_mtime = struct.unpack("<d", recuperado[20:28])[0]
        super_tmp.s_umtime = struct.unpack("<d", recuperado[28:36])[0]
        super_tmp.s_mnt_count = struct.unpack("<i", recuperado[36:40])[0]
        super_tmp.s_magic = struct.unpack("<i", recuperado[40:44])[0]
        super_tmp.s_inode_size = struct.unpack("<i", recuperado[44:48])[0]
        super_tmp.s_block_size = struct.unpack("<i", recuperado[48:52])[0]
        super_tmp.s_first_ino = struct.unpack("<i", recuperado[52:56])[0]
        super_tmp.s_first_blo = struct.unpack("<i", recuperado[56:60])[0]
        super_tmp.s_bm_inode_start = struct.unpack("<i", recuperado[60:64])[0]
        super_tmp.s_bm_block_start = struct.unpack("<i", recuperado[64:68])[0]
        super_tmp.s_inode_start = struct.unpack("<i", recuperado[68:72])[0]
        super_tmp.s_block_start = struct.unpack("<i", recuperado[72:76])[0] 
    except Exception as e:
        print(e)

    inode = Inodos()
    inode.i_uid = 1
    inode.i_gid = 1
    inode.i_size = 0
    inode.i_atime = super.s_umtime
    inode.i_ctime = super.s_umtime
    inode.i_mtime = super.s_umtime
    inode.i_type = 0
    inode.i_perm = 664
    inode.i_block[0] = 0 #porque es una carpeta

    fb = BloquesCarpetas()
    fb.b_content[0].b_name = "."
    fb.b_content[0].b_inodo = 0
    fb.b_content[1].b_name = ".."
    fb.b_content[1].b_inodo = 0
    fb.b_content[2].b_name = "user.txt"
    fb.b_content[2].b_inodo = 1

    data = "1,G,root\n1,U,root,root,123\n"
    inode_tmp = Inodos()
    inode_tmp.i_uid = 1
    inode_tmp.i_gid = 1
    inode_tmp.i_size = len(data) + size_bloques_carpetas
    inode_tmp.i_atime = super.s_umtime
    inode_tmp.i_ctime = super.s_umtime
    inode_tmp.i_mtime = super.s_umtime
    inode_tmp.i_type = 1
    inode_tmp.i_perm = 664
    inode_tmp.i_block[0] = 1 #porque es un archivo

    inode.i_size = inode_tmp.i_size + size_bloques_carpetas + size_inodos

    fileb = BloquesArchivos()
    fileb.b_content = data

    try:
        with open(path, "rb+") as bfiles:
            bfiles.seek(super.s_bm_inode_start)
            bfiles.write(b'1' * 2)

            bfiles.seek(super.s_bm_block_start)
            bfiles.write(b'1' * 2)

            bfiles.seek(super.s_inode_start)
            bfiles.write(bytes(inode))
            bfiles.write(bytes(inode_tmp))

            bfiles.seek(super.s_block_start)
            bfiles.write(bytes(fb))
            bfiles.write(bytes(fileb))

    except Exception as e:
        print(e)
    