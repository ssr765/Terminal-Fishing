import os
import datetime

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

def tiempo_formato(tiempo) -> str:
    formato = ""
    td = str(datetime.timedelta(seconds=tiempo))
    hms = td.split(":")

    if "days" in hms[0]:
        dias = hms[0].split(",")[0]
        hms[0] = hms[0].split(",")[1].strip()
        dias = dias.split(" ")[0]
        formato += f"{dias} días, "
    
    hms[2] = hms[2].split(".")[0]
    formato += f"{hms[0]} horas, {hms[1]} minutos y {hms[2]} segundos"

    return formato