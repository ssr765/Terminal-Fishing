import os
import random
import time

from colorama import Fore

from etc import *

COLORES = [Fore.RED, Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.YELLOW, Fore.WHITE]
PECES = ["  <º))))><  ", "  <º)))><  ", "  <º))><  ", "  <º)><  ", "  <><  ",
"  ><((((º>  ", "  ><(((º>  ", "  ><((º>  ", "  ><(º>  ", "  ><>  "]

with open("ascii/trofeo.txt", "r") as f:
    TROFEO = f.read()

with open("ascii/felicidades.txt", "r") as f:
    FELICIDADES = f.read()

with open("ascii/billete.txt", "r") as f:
    BILLETE = f.read()

def animacion(segundos):
    """Función que dibuja la animación de pescar en la pantalla. También espera
    el tiempo de pesca de la caña."""
    frames = segundos * 2
    # Bucle del movimiento de la animación.
    for x in range(frames):
        os.system("cls")
        print()
        pescando = centrar_en_terminal("Pescando").rstrip() + "." * x
        print(pescando)
        print()
        print(Fore.BLUE + "~" * os.get_terminal_size().columns + Fore.RESET)

        # Bucle para dibujar las lineas.
        for _ in range(os.get_terminal_size().lines - 5):
            # El contador sirve para contar la cantidad de caracteres que han sido
            # impresos, así evitando que hayan peces cortados o más lineas de las
            # deseadas.
            contador = 0
            # Bucle para dibujar cada linea.
            for _ in range(int(os.get_terminal_size().columns / 2)):
                # Olas.
                ola = " ~~ " if random.randint(1, 20) == 1 else " "
                if len(ola) < os.get_terminal_size().columns - contador:
                    print(Fore.BLUE + ola + Fore.RESET, end="")
                    contador += len(ola)

                # Peces
                ascii_pez = random.choice(PECES) if random.randint(1, 200) == 1 else " "
                if len(ascii_pez) < os.get_terminal_size().columns - contador:
                    print((random.choice(COLORES) + ascii_pez + Fore.RESET) , end="")
                    contador += len(ascii_pez)

            print()

        time.sleep(0.5)

def anuncio_final(nombre):
    """En vez de usar usuario.anuncio_logro() para mostrar el logro final se
    usará esta función la cual dibuja un anuncio más grande."""
    linea = "#" * (os.get_terminal_size().columns - 1)
    espacio = "#" + (" " * (os.get_terminal_size().columns - 3)) + "#"

    # Color, línea superior y espacio.
    print(Fore.CYAN, end="")
    print(linea)
    print(espacio)
    
    # Felicidades ASCII art.
    for x in FELICIDADES.split("\n"):
        print("#" + (x.center(os.get_terminal_size().columns - 3)) + "#")

    # Espacio y mensaje de juego completado.
    print(espacio)
    print("#" + ("Has conseguido todos los logros".center(os.get_terminal_size().columns - 3)) + "#")
    print("#" + ("Por lo tanto... ¡HAS COMPLETADO EL JUEGO!".center(os.get_terminal_size().columns - 3)) + "#")

    # Espacios según el tamaño de la terminal.
    for _ in range(int((os.get_terminal_size().lines - 28) / 2)):
        print(espacio)

    # Trofeo ASCII art.
    for x in TROFEO.split("\n"):
        print("#" + (x.center(os.get_terminal_size().columns - 3)) + "#")

    # Espacios según el tamaño de la terminal.
    for _ in range(int((os.get_terminal_size().lines - 28) / 2)):
        print(espacio)
    
    # Mensaje de enhorabuena con un espacio de separación y la línea de abajo.
    print("#" + (f"¡Enhorabuena, {nombre}!".center(os.get_terminal_size().columns - 3)) + "#")
    print(espacio)
    print(linea)
    print(Fore.RESET, end="")
    enter()
    limpiar_pantalla()