from Global.Global import particiones_montadas
from Estructuras.MBR import *
from Estructuras.EBR import *
from Estructuras.SuperBloque import *
from Estructuras.Bloques import *
from Estructuras.Inodos import *
from utils import *
import boto3
import os
import graphviz
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

load_dotenv()
aws_access_key_id = os.getenv("KEY_ID")
aws_secret_access_key = os.getenv("SECRET_KEY")
bucket_name = "front-proyecto2-mia-202001800"

@cross_origin()
def cmd_reporte_mbr(path, id):
    
    print("\t> REP: Generando reporte mbr...")
    salida.append("REP: Generando reporte mbr...")
    #buscar en particiones montadas el id
    mbr = MBR()
    particiones =   []
    esta = False
    for particion in particiones_montadas:
        nombre = particion.get('id')
        if nombre == id:
            esta = True
            #print("Se encontro la particion")
            dir = particion.get('path')
            particiones  = leer_particiones_desde_archivo(dir) 
            mbr = leer_mbr_desde_archivo(dir)

    if esta == False:
        print("\tERROR: No se encontro la particion montada.")
        salida.append("ERROR: No se encontro la particion montada.")
        return 

    dot = "digraph G {\n"
    dot += "node [shape=plaintext]\n"
    dot += "graph [rankdir=LR]\n"
    dot += "mbr [label=<\n"
    dot += "<table border='0' cellborder='1' cellspacing='0'>\n"
    dot += "<tr><td colspan='2' bgcolor='lightblue'><b>MBR</b></td></tr>\n"
    dot += "<tr><td><b>Nombre</b></td><td><b>Valor</b></td></tr>\n"
    dot += "<tr><td>mbr_tamano</td><td>{}</td></tr>\n".format(mbr.mbr_tamano)
    dot += "<tr><td>mbr_fecha_creacion</td><td>{}</td></tr>\n".format(mbr.mbr_fecha_creacion)
    dot += "<tr><td>mbr_disk_signature</td><td>{}</td></tr>\n".format(mbr.mbr_disk_signature)
    dot += "<tr><td>disk_fit</td><td>{}</td></tr>\n".format(mbr.disk_fit)
    
    #particiones
    index1 = 0
    for part in particiones:
        index1 += 1
        dot += "<tr><td colspan='2' bgcolor='lightblue'><b>Particion {}</b></td></tr>\n".format(index1)
        dot += "<tr><td><b>Nombre</b></td><td><b>Valor</b></td></tr>\n"
        dot += "<tr><td>part_status</td><td>{}</td></tr>\n".format(part.part_status)
        dot += "<tr><td>part_type</td><td>{}</td></tr>\n".format(part.part_type)
        dot += "<tr><td>part_fit</td><td>{}</td></tr>\n".format(part.part_fit)
        dot += "<tr><td>part_start</td><td>{}</td></tr>\n".format(part.part_start)
        dot += "<tr><td>part_size</td><td>{}</td></tr>\n".format(part.part_size)
        dot += "<tr><td>part_name</td><td>{}</td></tr>\n".format(part.part_name)

        if part.part_type == 'E':
            if part.part_status == 'D':
                pass
            else:
                ebr_list = leer_ebr_desde_archivo(dir, part.part_start)
                index = 0
                for ebr in ebr_list:
                    index += 1
                    if ebr.part_next == 1234:
                        break
                    dot += "<tr><td colspan='2' bgcolor='lightyellow'><b>Particion Logica {}</b></td></tr>\n".format(index)
                    dot += "<tr><td><b>Nombre</b></td><td><b>Valor</b></td></tr>\n"
                    dot += "<tr><td>part_status</td><td>{}</td></tr>\n".format(ebr.part_status)
                    dot += "<tr><td>part_fit</td><td>{}</td></tr>\n".format(ebr.part_fit)
                    dot += "<tr><td>part_start</td><td>{}</td></tr>\n".format(ebr.part_start)
                    dot += "<tr><td>part_size</td><td>{}</td></tr>\n".format(ebr.part_size)
                    dot += "<tr><td>part_next</td><td>{}</td></tr>\n".format(ebr.part_next)
                    dot += "<tr><td>part_name</td><td>{}</td></tr>\n".format(ebr.part_name)
                
        else:
            continue
                
    
    dot += "</table>\n"
    dot += ">];\n"
    dot += "}"

    nombre_archivo = os.path.splitext(os.path.basename(path))[0]
    graph = graphviz.Source(dot)
    graph.render(nombre_archivo, format='svg')
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.upload_file(nombre_archivo + ".svg", bucket_name, "/reportes/"+nombre_archivo + ".svg")
    #salida.append(dot)

    print("\t> REP: Reporte mbr generado")
    salida.append("REP: Reporte mbr generado")


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



