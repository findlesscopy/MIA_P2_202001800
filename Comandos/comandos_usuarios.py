from Estructuras.User import *
from Estructuras.Bloques import *
from Estructuras.MBR import *
from Global.Global import *
from Estructuras.SuperBloque import *

actualSesion = Sesion()
logueado = UsuarioActivo()

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

def cmd_login(user, password, id):
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))
    try:
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == id:
                #print("\tLogin: Se encontro la particion")
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                particion_actual = par
                break

        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))

        with open(path_particion, "rb") as file:
            file.seek(particion_actual.part_start)
            file.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[0:4])[0]
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

        fb = BloquesArchivos()
        bytes_bloque_archivo = bytes(fb)
        usuariostxt = bytearray(len(bytes_bloque_archivo))
        with open(path_particion, "rb") as rfile:
            rfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            rfile.readinto(usuariostxt)

        fb.b_content = struct.unpack("<64s", usuariostxt[0:64])[0]

        txt = usuariostxt.decode('ascii')
        vctr = get_elements(txt, '\n')


        for line in vctr:
            if line[2] == 'U':
                in_ = get_elements(line, ',')
                if in_[3] == user and in_[4]:
                    print("\tLOGIN: Usuario ", user, " logueado correctamente")
                    global logueado
                    logueado.id = id
                    logueado.user = user
                    logueado.password = password
                    logueado.uid = int(in_[0])

                    return True
        print("\tLOGIN: Usuario ", user, " no encontrado")
        return False
    except Exception as e:
        print("\tLOGIN: Error al leer el archivo de usuarios")
        return False



def get_elements(txt, c):
    v = []
    line = ""
    if c == ',':
        txt += ','
    for i in txt:
        if i == c:
            v.append(line)
            line = ""
            continue
        line += i

    if not v:
        print("\tERROR: no existe un archivo")

    return v

def cmd_logout():
    global logueado
    print("\tLOGOUT: Usuario ", logueado.user, " deslogueado correctamente")
    global actualSesion
    logueado = UsuarioActivo()
    actualSesion = Sesion()
    return False

def cmd_mkgrp(nombre):
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))

    try:
        global logueado 
        if not logueado.user == "root":
            print("\tMKGRP: No se puede crear el grupo, no tiene permisos de administrador")
            return False
        
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == logueado.id:
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                particion_actual = par
                break

        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))
        with open(path_particion, "rb") as file:
            file.seek(particion_actual.part_start)
            file.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[0:4])[0]
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

        fb = BloquesArchivos()
        bytes_bloque_archivo = bytes(fb)
        usuariostxt = bytearray(len(bytes_bloque_archivo))
        with open(path_particion, "rb") as rfile:
            rfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            rfile.readinto(usuariostxt)

        fb.b_content = struct.unpack("<64s", usuariostxt[0:64])[0]

        txt = usuariostxt.decode('ascii')
        vctr = get_elements(txt, '\n')
        c = 0
        txttmp = ""
        for line in vctr:
            if line[2] == 'G':
                txttmp += line + '\n'
                c += 1
                in_ = line.split(',')
                if in_[2] == nombre:
                    if line[0] == '0':
                        pass
                    else:
                        print("\tMKGRP: No se puede crear el grupo, ya existe un grupo con el nombre ", nombre)
                        return False
            else:
                txttmp += line + '\n'

        txttmp += f"{c+1},G,{nombre}\n"
        fb.b_content = txttmp

        print("ESTE ES EL TXTTMP ", fb.b_content)
        print("-----------------------")
        with open(path_particion, "rb+") as wfile:
            wfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            wfile.write(bytes(fb))
            print("\tMKGRP: Grupo ", nombre, " creado correctamente")

    except Exception as e:
        print("\tMKGRP: Error al leer el archivo de usuarios")
        return False

def cmd_rmgrp(nombre):
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))

    try:
        global logueado 
        if not logueado.user == "root":
            print("\tMKGRP: No se puede crear el grupo, no tiene permisos de administrador")
            return False
        
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == logueado.id:
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                particion_actual = par
                break

        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))
        with open(path_particion, "rb") as file:
            file.seek(particion_actual.part_start)
            file.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[0:4])[0]
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

        fb = BloquesArchivos()
        bytes_bloque_archivo = bytes(fb)
        usuariostxt = bytearray(len(bytes_bloque_archivo))
        with open(path_particion, "rb") as rfile:
            rfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            rfile.readinto(usuariostxt)

        fb.b_content = struct.unpack("<64s", usuariostxt[0:64])[0]

        txt = usuariostxt.decode('ascii')
        vctr = get_elements(txt, '\n')
        c = 0
        txttmp = ""
        exist = False
        for line in vctr:
            if(line[2] == 'G' and line[0] != '0'):
                in_ = get_elements(line, ',')
                if in_[2] == nombre:
                    exist = True
                    txttmp += f"0,G,{in_[2]}\n"
                    continue
                else:
                    txttmp += line + '\n'
            else:
                txttmp += line + '\n'

        if not exist:
            print("\tRMGRP: No se puede eliminar el grupo, no existe un grupo con el nombre ", nombre)
            return False
        
        fb.b_content = txttmp
        with open(path_particion, "rb+") as wfile:
            wfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            wfile.write(bytes(fb))
            print("\tRMGRP: Grupo ", nombre, " eliminado correctamente")

    except Exception as e:
        print("\tRMGRP: Error al leer el archivo de usuarios")
        return False
    
