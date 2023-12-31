import json
from utils import enter


with open('data.json', 'r', encoding='UTF-8') as f:
    GAMEDATA = json.load(f)

class Actualizador:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.versiones = {
            None: self.ver1_2_0,
        }

    def buscar_actualizaciones(self) -> None:
        version = self.data.get('version')

        if version is None:
            print('esta versión puede no ser compatible con el actualizador')
            enter()

        if version not in self.versiones:
            raise RuntimeError('El archivo de guardado es de una versión desconocida.')

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