def cmd_reporte_disk(path, id):
    print("\t> REP: Generando reporte disk...")
    salida.append("REP: Generando reporte disk...")
    #buscar en particiones montadas el id
    mbr = MBR()
    particiones =   []
    for particion in particiones_montadas:
        nombre = particion.get('id')
        if nombre == id:
            #print("Se encontro la particion")
            dir = particion.get('path')
            particiones  = leer_particiones_desde_archivo(dir) 
            mbr = leer_mbr_desde_archivo(dir)

    size_disco = mbr.mbr_tamano

    # hacer la representación visual del disco con tamaño de particiones y espacio libre

    dot = "digraph G {\n"
    dot += "node [shape=plaintext]\n"
    dot += "graph [rankdir=LR]\n"
    dot += "disk [label=<\n"
    dot += "<table border='0' cellborder='1' cellspacing='0' cellpadding='50'>\n"
    dot += "<tr><td colspan='2' bgcolor='lightblue'><b>MBR ocupa el {}% del disco</b> </td>\n".format(126*100/size_disco)

    for part in particiones:
        if part.part_type == 'E':
            if part.part_status == 'D':
                dot += "<td colspan='2' bgcolor='lightblue'><b>Partición </b><br/><b>Ocupa el {}% del disco</b></td>\n".format(part.part_size*100/size_disco)
            else:
                dot += "<td colspan='2' bgcolor='lightblue'><b>Partición Extendida</b><br/><b>Ocupa el {}% del disco</b></td>\n".format(part.part_size*100/size_disco)
                ebr_list = leer_ebr_desde_archivo(dir, part.part_start)
                dot += "<td>\n<table border='0' cellborder='1' cellspacing='0' cellpadding='50'><tr>"
                for ebr in ebr_list:
                    if ebr.part_next == 1234:
                        break
                    dot += "<td bgcolor='lightyellow'>"
                    dot += "<b>Partición Lógica</b><br/>"
                    dot += "<b>Ocupa el {}% del disco</b><br/>".format(ebr.part_size*100/size_disco)
                    dot += "</td>"
                dot += "</tr></table>\n</td>\n"
        else:
            # Agregar celdas para particiones primarias
            dot += "<td colspan='2' bgcolor='lightblue'><b>Partición {}</b><br/><b>Ocupa el {}% del disco</b></td>\n".format(part.part_type, part.part_size*100/size_disco)

    dot += "</tr>\n"
    dot += "</table>\n"
    dot += ">];\n"
    dot += "}"

    # nombre_archivo = os.path.splitext(os.path.basename(path))[0]
    # graph = graphviz.Source(dot)
    # graph.render(nombre_archivo, format='svg', )
    #salida.append(dot)
    print("\t> REP: Reporte disk generado")
    salida.append("REP: Reporte disk generado")

def cmd_reporte_super_bloque(path, id):
    size_bloques_carpetas = len(bytes(BloquesCarpetas()))
    print("\t> REP: Generando reporte super_bloque...")
    salida.append("REP: Generando reporte super_bloque...")
    try:
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == id:
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

        dot = "digraph G {\n"
        dot += "node [shape=plaintext]\n"
        dot += "graph [rankdir=LR]\n"
        dot += "super [label=<\n"
        dot += "<table border='0' cellborder='1' cellspacing='0'>\n"
        dot += "<tr><td colspan='2' bgcolor='lightblue'><b>Super Bloque</b></td></tr>\n"
        dot += "<tr><td><b>Nombre</b></td><td><b>Valor</b></td></tr>\n"
        dot += "<tr><td>s_filesystem_type</td><td>{}</td></tr>\n".format(super_tmp.s_filesystem_type)
        dot += "<tr><td>s_inodes_count</td><td>{}</td></tr>\n".format(super_tmp.s_inodes_count)
        dot += "<tr><td>s_blocks_count</td><td>{}</td></tr>\n".format(super_tmp.s_blocks_count)
        dot += "<tr><td>s_free_blocks_count</td><td>{}</td></tr>\n".format(super_tmp.s_free_blocks_count)
        dot += "<tr><td>s_free_inodes_count</td><td>{}</td></tr>\n".format(super_tmp.s_free_inodes_count)
        dot += "<tr><td>s_mtime</td><td>{}</td></tr>\n".format(super_tmp.s_mtime)
        dot += "<tr><td>s_umtime</td><td>{}</td></tr>\n".format(super_tmp.s_umtime)
        dot += "<tr><td>s_mnt_count</td><td>{}</td></tr>\n".format(super_tmp.s_mnt_count)
        dot += "<tr><td>s_magic</td><td>{}</td></tr>\n".format(super_tmp.s_magic)
        dot += "<tr><td>s_inode_size</td><td>{}</td></tr>\n".format(super_tmp.s_inode_size)
        dot += "<tr><td>s_block_size</td><td>{}</td></tr>\n".format(super_tmp.s_block_size)
        dot += "<tr><td>s_first_ino</td><td>{}</td></tr>\n".format(super_tmp.s_first_ino)
        dot += "<tr><td>s_first_blo</td><td>{}</td></tr>\n".format(super_tmp.s_first_blo)
        dot += "<tr><td>s_bm_inode_start</td><td>{}</td></tr>\n".format(super_tmp.s_bm_inode_start)
        dot += "<tr><td>s_bm_block_start</td><td>{}</td></tr>\n".format(super_tmp.s_bm_block_start)
        dot += "<tr><td>s_inode_start</td><td>{}</td></tr>\n".format(super_tmp.s_inode_start)
        dot += "<tr><td>s_block_start</td><td>{}</td></tr>\n".format(super_tmp.s_block_start)
        dot += "</table>\n"
        dot += ">];\n"
        dot += "}"
        #print(dot)
        # nombre_archivo = os.path.splitext(os.path.basename(path))[0]
        # graph = graphviz.Source(dot)
        # graph.render(nombre_archivo, format='svg')
        salida.append(dot)
        print("\t> REP: Reporte super_bloque generado")
        salida.append("REP: Reporte super_bloque generado")
    except Exception as e:
        print(e)
        return False


