from datetime import datetime
import random
import json
from typing import Literal

from colorama import Style, Fore

from ascii import *
from etc import *

class pescador:
    """Usuario del juego, tiene todas las estadísticas y funciones del juego."""
    def __init__(self, nombre) -> None:
        self.nombre = nombre
        self.genero = None

        # Nombre con easter egg
        color = [v for k, v in zip(EASTER_EGGS.keys(), EASTER_EGGS.values()) if nombre.lower() == k]
        if len(color) != 0:
            self.nombre_mostrar = color[0] + nombre + Fore.RESET
        
        else:
            self.nombre_mostrar = nombre

        # Equipo del usuario, el diccionario es para saber el tipo de item que
        # tiene y este se actualiza con self.actualizar_equipo().
        self.equipo = {"sedal": 0, "anzuelo": 0, "cebo": 0, "caña": 0}
        self.sedal = sedal(self.equipo["sedal"])
        self.anzuelo = anzuelo(self.equipo["anzuelo"])
        self.cebo = cebo(self.equipo["cebo"])
        self.caña = caña(self.equipo["caña"])

        self.tienda = tienda(self)

        self.inventario = []
        self.dinero = 0
    
        # Estadísticas y logros.
        self.numero_peces = 0
        self.numero_basura = 0
        self.ostras = 0
        self.perlas_blancas = 0
        self.perlas_negras = 0
        self.sacos_dinero = 0
        self.tesoros = 0
        self.sedales_rotos = 0
        self.sedales_racha = 0
        self.sedales_max_racha = 0

        self.logros = {key: None for key in d['logros']}
        self.estadisticas = {"aventura": datetime.now().strftime("%d/%m/%Y a las %H:%M:%S"), "tamaño": None, "peso": None, "precio": None}

    def pescar(self) -> list | None:
        """Función de pescar, si la potencia del sedal es mayor a la de un
        número aleatorio de entre 1 y 100, devuelve pez o basura, si no devuelve
        None."""
        # La animación aplica el tiempo de pesca de la caña y limpia la pantalla.
        animacion(self.caña.tiempo())
        limpiar_pantalla()
        if random.randint(1, 100) <= self.sedal.potencia:   # potencia de la caña%
            # Reinicio de la racha de sedales rotos.
            self.sedales_racha = 0
            # Aquí se determina la calidad del pez, por si es zero, devolver basura.
            resultado_pesca = []
            for _ in range(self.anzuelo.anzuelos):
                calidad = random.choices(range(len(d["pez"]["nombres"])), weights=self.caña.probabilidades, k=1)[0]
                if calidad == 0:
                    pesca = basura(calidad)
                    self.numero_basura += 1
                
                elif calidad in range(1, 6):
                    pesca = pez(calidad)
                    # Sumar las estadísticas bonus del cebo.
                    pesca = self.cebo.sumar_estadisticas(pesca)
                    # Estadisticas y logros.
                    self.numero_peces += 1
                    self.actualizar_estadisticas(pesca)
                
                elif calidad == 6:
                    pesca = objeto_dinero(calidad)
                    if pesca.nombre == d["pez"]["nombres"][pesca.calidad][0]:
                        self.sacos_dinero += 1

                    elif pesca.nombre == d["pez"]["nombres"][pesca.calidad][1]:
                        self.tesoros += 1

                elif calidad == 7:
                    pesca = ostra(calidad)
                    self.ostras += 1

                self.comprovar_logros(pescado=pesca)
                if self.anzuelo.anzuelos == 1:
                    print(f"Has pescado: {pesca.detalles_full()}")
                
                else:
                    print(f"Has pescado: {pesca.detalles_fila()}")

                resultado_pesca.append(pesca)

            enter()
            return resultado_pesca
        
        else:
            self.sedales_rotos += 1
            self.sedales_racha += 1
            self.sedales_max_racha = self.sedales_racha if self.sedales_racha > self.sedales_max_racha else self.sedales_max_racha
            self.comprovar_logros()
            print("Se ha roto el sedal :(")
            enter()
            return None

    def actualizar_equipo(self) -> None:
        """Vuelve a crear las clases al comprar algo."""
        self.sedal = sedal(self.equipo["sedal"])
        self.anzuelo = anzuelo(self.equipo["anzuelo"])
        self.cebo = cebo(self.equipo["cebo"])
        self.caña = caña(self.equipo["caña"])

    def mostrar_inventario(self) -> None:
        """Muestra el inventario del jugador."""
        print("Tus peces:")
        if len(self.inventario) == 0:
            print(f"{Fore.YELLOW}No hay peces todavía.{Fore.RESET}")

        for i, pescado in enumerate(self.inventario):
            print(f"  {i + 1}. {pescado.detalles_fila()}")

    def menu_inventario(self) -> None:
        limpiar_pantalla()
        incorrecto = False
        salir = False
        while not salir:
            self.mostrar_inventario()
            print()
            print(f"Tu equipo:\n  Sedal: {self.sedal.nombre}\
                \n  Anzuelo: {self.anzuelo.nombre}\n  Cebo: {self.cebo.nombre}\
                \n  Caña: {self.caña.nombre}")
            print()
            print("Probabilidades de pescar peces:")
            print(f"  {', '.join([str(x) + '%' for x in self.caña.probabilidades])}")
            print("  Siendo estos basura el primero y peces\n  de calidad 1 a 5 para los 5 siguientes.\n  Me pregunto qué serán los otros porcentajes...")
            print()
            print("  V = Vender")
            print("  O = Abrir ostras" if self.ostras > 0 else Fore.LIGHTBLACK_EX + "  ? = ???" + Fore.RESET)
            print("  M = Volver al menú")
            print()
            
            if incorrecto:
                print(f"{Fore.RED}Opción no valida.{Fore.RESET}")
                incorrecto = False
                
            eleccion = input("Acción: ").upper()

            if eleccion == "V":
                self.vender()
                salir = True

            elif eleccion == "O" and self.ostras > 0:
                self.abrir_ostras()
                salir = True

            elif eleccion == "M":
                limpiar_pantalla()
                salir = True

            else:
                limpiar_pantalla()
                incorrecto = True

    def vender(self):
        """Menú de venta."""
        limpiar_pantalla()
        if len(self.inventario) != 0:
            self.mostrar_inventario()
            
            venta = input("Selecciona los peces que quieres vender: \n\
                \n  T/Todo = Vende todos los peces\n  1 = Vende el pez con ID 1\
                \n  2, 5, 8 = Vende los peces con IDs 2, 5 y 8\
                \n  M = Volver al menú principal.\n\n> ").lower()

            # Comprueva si hay comas.
            numero_coma = False
            for x in venta:
                if x == ",":
                    numero_coma = True

            # Comprueva si hay guiones.
            numero_guion = False
            for x in venta:
                if x == "-":
                    numero_guion = True
            
            # Si las hay, separa los índices de las comas y descarta los que no
            # son números y los que no son índices correctos.
            if numero_coma and not numero_guion:
                l = venta.split(",")
                indexes = []
                for index in l:
                    try:
                        i = int(index.strip()) - 1
                    
                    except ValueError:
                        pass

                    else:
                        if i in range(len(self.inventario)):
                            indexes.append(i)

                # Ordena la lista a la inversa para no tener problemas con los
                # peces que ya han sido vendidos.
                indexes.sort(reverse=True)
            
            # Si hay guiones coje los dos primeros índices para más adelante
            # crear un rango con ellos. Si hay algún índice no valido pone
            # numero_guion a falso para que no entré en la condición.
            if numero_guion and not numero_coma:
                l = venta.split("-")
                indexes = []
                for index in l:
                    try:
                        i = int(index.strip()) - 1
                    
                    except ValueError:
                        pass

                    else:
                        if i in range(len(self.inventario)):
                            indexes.append(i)
                        
                        else:
                            numero_guion = False

                # Ordenar la lista en caso de que los índices estén al reves.
                indexes.sort()
            
            # Si no hay comas y tampoco es todo o salir, significa que es un número así
            # que lo intenta pasar a entero, si no lo consigue hace que la
            # cadena sea "" para que vuelva a entrar en el bucle.
            if venta != "todo" and venta != "t" and venta != "m" and not numero_coma:
                try:
                    venta = int(venta) - 1
                
                except ValueError:
                    venta = ""

            # Todo.
            if venta == "todo" or venta == "t":
                confirmacion = input("Estás seguro de vender TODOS tus peces? (S/N) ").upper()

                if confirmacion == "S":
                    contador = 0
                    for _ in range(len(self.inventario)):
                        vendido = self.inventario.pop()
                        contador += vendido.calcular_precio()
                    
                    self.dinero += contador
                    limpiar_pantalla()
                    print(f"Se han vendido todos los peces por un total de {round(contador, 2)}€")
                
                else:
                    limpiar_pantalla()
                    print(f"{Fore.YELLOW}Operación cancelada.{Fore.RESET}")
            
            elif venta == "m":
                pass

            # Índices separados por comas.
            elif numero_coma:
                lista_peces = ['  ' + pescado.detalles_fila() + '\n' for pescado in self.inventario if self.inventario.index(pescado) in indexes]
                confirmacion = input(f"Estás seguro de vender los siguientes peces?\n{''.join(lista_peces)}\n > (S/N) ").upper()

                contador = 0
                if confirmacion == "S":
                    for index in indexes:
                        vendido = self.inventario.pop(index)
                        contador += vendido.calcular_precio()
                    
                    self.dinero += contador
                    limpiar_pantalla()
                    print(f"Se han vendido {len(indexes)} peces por un total de {round(contador, 2)}€")
                
                else:
                    limpiar_pantalla()
                    print(f"{Fore.YELLOW}Operación cancelada.{Fore.RESET}")

            # Índices separados por guión.
            elif numero_guion:
                # Crea un rango con los dos índices.
                rango_peces = range(indexes[0], indexes[1] + 1)
                lista_peces = ['  ' + pescado.detalles_fila() + '\n' for pescado in self.inventario if self.inventario.index(pescado) in rango_peces]
                confirmacion = input(f"Estás seguro de vender los siguientes peces?\n{''.join(lista_peces)}\n > (S/N) ").upper()

                contador = 0
                if confirmacion == "S":
                    # Por cada elemento borra el primer índice para que no se
                    # vendan peces no deseados.
                    for _ in rango_peces:
                        vendido = self.inventario.pop(indexes[0])
                        contador += vendido.calcular_precio()
                    
                    self.dinero += contador
                    limpiar_pantalla()
                    print(f"Se han vendido {len(rango_peces)} peces por un total de {round(contador, 2)}€")
                
                else:
                    limpiar_pantalla()
                    print(f"{Fore.YELLOW}Operación cancelada.{Fore.RESET}")

            # Índice solo.
            # Ya que venta ha sido previamente convertido a número entero si se
            # da el caso se puede comparar con números enteros.
            elif venta in range(len(self.inventario)):
                confirmacion = input(f"Estás seguro de vender: {self.inventario[venta].detalles_fila()}?\n\n> (S/N) ").upper()

                if confirmacion == "S":
                    vendido = self.inventario.pop(venta)
                    self.dinero += vendido.calcular_precio()
                    limpiar_pantalla()
                    print(f"Se ha vendido: {vendido.nombre} por {vendido.calcular_precio()}€")
                
                else:
                    limpiar_pantalla()
                    print(f"{Fore.YELLOW}Operación cancelada.{Fore.RESET}")

            else:
                limpiar_pantalla()
                print(f"{Fore.RED}Opción incorrecta, regresando al menú principal.{Fore.RESET}")
        
        # Caso de que el usuario no tenga peces.
        else:
            print(f"{Fore.YELLOW}No hay peces para vender.{Fore.RESET}")

    def abrir_ostras(self):
        limpiar_pantalla()
        salir = False
        while not salir:
            indexes_ostras = []
            lista_ostras = []
            for i, item in enumerate(self.inventario):
                if type(item) == ostra:
                    if not item.abierta:
                        indexes_ostras.append(i)
                        lista_ostras.append(item)
            
            if len(self.inventario) == 0 or len(lista_ostras) == 0:
                print(f"{Fore.RED}No tienes ninguna ostra.{Fore.RESET}")
                salir = True
            
            else:
                print("Tus ostras:")
                for i, x in enumerate(lista_ostras):
                    print(f"  {i + 1}. {x.detalles_fila()}")

                # Selección de la subtienda.
                print()
                try:
                    index_ostra = int(input("Selecciona el ID de la ostra: ")) - 1
                
                except ValueError:
                    index_ostra = -1

                if index_ostra in range(len(lista_ostras)):
                    limpiar_pantalla()
                    ostra_seleccionada = self.inventario.pop(indexes_ostras[index_ostra])
                    contenido = ostra_seleccionada.abrir()
                    self.inventario.append(ostra_seleccionada)
                    if contenido:
                        self.inventario.append(contenido)
                        if contenido.tipo == "blanca":
                            self.perlas_blancas += 1

                        elif contenido.tipo == "negra":
                            self.perlas_blancas += 1

                        self.comprovar_logros(perla=True)
                        print(f"{Fore.MAGENTA}Has encontrado una {contenido.nombre.lower()} con un valor de {contenido.precio}€!{Fore.RESET}")

                    else:
                        print(f"{Fore.YELLOW}La ostra estaba vacia :({Fore.RESET}")

                    salir = True

                elif index_ostra not in range(len(lista_ostras)):
                    limpiar_pantalla()
                    print(f"{Fore.RED}ID de la ostra incorrecto.{Fore.RESET}")

                else:
                    limpiar_pantalla()
                    print(f"{Fore.RED}Opción incorrecta, regresando al menú principal.{Fore.RESET}")
    
    def mostrar_estadisticas(self) -> None:
        """Muestra las estadísticas del usuario."""
        limpiar_pantalla()
        print(centrar_en_terminal("Tus estadísticas"))
        print()
        print(centrar_en_terminal(f"Tu aventura empezó el {self.estadisticas['aventura']}"))
        print()
        print(centrar_en_terminal(f"Peces pescados: {self.numero_peces:,}"))
        print(centrar_en_terminal(f"Basura pescada: {self.numero_basura:,}"))
        print()
        # Si no hay un registro del tamaño más grande tampoco lo habrá de los
        # otros por lo tanto no muestra estas estadísticas.
        if self.estadisticas["tamaño"] != None:
            print(f"{centrar_en_terminal('Pez más grande:')}\n{centrar_en_terminal(self.estadisticas['tamaño'].detalles_estadisticas('tamaño'))}\n")
            print(f"{centrar_en_terminal('Pez más pesado:')}\n{centrar_en_terminal(self.estadisticas['peso'].detalles_estadisticas('peso'))}\n")
            print(f"{centrar_en_terminal('Pez más caro:')}\n{centrar_en_terminal(self.estadisticas['precio'].detalles_estadisticas('precio'))}\n")
        print(centrar_en_terminal(f"Ostras pescadas: {self.ostras:,}"))
        print(centrar_en_terminal(f"Perlas blancas encontradas: {self.perlas_blancas:,}"))
        print(centrar_en_terminal(f"Perlas negras encontradas: {self.perlas_blancas:,}"))
        print()
        print(centrar_en_terminal(f"Cofres del tesoro pescados: {self.tesoros:,}"))
        print()
        print(centrar_en_terminal(f"Has roto {self.sedales_rotos:,} sedales"))
        print(centrar_en_terminal(f"Tu racha máxima de sedales rotos ha sido {self.sedales_max_racha:,}"))
        print()
        if self.logros["todos"] != None:
            print(Fore.CYAN, end="")
            print(centrar_en_terminal(f"Completaste el juego el {self.logros['todos']}"))
            print(Fore.RESET, end="")
        enter()

    def actualizar_estadisticas(self, pescado):
        """Actualiza las estadísticas con el pez recien pescado, esta función
        se llama desde self.pescar().
        Si no hay un registro de estadísticas pone las estadísticas de ese pez,
        si no actualiza las estadísticas si son mejores que las registradas."""
        if self.estadisticas["tamaño"] != None:
            if self.estadisticas["tamaño"].tamaño < pescado.tamaño:
                self.estadisticas["tamaño"] = pescado

            if self.estadisticas["peso"].peso < pescado.peso:
                self.estadisticas["peso"] = pescado

            if self.estadisticas["precio"].calcular_precio() < pescado.calcular_precio():
                self.estadisticas["precio"] = pescado
        else:
            self.estadisticas["tamaño"] = pescado
            self.estadisticas["peso"] = pescado
            self.estadisticas["precio"] = pescado
    
    def mostrar_logros(self):
        """Muestra el menú de logros."""
        # Nombres internos de los logros.
        nombres_logros = [x for x in self.logros.keys()]
        index = 0
        incorrecto = False
        salir = False

        # Bucle del menú de logros.
        while not salir:
            limpiar_pantalla()
            print()
            print(centrar_en_terminal(f"{index + 1}/{len(self.logros)}"))
            # Si el valor es una fecha en vez de None, pinta el trofeo de
            # amarillo, si no lo pinta de gris.
            if self.logros[nombres_logros[index]] != None:
                print(d['logros'][nombres_logros[index]]['color'].format(amarillo=Fore.YELLOW, cyan=Fore.CYAN))

            else:
                print(Fore.LIGHTBLACK_EX)
            
            # Centrar cada línea.
            for linea in TROFEO.split("\n"):
                print(centrar_en_terminal(linea))
            
            # Datos del logro y opciones.
            print(Fore.RESET)
            print(f"{Style.BRIGHT}{centrar_en_terminal(d['logros'][nombres_logros[index]]['nombre'][self.genero])}{Style.RESET_ALL}")
            print(f"{centrar_en_terminal(d['logros'][nombres_logros[index]]['pista']) if self.logros[nombres_logros[index]] == None else centrar_en_terminal(d['logros'][nombres_logros[index]]['descripcion'])}")
            print(f"{centrar_en_terminal(self.logros[nombres_logros[index]]) if self.logros[nombres_logros[index]] != None else Fore.RED + centrar_en_terminal('No desbloqueado') + Fore.RESET}")
            print()
            print("  A = Logro anterior")
            print("  D = Siguiente logro")
            print("  M = Volver al menú")
            print()

            if incorrecto:
                print(f"{Fore.RED}Opción incorrecta.{Fore.RESET}")
                incorrecto = False

            eleccion = input("Acción: ").upper()

            if eleccion == "A":
                index = index - 1 if index != 0 else len(self.logros) - 1
            
            elif eleccion == "D":
                index = index + 1 if index != len(self.logros) - 1 else 0
                
            elif eleccion == "M":
                salir = True

            else:
                incorrecto = True

    def comprovar_logros(self, pescado = None, perla = None):
        """Comprueba cada uno de los logros. Esta función se llama desde
        self.pescar()"""
        # Logros de pesca.
        if pescado != None:
            if self.numero_peces == 100 and not self.logros['peces_100']:
                self.logros["peces_100"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                self.anuncio_logro("peces_100")
            
            if self.numero_peces == 500 and not self.logros['peces_500']:
                self.logros["peces_500"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                self.anuncio_logro("peces_500")
            
            if self.numero_peces == 2000 and not self.logros['peces_2000']:
                self.logros["peces_2000"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                self.anuncio_logro("peces_2000")
            
            if self.numero_peces == 5000 and not self.logros['peces_5000']:
                self.logros["peces_5000"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                self.anuncio_logro("peces_5000")
            
            if self.numero_basura == 50 and not self.logros['basura']:
                self.logros["basura"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                self.anuncio_logro("basura")
            
            # Logros de peces.
            if type(pescado) == pez:
                if pescado.calcular_precio() >= 500 and not self.logros['pescado_500']:
                    self.logros["pescado_500"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                    self.anuncio_logro("pescado_500")
                
                if pescado.calcular_precio() >= 2000 and not self.logros['pescado_2000']:
                    self.logros["pescado_2000"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                    self.anuncio_logro("pescado_2000")
                
                if pescado.calcular_precio() >= 5000 and not self.logros['pescado_5000']:
                    self.logros["pescado_5000"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                    self.anuncio_logro("pescado_5000")
                
                if pescado.calcular_precio() >= 10000 and not self.logros['pescado_10000']:
                    self.logros["pescado_10000"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                    self.anuncio_logro("pescado_10000")

                if pescado.dorado and not self.logros["dorado"]:
                    self.logros["dorado"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                    self.anuncio_logro("dorado")
            
                if pescado.nombre == d["pez"]["nombres"][5][-1] and not self.logros["pez_raro"]:
                    self.logros["pez_raro"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                    self.anuncio_logro("pez_raro")
        
        # Otros logros.
        if self.sedales_racha == 5 and not self.logros["logro_sedal"]:
            self.logros["logro_sedal"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            self.anuncio_logro("logro_sedal")

        if self.equipo["sedal"] == 3 and self.equipo["anzuelo"] == 3 and self.equipo["cebo"] == 3 and self.equipo["caña"] == 3 and not self.logros['full_equipo']:
            self.logros["full_equipo"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            self.anuncio_logro("full_equipo")
        
        if perla and not self.logros["ostra"]:
            self.logros["ostra"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            self.anuncio_logro("ostra")
        
        if self.tesoros > 0 and not self.logros["tesoro"]:
            self.logros["tesoro"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            self.anuncio_logro("tesoro")
        
        todos_los_logros = True
        for logro in self.logros:
            if not self.logros[logro] and logro != "todos":
                todos_los_logros = False
        
        if todos_los_logros and not self.logros["todos"]:
            self.logros["todos"] = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            anuncio_final(self.nombre_mostrar)

    def anuncio_logro(self, logro):
        """Cuando se consigue un logro se llama a esta función, esto ocurre
        desde self.comprovar_logros()"""
        print(Fore.CYAN, end="")
        print("#" * 56)
        print(f"#{'¡Has desbloqueado un nuevo logro!'.center(54)}#")
        print(f"#{d['logros'][logro]['nombre'][self.genero].center(54)}#")
        print(f"#{d['logros'][logro]['descripcion'].center(54)}#")
        print("#" * 56)
        print(Fore.RESET, end="")
        print()

class objeto_pesca:
    """Cosa que se puede pescar, esta función es heredada desde pez y basura."""
    def __init__(self, calidad) -> None:
        self.calidad = calidad
        if calidad == 0 or calidad == 7:
            # Se selecciona el nombre de la basura.
            self.nombre = random.choice(d["pez"]["nombres"][self.calidad])
        
        elif calidad in range(1, 6):
            # Se selecciona el nombre del pez con ciertos porcentajes.
            # ~30% ~24% ~19% ~13.5% ~8% ~4%
            self.nombre = random.choices(d["pez"]["nombres"][self.calidad], weights=[11, 9, 7, 5, 3, 1.5], k=1)[0]

        elif calidad == 6:
            self.nombre = random.choices(d["pez"]["nombres"][self.calidad], weights=[95, 5], k=1)[0]

    def calcular_precio(self) -> float:
        return round(self.precio, 2)
    
    def detalles_fila(self) -> str:
        return f"{self.nombre}, Valor: {self.calcular_precio()}€"

    def detalles_full(self) -> str:
        return f"{self.nombre}\n  Valor: {self.calcular_precio()}€"

class pez(objeto_pesca):
    """Clase con la que se puede hacer cualquier cosa relacionada con el pez."""
    def __init__(self, calidad) -> None:
        objeto_pesca.__init__(self, calidad)
        # Se deciden las cualidades del pez.
        self.tamaño = random.uniform(d["pez"]["tamaño"][self.calidad][0], d["pez"]["tamaño"][self.calidad][1])
        self.peso = random.uniform(d["pez"]["peso"][self.calidad][0], d["pez"]["peso"][self.calidad][1])
        self.estrellas = " ".join(["*"] * calidad)
        self.dorado = True if random.randint(1, 10000) == 1 else False # 0,01%

    def calcular_precio(self) -> float:
        """Calcula el precio del pez al consultarlo."""
        # Formula para calcular el precio del pez.
        precio_crudo = 2 ** self.calidad + (d["pez"]["nombres"][self.calidad].index(self.nombre) + 1) * 5 * self.tamaño * self.peso * self.calidad ** 2
        if self.dorado:
            precio = precio_crudo * 2   # Bonificación dorado
        
        else:
            precio = precio_crudo / 4   # Calculo estándar

        return round(precio, 2)
    
    def detalles_fila(self) -> str:
        """Detalles del pez en forma de fila para ponerlos en una lista."""
        return f"{Fore.YELLOW if self.dorado else ''}Pez {self.nombre}, Calidad: {self.estrellas}, Longitud: {round(self.tamaño, 2)} m, Peso: {round(self.peso, 2)} kg, Valor: {self.calcular_precio():,}€{Fore.RESET}"

    def detalles_full(self) -> str:
        """Detalles del pez con saltos de linea."""
        return f"{Fore.YELLOW if self.dorado else ''}Pez {self.nombre}\n  Calidad: {self.estrellas}\n  Longitud: {round(self.tamaño, 2)} m\n  Peso: {round(self.peso, 2)} kg\n  Valor: {self.calcular_precio():,}€{Fore.RESET}"
    
    def detalles_estadisticas(self, stat) -> str:
        """Detalles del pez donde solo se muestra la cualidad deseada.
        Se usa para mostrar las estadísticas del jugador."""
        detalles = ""
        if self.dorado:
            detalles += Fore.YELLOW

        detalles += f"Fue un: {self.nombre} ({self.estrellas}), "
        if stat == "tamaño":
            detalles += f"con un tamaño de {self.tamaño} m"

        if stat == "peso":
            detalles += f"con un peso de {self.peso} kg"

        if stat == "precio":
            detalles += f"con un precio de {self.calcular_precio():,} €"
        
        return detalles + (Fore.RESET if self.dorado else "")

class basura(objeto_pesca):
    def __init__(self, calidad) -> None:
        objeto_pesca.__init__(self, calidad)
        self.precio = random.uniform(1, 5)

class objeto_dinero(objeto_pesca):
    def __init__(self, calidad) -> None:
        objeto_pesca.__init__(self, calidad)
        if self.nombre == d["pez"]["nombres"][self.calidad][0]:
            self.precio = random.uniform(50, 250)
        
        elif self.nombre == d["pez"]["nombres"][self.calidad][1]:
            self.precio = random.uniform(2000, 5000)

class ostra(objeto_pesca):
    def __init__(self, calidad) -> None:
        objeto_pesca.__init__(self, calidad)
        self.precio = 5
        self.abierta = False
        
    def abrir(self):
        self.nombre = "Ostra abierta"
        self.precio = 1
        self.abierta = True
        n = random.randint(1, 100)
        if n <= 95:
            return None
        
        elif n in range(96, 100):
            return perla("blanca")
        
        elif n == 100:
            return perla("negra")

class perla:
    def __init__(self, tipo: Literal["blanca", "negra"]) -> None:
        if tipo == "blanca":
            self.nombre = "Perla blanca"
            self.precio = 5000
        
        elif tipo == "negra":
            self.nombre = "Perla negra"
            self.precio = 2000
        
        self.tipo = tipo

    def calcular_precio(self) -> float:
        return round(self.precio, 2)
    
    def detalles_fila(self) -> str:
        return f"{Fore.MAGENTA}{self.nombre}, Valor: {self.calcular_precio()}€{Fore.RESET}"

    def detalles_full(self) -> str:
        return f"{Fore.MAGENTA}{self.nombre}\n  Valor: {self.calcular_precio()}€{Fore.RESET}"

class caña:
    def __init__(self, i):
        self.nombre = d["items"]["caña"]["tipos"][i]["nombre"]
        self.probabilidades = d["items"]["caña"]["tipos"][i]["probabilidades"]
        self.tiempo_pesca = d["items"]["caña"]["tipos"][i]["tiempo_pesca"]
    
    def tiempo(self) -> int:
        """Devuelve el tiempo aleatorio de pesca."""
        return random.randint(self.tiempo_pesca[0], self.tiempo_pesca[1])

class sedal:
    def __init__(self, i) -> None:
        self.nombre = d["items"]["sedal"]["tipos"][i]["nombre"]
        self.potencia = d["items"]["sedal"]["tipos"][i]["potencia"]
        self.precio = d["items"]["sedal"]["tipos"][i]["precio"]

class anzuelo:
    def __init__(self, i) -> None:
        self.nombre = d["items"]["anzuelo"]["tipos"][i]["nombre"]
        self.anzuelos = d["items"]["anzuelo"]["tipos"][i]["anzuelos"]
        self.precio = d["items"]["anzuelo"]["tipos"][i]["precio"]

class cebo:
    def __init__(self, i) -> None:
        self.nombre = d["items"]["cebo"]["tipos"][i]["nombre"]
        self.tamaño = d["items"]["cebo"]["tipos"][i]["tamaño"]  # list
        self.peso = d["items"]["cebo"]["tipos"][i]["peso"]      # list
        self.precio = d["items"]["cebo"]["tipos"][i]["precio"]
    
    def sumar_estadisticas(self, pescado) -> pez:
        """Suma la bonicicación del cebo a las cualidades del pez y devuelve el
        pez bonificado. Esta función se llama desde self.pescar()
        Si el usuario no tiene un cebo bonificado suma 0 a las cualidades."""
        pescado.tamaño += random.uniform(self.tamaño[0], self.tamaño[1])
        pescado.peso += random.uniform(self.peso[0], self.peso[1])

        return pescado

class tienda:
    """Tienda del usuario."""
    def __init__(self, usuario) -> None:
        self.usuario = usuario
        self.nombres_tiendas = [item for item in d["items"].keys()]
        self.tiendas = [d["items"][item] for item in d["items"]]
    
    def menu_tienda(self):
        """Menú principal de la tienda, aquí se decide una subtienda para
        empezar a comprar."""
        incorrecto = False
        salir = False
        while not salir:
            limpiar_pantalla()
            print("Tienda:")

            # Lista de subtiendas.
            for i, nombre in enumerate(self.nombres_tiendas):
                print(f"  {i + 1}. {nombre.capitalize()}")

            if incorrecto:
                print(f"{Fore.RED}ID de la tienda incorrecto.{Fore.RESET}")
                incorrecto = False
                
            print(f"  {99}. Salir de la tienda.")

            # Selección de la subtienda.
            print()
            try:
                index_tienda = int(input("Selecciona el ID de la tienda: ")) - 1
            
            except ValueError:
                index_tienda = -1

            if index_tienda + 1 == 99:
                limpiar_pantalla()
                salir = True

            elif index_tienda not in range(len(self.tiendas)):
                incorrecto = True

            else:
                self.subtienda(index_tienda)
                salir = True

    def subtienda(self, index_tienda: int):
        """Menú de la tienda seleccionada. En este se pueden comprar productos.
        """
        limpiar_pantalla()
        agotado = False
        incorrecto = False
        cancelado = False
        salir = False
        nombre_tienda = self.nombres_tiendas[index_tienda]
        productos_tienda = self.tiendas[index_tienda]["tipos"]
        while not salir:
            print(f"Tienda de {nombre_tienda}")
            # El formato de la cadena son las probabilidades de la caña, solo
            # necesita formato la descripción de esta.
            print(f"{self.tiendas[index_tienda]['descripcion'].format(a=', '.join([str(x) + '%' for x in self.usuario.caña.probabilidades]))}.")
            print()

            # Lista de productos.
            for i, elemento in enumerate(productos_tienda):
                # Salta el primer elemento de los productos, el cual tiene una
                # clave "_excluido". Al hacer esto salta el elemento 0 por lo
                # que no hay que sumarle 1 al índice.
                if "_excluido" not in elemento:
                    # Si el usuario ya tiene cierto objeto de la misma o mayor
                    # calidad, estos aparecerán como agotados en la tienda.
                    # Si tiene suficiente saldo sale el precio en verde, si no
                    # en rojo.
                    print(f"  {i}. {elemento['nombre'] + ' -> ' + (Fore.GREEN if self.usuario.dinero >= elemento['precio'] else Fore.RED) + str(elemento['precio']) + '€' + Fore.RESET if self.usuario.equipo[nombre_tienda] < i else Fore.LIGHTBLACK_EX + 'Agotado.' + Fore.RESET}")
        
            print(f"  {99}. Salir de la tienda.")

            # Selección de productos.
            print()
            print(f"Tu saldo es de: {round(self.usuario.dinero, 2)}€")

            if incorrecto:
                print(f"{Fore.RED}ID del objeto incorrecto.{Fore.RESET}")
                incorrecto = False

            if agotado:
                print(f"{Fore.YELLOW}El producto está agotado.{Fore.RESET}")
                agotado = False

            if cancelado:
                print(f"{Fore.YELLOW}Operación cancelada.{Fore.RESET}")
                cancelado = False
                
            try:
                index_producto = int(input("Selecciona el ID del objeto: "))
            
            except ValueError:
                index_producto = -1
            
            if index_producto == 99:
                limpiar_pantalla()
                salir = True

            elif index_producto not in range(len(productos_tienda)):
                limpiar_pantalla()
                incorrecto = True

            elif self.usuario.equipo[nombre_tienda] >= index_producto:
                limpiar_pantalla()
                agotado = True

            else:
                producto = productos_tienda[index_producto]
                limpiar_pantalla()
                confirmacion = input(f"Quieres comprar: {producto['nombre']} por {producto['precio']}€?\nSaldo disponible: {round(self.usuario.dinero, 2)}€\n\n> (S/N) ").upper()
                if confirmacion == "S":
                    if self.usuario.dinero >= producto["precio"]:
                        self.usuario.dinero -= producto["precio"]
                        self.usuario.equipo[nombre_tienda]= index_producto
                        self.usuario.actualizar_equipo()
                        limpiar_pantalla()
                        self.usuario.comprovar_logros()
                        print(f"{Fore.CYAN}Ahora tienes: {producto['nombre']}!\nNuevo saldo: {round(self.usuario.dinero, 2)}€{Fore.RESET}")
                        salir = True
                    
                    else:
                        limpiar_pantalla()
                        print(f"{Fore.RED}No tienes suficiente dinero.{Fore.RESET}")
                
                else:
                    limpiar_pantalla()
                    cancelado = True

with open("data.json", "r", encoding="UTF-8") as f:
    d = json.load(f)

# Easter eggs de los nombres.
EASTER_EGGS = {"sae": Fore.MAGENTA, "sergo": Fore.RED, "ssr": Fore.RED}

for l in d["pez"]["nombres"]:
    for nombre in l:
        if nombre.lower() != "sae":
            EASTER_EGGS[nombre.lower()] = Fore.BLUE