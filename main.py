import os
import json
from pathlib import Path
import signal
import sys
import time

from colorama import Fore

from classes import *
from utils import *

def item_a_diccionario(item) -> dict:
    """Convierte un item de inventario a diccionario para ser guardado."""
    if type(item) == pez:
        d_item = {
            "tipo": "pez",
            "nombre": item.nombre,
            "calidad": item.calidad,
            "pez": {
                "tamaño": item.tamaño,
                "peso": item.peso,
                "dorado": item.dorado
            }
        }
            
    elif type(item) == basura:
        d_item = {
            "tipo": "basura",
            "nombre": item.nombre,
            "calidad": item.calidad,
            "basura": {
                "precio": item.precio
            }
        }
            
    elif type(item) == objeto_dinero:
        d_item = {
            "tipo": "objeto_dinero",
            "nombre": item.nombre,
            "calidad": item.calidad,
            "objeto_dinero": {
                "precio": item.precio
            }
        }
            
    elif type(item) == ostra:
        d_item = {
            "tipo": "ostra",
            "nombre": item.nombre,
            "calidad": item.calidad,
            "ostra": {
                "precio": item.precio,
                "abierta": item.abierta
            }
        }
            
    elif type(item) == perla:
        d_item = {
            "tipo": "perla",
            "nombre": item.nombre,
            "perla": {
                "precio": item.precio,
                "tipo_perla": item.tipo
            }
        }
    
    return d_item

def diccionario_a_item(d: dict):
    """Convierte un diccionario a un item de inventario para ser restaurado
    en el juego."""
    if d['tipo'] == "pez":
        item = pez(d['calidad'])
        item.nombre = d['nombre']
        item.tamaño = d['pez']['tamaño']
        item.peso = d['pez']['peso']
        item.dorado = d['pez']['dorado']
    
    elif d['tipo'] == "basura":
        item = basura(d['calidad'])
        item.nombre = d['nombre']
        item.precio = d['basura']['precio']
    
    elif d['tipo'] == "objeto_dinero":
        item = objeto_dinero(d['calidad'])
        item.nombre = d['nombre']
        item.precio = d['objeto_dinero']['precio']
    
    elif d['tipo'] == "ostra":
        item = ostra(d['calidad'])
        item.nombre = d['nombre']
        item.precio = d['ostra']['precio']
        item.abierta = d['ostra']['abierta']
    
    elif d['tipo'] == "perla":
        item = perla(d['perla']['tipo_perla'])
        item.nombre = d['nombre']
        item.precio = d['perla']['precio']
    
    return item

def guardar_partida(usuario):
    """Guarda la partida copiando todos los datos del usuario a un diccionario."""
    # Por cada item en el inventario crea un diccionario y lo guarda en el
    # diccionario de la partida.
    inventario = []
    for item in usuario.inventario:
        inventario.append(item_a_diccionario(item))

    # Para las estadisticas del pez más grande, más largo y más caro, guarda
    # estos en un diccionario también.
    estadisticas = {}
    for estadistica in usuario.estadisticas:
        if type(usuario.estadisticas[estadistica]) == pez:
            estadisticas[estadistica] = item_a_diccionario(usuario.estadisticas[estadistica])
        
        else:
            estadisticas[estadistica] = usuario.estadisticas[estadistica]

    partida = {
        "nombre": usuario.nombre,
        "genero": usuario.genero,
        "equipo": usuario.equipo,
        "inventario": inventario,
        "dinero": usuario.dinero,
        "tiempo_jugado": usuario.tiempo_jugado,
        "numero_peces": usuario.numero_peces,
        "numero_basura": usuario.numero_basura,
        "ostras": usuario.ostras,
        "perlas_blancas": usuario.perlas_blancas,
        "perlas_negras": usuario.perlas_negras,
        "sacos_dinero": usuario.sacos_dinero,
        "tesoros": usuario.tesoros,
        "sedales_rotos": usuario.sedales_rotos,
        "sedales_racha": usuario.sedales_racha,
        "sedales_max_racha": usuario.sedales_max_racha,
        "logros": usuario.logros,
        "estadisticas": estadisticas
    }

    with open(RUTA_PARTIDA, "w", encoding="UTF-8") as f:
        json.dump(partida, f)

    limpiar_pantalla()
    print(f"{Fore.GREEN}Se ha guardado la partida.{Fore.RESET}")

def cargar_partida(usuario):
    """ """
    with open(RUTA_PARTIDA, "r", encoding="UTF-8") as f:
        partida = json.load(f)

    inventario = []
    for item in partida['inventario']:
        inventario.append(diccionario_a_item(item))
    
    estadisticas = {}
    for estadistica in partida["estadisticas"]:
        if type(partida["estadisticas"][estadistica]) == dict:
            estadisticas[estadistica] = diccionario_a_item(partida["estadisticas"][estadistica])
        
        else:
            estadisticas[estadistica] = partida["estadisticas"][estadistica]

    usuario.genero = partida['genero']
    usuario.equipo = partida['equipo']
    usuario.actualizar_equipo()
    usuario.inventario = inventario
    usuario.dinero = partida['dinero']
    usuario.tiempo_jugado = partida['tiempo_jugado']
    usuario.numero_peces = partida['numero_peces']
    usuario.numero_basura = partida['numero_basura']
    usuario.ostras = partida['ostras']
    usuario.perlas_blancas = partida['perlas_blancas']
    usuario.perlas_negras = partida['perlas_negras']
    usuario.sacos_dinero = partida['sacos_dinero']
    usuario.tesoros = partida['tesoros']
    usuario.sedales_rotos = partida['sedales_rotos']
    usuario.sedales_racha = partida['sedales_racha']
    usuario.sedales_max_racha = partida['sedales_max_racha']
    usuario.logros = partida['logros']
    usuario.estadisticas = estadisticas