def cmd_reporte_inode(path, id):

    try:
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == id:
                path_particion = particion.get('path')
                particion_nombre = particion.get('name')
                break
        
        particiones = leer_particiones_desde_archivo(path_particion)

        particion_actual = None
        for par in particiones:
            if par.part_name == particion_nombre:
                # print(par.part_status)
                # print(par.part_type)
                # print(par.part_fit)
                # print(par.part_start)
                # print(par.part_size)
                # print(par.part_name)  
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

        # Recuperar Bloques de Inodos
        inodos = []

        tmp_size = super_tmp.s_inode_start
        inode_list = []
        with open(path_particion, "rb+") as file:
        
            for i in range(5):
                file.seek(tmp_size)
                inode = Inodos()
                inode_data = file.read()  # Leer EBR
                inode.i_uid = struct.unpack("<i", inode_data[0:4])[0]
                inode.i_gid = struct.unpack("<i", inode_data[4:8])[0]
                inode.i_size = struct.unpack("<i", inode_data[8:12])[0]
                inode.i_atime = struct.unpack("<d", inode_data[12:20])[0]
                inode.i_ctime = struct.unpack("<d", inode_data[20:28])[0]
                inode.i_mtime = struct.unpack("<d", inode_data[28:36])[0]
                inode.i_block = list(struct.unpack("<15i", inode_data[36:96]))
                inode.i_type = struct.unpack("<B", inode_data[96:97])[0]
                inode.i_perm = struct.unpack("<i", inode_data[97:101])[0]
                
                inode_list.append(inode)

        # hacer un grafico de lista enlazada con cada inodo
        dot = "digraph G {\n"
        dot += "node [shape=plaintext]\n"
        dot += "graph [rankdir=LR]\n"
        dot += "inodos [label=<\n"
        dot += "<table border='0' cellborder='1' cellspacing='0'>\n"
        dot += "<tr><td colspan='2' bgcolor='lightblue'><b>Inodos</b></td></tr>\n"

        for inode in inode_list:
            dot += "<tr><td><b>Nombre</b></td><td><b>Valor</b></td></tr>\n"
            dot += "<tr><td>i_uid</td><td>{}</td></tr>\n".format(inode.i_uid)
            dot += "<tr><td>i_gid</td><td>{}</td></tr>\n".format(inode.i_gid)
            dot += "<tr><td>i_size</td><td>{}</td></tr>\n".format(inode.i_size)
            dot += "<tr><td>i_atime</td><td>{}</td></tr>\n".format(inode.i_atime)
            dot += "<tr><td>i_ctime</td><td>{}</td></tr>\n".format(inode.i_ctime)
            dot += "<tr><td>i_mtime</td><td>{}</td></tr>\n".format(inode.i_mtime)
            dot += "<tr><td>i_block</td><td>{}</td></tr>\n".format(inode.i_block)
            dot += "<tr><td>i_type</td><td>{}</td></tr>\n".format(inode.i_type)
            dot += "<tr><td>i_perm</td><td>{}</td></tr>\n".format(inode.i_perm)
            
        dot += "</table>\n"
        dot += ">];\n"
        dot += "}"
        print(dot)

        # nombre_archivo = os.path.splitext(os.path.basename(path))[0]
        # graph = graphviz.Source(dot)
        # graph.render(nombre_archivo, format='svg')
        salida.append(dot)
        print("\t> REP: Reporte inode generado")
        salida.append("REP: Reporte inode generado")

    except Exception as e:
        print(e)

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


def cmd_reporte_block():
    pass

def cmd_reporte_bm_inode(path, id):
    try:
        id_particion = ""
        path_particion = ""
        particion_nombre = ""
        for particion in particiones_montadas:
            id_particion = particion.get('id')
            if id_particion == id:
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

    except Exception as e:
        print(e)
        return False

def cmd_reporte_bm_block():
    pass

