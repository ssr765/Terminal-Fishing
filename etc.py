import os

def limpiar_pantalla():
    """Limpia la pantalla con "cls" en caso de Windows, si no usa "clear"."""
    os.system("cls") if os.name == "nt" else os.system("clear")

def centrar_en_terminal(cadena: str) -> str:
    """Devuelve la cadena centrada en la terminal."""
    return cadena.center(os.get_terminal_size().columns)

def enter() -> None:
    """Pausa para que se vea el contenido en la pantalla."""
    print()
    input("Pulsa ENTER para continuar")