import json
from pathlib import Path
import shutil

from colorama import Fore

from utils import centrar_en_terminal, enter
from ascii import ATENCION


with open('data.json', 'r', encoding='UTF-8') as f:
    GAMEDATA = json.load(f)

class Actualizador:
    def __init__(self, data: dict, path: str) -> None:
        self.data = data
        self.version_antigua = data['version'] if data.get('version') is not None else 'desconocida'
        self.path = Path(path)
        self.versiones = {
            None: self.ver1_2_0,
        }

    def buscar_actualizaciones(self) -> None:
        version = self.data.get('version')

        if version is None:
            print(Fore.YELLOW)
            # Centrar cada línea.
            for linea in ATENCION.split("\n"):
                print(centrar_en_terminal(linea))

            print(
                f"\n{centrar_en_terminal('ATENCIÓN!')}\n\n"
                'Se ha detectado un archivo de guardado anterior a la versión 1.2.0\n'
                'Se intentará actualizar la partida a la versión actual, en caso de algún fallo en '
                'el juego después de la actualización se puede restaurar la partida original con el'
                ' archivo .bck generado.'
            )
            print(Fore.RESET, end='')
            enter()

        if version not in self.versiones:
            raise RuntimeError('El archivo de guardado es de una versión desconocida.')

        backup = self.path.parent / f"{version if version is not None else 'old'}_{self.path.name}.bck"
        shutil.copy(self.path, backup)

        actualizando = False
        for old, actualizacion in self.versiones.items():
            if old == version:
                actualizando = True

            if actualizando:
                actualizacion()

    def guardar(self, path: str) -> None:
        with open(path, "w", encoding="UTF-8") as f:
            json.dump(self.data, f)

    def ver1_2_0(self):
        self.data = {'version': '1.2.0', **self.data}
        
        # --- Nuevos logros
        self.data['logros']['peces_1'] = None
        self.data['logros']['todos_peces'] = None
        
        # --- Cambiar el nombre de el pez Jack de 3*.
        for item in self.data['inventario']:
            if item['nombre'] == 'Jack' and item['calidad'] == 3:
                item['nombre'] == 'Jake'

        # --- Colección de peces para el nuevo logro.
        nombres_peces = [p for calidad in GAMEDATA['pez']['nombres'][1:6] for p in calidad]
        peces_inventario = [item['nombre'] for item in self.data['inventario'] if item['tipo'] == 'pez']
        
        # Los peces del inventario serán añadidos automaticamente.
        self.data['coleccion'] = {}
        for pez in nombres_peces:
            self.data['coleccion'][pez] = pez in peces_inventario
