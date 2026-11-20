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


def ruta_contador(nombre):
    # "docentes" -> ".../datos/docentes_ultimo_id.txt" (guarda el último número entregado)
    return os.path.join(CARPETA, nombre + "_ultimo_id.txt")


def leer_contador(nombre):
    if not os.path.exists(ruta_contador(nombre)):
        return 0
    with open(ruta_contador(nombre), "r", encoding="utf-8") as f:
        texto = f.read().strip()
    return int(texto) if texto else 0


def agregar(nombre, registro):
    # Le pone un id nuevo y lo guarda al final. El número nunca se repite,
    # aunque se haya borrado el último docente (se recuerda el último entregado).
    registros = leer(nombre)
    mayor = max([r["id"] for r in registros], default=0)
    ultimo = max(mayor, leer_contador(nombre))
    registro["id"] = ultimo + 1
    registros.append(registro)
    guardar_todo(nombre, registros)
    with open(ruta_contador(nombre), "w", encoding="utf-8") as f:
        f.write(str(registro["id"]))
    return registro