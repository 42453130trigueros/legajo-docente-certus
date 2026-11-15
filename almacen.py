# Ayudante para leer y guardar datos en archivos de texto (RF9).
import json
import os

CARPETA = os.path.join(os.path.dirname(__file__), "datos")


def ruta(nombre):
    # "docentes" -> ".../datos/docentes.txt"
    return os.path.join(CARPETA, nombre + ".txt")


def leer(nombre):
    # Devuelve una lista con todos los registros del archivo.
    if not os.path.exists(ruta(nombre)):
        return []
    registros = []
    #                            hace que las tildes y la ñ se guarden bien.
    with open(ruta(nombre), "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                registros.append(json.loads(linea))
    return registros


def guardar_todo(nombre, registros):
    # Reescribe el archivo completo (sirve para agregar, editar y eliminar).
    os.makedirs(CARPETA, exist_ok=True)
    with open(ruta(nombre), "w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def agregar(nombre, registro):
    # Le pone un id nuevo y lo guarda al final.
    registros = leer(nombre)
    ultimo = max([r["id"] for r in registros], default=0)
    registro["id"] = ultimo + 1
    registros.append(registro)
    guardar_todo(nombre, registros)
    return registro