def crear_partida(usuario):
    partida = {
        "nombre": usuario.nombre,
        "genero": usuario.genero,
        "equipo": usuario.equipo,
        "inventario": usuario.inventario,
        "dinero": usuario.dinero,
        "tiempo_jugado": usuario.tiempo_jugado,
        "numero_peces": usuario.numero_peces,
        "numero_basura": usuario.numero_basura,
        "ostras": usuario.ostras,
        "perlas_blancas": usuario.perlas_blancas,
        "perlas_negras": usuario.perlas_negras,
        "sacos_dinero": usuario.sacos_dinero,
        "tesoros": usuario.tesoros,
        "sedales_rotos": usuario.sedales_rotos,
        "sedales_racha": usuario.sedales_racha,
        "sedales_max_racha": usuario.sedales_max_racha,
        "logros": usuario.logros,
        "estadisticas": usuario.estadisticas
    }

    with open(RUTA_PARTIDA, "w", encoding="UTF-8") as f:
        json.dump(partida, f)

def comprovar_nombre(nombre) -> bool:
    CARACTERES_PROHIBIDOS = "\\/:*?\"<>|"
    cantidad_letras = False
    caracteres_incorrectos = False
    if len(nombre) not in range(1, 51):
        print(f"{Fore.RED}El nombre tiene que tener entre 1 y 50 caracteres.{Fore.RESET}")
    
    else:
        cantidad_letras = True
    
    for x in nombre:
        if x in CARACTERES_PROHIBIDOS and not caracteres_incorrectos:
            print(f"{Fore.RED}El nombre tiene caracteres no permitidos ({x}).{Fore.RESET}")
            caracteres_incorrectos = True
    
    if cantidad_letras and not caracteres_incorrectos:
        return True
    
    else:
        return False

def actualizar_tiempo(usuario, tiempo_inicial) -> float:
    """Guarda el tiempo jugado a la hora de guardar la partida, devuelve el
    tiempo actual para actualizar la variable que guarda el tiempo inicial."""
    usuario.tiempo_jugado += time.time() - tiempo_inicial
    return time.time()

# Evitar que Ctrl-C provoque KeyboardInterrupt y en vez de eso guarda la partida
# y sale del juego.
def signal_handler(sig, frame):
    global usuario
    try:
        actualizar_tiempo(usuario, tiempo_inicial)
        guardar_partida(usuario)
    
    except NameError:
        pass
    
    else:
        print(f"Hasta pronto, {usuario.nombre_mostrar}!")

    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

os.system("title SSR Terminal Fishing")
salir = False
nombre_valido = False
limpiar_pantalla()
print("Bienvenido al estanque!")
while not nombre_valido:
    nombre = input("Cuál es tu nombre? ")
    limpiar_pantalla()
    nombre_valido = comprovar_nombre(nombre)

usuario = pescador(nombre)
os.system(f"title SSR Terminal Fishing - {usuario.nombre}")

CARPETA_GUARDADO = os.path.expanduser('~') + "\\Documents\\SSRpesca\\"
Path(CARPETA_GUARDADO).mkdir(exist_ok=True)
RUTA_PARTIDA = CARPETA_GUARDADO + usuario.nombre.lower() + ".json"

if not os.path.isfile(RUTA_PARTIDA):
    crear_partida(usuario)

else:
    cargar_partida(usuario)

genero = ""
while usuario.genero == None:
    genero = input(f"Hola {usuario.nombre}, parece que no nos conociamos.\
        \n¿Cual és tu género?\n  M = Hombre\n  F = Mujer\n\n>  ").upper()
    limpiar_pantalla()

    if genero == "M":
        usuario.genero = 0

    elif genero == "F":
        usuario.genero = 1

# Tiempo inicial para calcular la sesión de juego.
tiempo_inicial = time.time()

while not salir:
    # Comprovación de logros de tiempo jugado.
    usuario.comprovar_logros(tiempo_inicial=tiempo_inicial)
    print(f"""Hola, {usuario.nombre_mostrar}! Qué quieres hacer?
  P = Pescar\n  I = Inventario\n  T = Tienda\n  C = Cartera\n  E = Estadísticas
  L = Logros\n  G = Guardar partida\n  S = Salir (se guarda la partida)""")
    print()
    accion = input("Acción: ").upper()

    if accion == "P":
        resultado_pesca = usuario.pescar()
        if resultado_pesca != None:
            for pescado in resultado_pesca:
                usuario.inventario.append(pescado)

        limpiar_pantalla()
    
    elif accion == "I":
        usuario.menu_inventario()
    
    elif accion == "T":
        usuario.tienda.menu_tienda()
            
    elif accion == "C":
        usuario.mostrar_saldo()
        limpiar_pantalla()
            
    elif accion == "E":
        usuario.mostrar_estadisticas()
        limpiar_pantalla()
            
    elif accion == "L":
        usuario.mostrar_logros()
        limpiar_pantalla()
            
    elif accion == "G":
        tiempo_inicial = actualizar_tiempo(usuario, tiempo_inicial)
        guardar_partida(usuario)
            
    elif accion == "S":
        tiempo_inicial = actualizar_tiempo(usuario, tiempo_inicial)
        guardar_partida(usuario)
        print(f"Hasta pronto, {usuario.nombre_mostrar}!")
        salir = True
    
    else:
        limpiar_pantalla()
        print(f"{Fore.RED}Opción no valida.{Fore.RESET}")