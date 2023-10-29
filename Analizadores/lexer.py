import ply.lex as lex

errores = []

palabras_reservadas = {

    'execute' : 'EXECUTE',
    'mkdisk' : 'MKDISK', # PRIMER COMANDO
    'rmdisk' : 'RMDISK', # SEGUNDO COMANDO
    'fdisk' : 'FDISK', # TERCER COMANDO
    'mount' : 'MOUNT', # CUARTO COMANDO
    'unmount' : 'UNMOUNT', # QUINTO COMANDO
    'mkfs' : 'MKFS', # SEXTO COMANDO

    'size': 'SIZE',
    'unit': 'UNIT',
    'path': 'PATH',
    'fit': 'FIT',

    'name': 'NAME',
    'type': 'TYPE',
    'delete': 'DELETE',
    'add': 'ADD',

    'full': 'FULL',

    'id': 'ID_DISK',

    'fs': 'FS_DISK',

    # COMANDOS DE USUARIOS
    'login' : 'LOGIN', # SEPTIMO COMANDO
    'logout' : 'LOGOUT', # OCTAVO COMANDO
    'mkgrp' : 'MKGRP', # NOVENO COMANDO
    'rmgrp' : 'RMGRP', # DECIMO COMANDO
    'mkusr' : 'MKUSR', # ONCEAVO COMANDO
    'rmusr' : 'RMUSR', # DOCEAVO COMANDO

    'user' : 'USER',
    'pass' : 'PASSWORD',

    'grp' : 'GRP',

    # COMANDOS DE USUARIO ROOT
    'mkfile' : 'MKFILE', # TRECEAVO COMANDO
    'cat' : 'CAT', # CATORCEAVO COMANDO

    'r' : "ERRE",
    'cont' : 'CONT',
    'file' : 'FILE',

    # comandos de los reportes
    'rep' : 'REP', # QUINCEAVO COMANDO
    'mbr' : 'MBR', # DECIMO SEXTO COMANDO
    'disk' : 'DISK', # DECIMO SEPTIMO COMANDO
    'inode' : 'INODE', # DECIMO OCTAVO COMANDO
    'journaling' : 'JOURNALING', # DECIMO NOVENO COMANDO
    'block' : 'BLOCK', # VIGESIMO COMANDO
    'bm_inode' : 'BM_INODE', # VIGESIMO PRIMER COMANDO
    'bm_block' : 'BM_BLOCK', # VIGESIMO SEGUNDO COMANDO
    'tree' : 'TREE', # VIGESIMO TERCER COMANDO
    'sb' : 'SB', # VIGESIMO CUARTO COMANDO
    'file' : 'FILE', # VIGESIMO QUINTO COMANDO
    'ls' : 'LS', # VIGESIMO SEXTO COMANDO
    'ruta' : 'RUTA', # VIGESIMO SEPTIMO COMANDO

    'pause': 'PAUSE', # VIGESIMO OCTAVO COMANDO

}

tokens = [
    'FS',
    'ENTERO',
    'FITSYM',
    'UNIDAD',
    'TIPO',
    'CADENA',
    'IGUAL',
    'GUION',
    'ID'
] + list(palabras_reservadas.values())

# Expresiones regulares para tokens simples
t_IGUAL = r'\=' 
t_GUION = r'\-'

# Expresiones regulares con acciones de codigo 55 
# todo ingresa como un string  "55" int(55) 
def t_COMMENT(t):
    r'\#.*'
    pass

def t_FS(t):
    r'2fs|3fs'
    t.value = t.value.upper()
    return t

def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

#  Cadena 
def t_CADENA(t):
    r'\"(.|\n)*?\"'
    t.value = t.value[1:-1] # remuevo las comillas
    return t

def t_FITSYM(t):
    r'BF|FF|WF'
    t.value = t.value.upper()
    return t

# Caracter M o K
def t_UNIDAD(t):
    r'M|K|B'
    t.value = t.value.upper()
    return t

def t_TIPO(t):
    r'P|E|L'
    t.value = t.value.upper()
    return t

#  ID mkdir -> ID mkdisk
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = palabras_reservadas.get(t.value.lower(), 'ID') 
    return t

# New line
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#  Caracteres ignorados
t_ignore = ' \t'

def t_error(t):
    errores.append(t.value[0])
    print(f'Caracter no reconocido: {t.value[0]} en la linea {t.lexer.lineno}')
    t.lexer.skip(1)

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

lexer = lex.lex()