def cmd_mkusr(user, pwd, grp):
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))

    try:
        global logueado 
        if not logueado.user == "root":
            print("\tMKGRP: No se puede crear el grupo, no tiene permisos de administrador")
            return False
        
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == logueado.id:
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                particion_actual = par
                break

        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))
        with open(path_particion, "rb") as file:
            file.seek(particion_actual.part_start)
            file.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[0:4])[0]
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

        fb = BloquesArchivos()
        bytes_bloque_archivo = bytes(fb)
        usuariostxt = bytearray(len(bytes_bloque_archivo))
        with open(path_particion, "rb") as rfile:
            rfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            rfile.readinto(usuariostxt)

        fb.b_content = struct.unpack("<64s", usuariostxt[0:64])[0]

        txt = usuariostxt.decode('ascii')
        vctr = get_elements(txt, '\n')
        c = 0
        txttmp = ""
        for line in vctr:
            if(line[2] == 'U' and line[0] != '0'):
                c += 1
                in_ = get_elements(line, ',')
                if in_[3] == user:
                    print("\tMKUSR: No se puede crear el usuario, ya existe un usuario con el nombre ", user)
                    return False
                else:
                    txttmp += line + '\n'
            else:
                txttmp += line + '\n'

        txttmp += f"{c+1},U,{grp},{user},{pwd}\n"
        fb.b_content = txttmp

        print(txttmp)

        with open(path_particion, "rb+") as wfile:
            wfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            wfile.write(bytes(fb))
            print("\tMKUSR: Usuario ", user, " creado correctamente")
            
    except Exception as e:
        print("\tMKUSR: Error al leer el archivo de usuarios")
        return False
    
def cmd_rmusr(nombre):
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))

    try:
        global logueado 
        if not logueado.user == "root":
            print("\RMUSR: No se puede eliminar el grupo, no tiene permisos de administrador")
            return False
        
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == logueado.id:
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                particion_actual = par
                break

        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))
        with open(path_particion, "rb") as file:
            file.seek(particion_actual.part_start)
            file.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[0:4])[0]
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

        fb = BloquesArchivos()
        bytes_bloque_archivo = bytes(fb)
        usuariostxt = bytearray(len(bytes_bloque_archivo))
        with open(path_particion, "rb") as rfile:
            rfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            rfile.readinto(usuariostxt)

        fb.b_content = struct.unpack("<64s", usuariostxt[0:64])[0]

        txt = usuariostxt.decode('ascii')
        vctr = get_elements(txt, '\n')
        txttmp = ""
        exist = False
        for line in vctr:
            if(line[2] == 'U' and line[0] != '0'):
                in_ = get_elements(line, ',')
                if in_[3] == nombre:
                    exist = True
                    txttmp += f"0,U,{in_[2]},{in_[3]},{in_[4]}\n"
                    continue
                else:
                    txttmp += line + '\n'
            else:
                txttmp += line + '\n'

        #print(exist)
        if not exist:
            print("\tRMUSR: No se puede eliminar el usuario, no existe un usuario con el nombre ", nombre)
            return False
        
        fb.b_content = txttmp
        with open(path_particion, "rb+") as wfile:
            wfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            wfile.write(bytes(fb))
            print("\tRMUSR: Usuario ", nombre, " eliminado correctamente")

    except Exception as e:
        print("\tRMUSR: Error al leer el archivo de usuarios")
        print(e)
        return False
    
def imprimirtxt():
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))

    try:
        global logueado 
        if not logueado.user == "root":
            print("\RMUSR: No se puede eliminar el grupo, no tiene permisos de administrador")
            return False
        
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == logueado.id:
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                particion_actual = par
                break

        super_tmp = SuperBloque()
        bytes_super_bloque = bytes(super_tmp)

        recuperado = bytearray(len(bytes_super_bloque))
        with open(path_particion, "rb") as file:
            file.seek(particion_actual.part_start)
            file.readinto(recuperado)

        # Recuperar SuperBloque
        super_tmp.s_filesystem_type = struct.unpack("<i", recuperado[0:4])[0]
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

        fb = BloquesArchivos()
        bytes_bloque_archivo = bytes(fb)
        usuariostxt = bytearray(len(bytes_bloque_archivo))
        with open(path_particion, "rb") as rfile:
            rfile.seek(super_tmp.s_block_start + size_bloques_carpetas)
            rfile.readinto(usuariostxt)

        fb.b_content = struct.unpack("<64s", usuariostxt[0:64])[0]

        txt = usuariostxt.decode('ascii')
        vctr = get_elements(txt, '\n')
        for line in vctr:
            print(line)

    except Exception as e:
        print("\tRMUSR: Error al leer el archivo de usuarios")
        print(e)
        return False