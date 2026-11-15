# Legajo Docente CERTUS - Paso 4: una direccion para cada pantalla.
from flask import Flask, render_template, request, redirect, session

import almacen

app = Flask(__name__)
# Clave para que Flask pueda "firmar" la memoria (session) de cada persona.
app.secret_key = "legajo-certus-grupo5"

def leer_formulario():
    # Toma lo que la persona escribió en el formulario.
    return {
        "nombre": request.form["nombre"].strip(),
        "correo": request.form["correo"].strip().lower(),
        "carrera": request.form["carrera"],
        "telefono": request.form["telefono"].strip(),
        "ingreso": request.form["ingreso"],
    }


def validar(datos, id_actual=None):
    # Devuelve un TEXTO con el problema, o None si todo está bien.
    if not datos["nombre"] or not datos["correo"] or not datos["carrera"]:
        return "Nombre, correo y carrera son obligatorios."
    if not datos["correo"].endswith("@certus.edu.pe") or datos["correo"] == "@certus.edu.pe":
        return "El correo debe terminar en @certus.edu.pe."
    for otro in almacen.leer("docentes"):
        if otro["correo"] == datos["correo"] and otro["id"] != id_actual:
            return "Ese correo ya está registrado."
    return None





# Cuando el navegador pide "/" o "/login", mostramos la pantalla de ingreso.
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        if correo.endswith("@certus.edu.pe") and correo != "@certus.edu.pe":
            session["correo"] = correo
            return redirect("/docentes")
        return render_template("login.html", error=True)
    session.clear()  # al entrar o pulsar "Salir", se olvida el correo
    return render_template("login.html", error=False)


@app.route("/docentes")
def docentes():
    lista = almacen.leer("docentes")          # aquí nace "lista": todos los docentes del archivo
    return render_template("docentes.html", docentes=lista)


@app.route("/docentes/nuevo", methods=["GET", "POST"])
def registrar_docente():
    error = None       # empezamos sin error...
    mostrar = {}       # formulario vacío

    if request.method == "POST":          # la persona pulsó Guardar
        datos = leer_formulario()         # aquí nace "datos": lo que escribió
        error = validar(datos)            # aquí se llena "error": un texto o None
        if not error:                     # sin error: guardamos y volvemos a la lista
            almacen.agregar("docentes", datos)
            return redirect("/docentes")
        mostrar = datos                   # con error: mostramos lo que escribió

    return render_template("registrar_docente.html", error=error, docente=mostrar)


@app.route("/docentes/<int:id>/editar", methods=["GET", "POST"])
def editar_docente(id):                   # "id" es el número que viene en la dirección
    lista = almacen.leer("docentes")      

    docente = None
    for x in lista:                       # buscamos el que tenga ese id
        if x["id"] == id:
            docente = x
    if docente is None:                   # ese id no existe: volvemos a la lista
        return redirect("/docentes")

    error = None
    mostrar = docente                     # por defecto, mostramos los datos guardados

    if request.method == "POST":          # la persona pulsó Guardar
        datos = leer_formulario()
        error = validar(datos, id)        # le pasamos el id para que no se compare consigo mismo
        if not error:
            docente.update(datos)         # cambia los datos de este docente y mantiene su id
            almacen.guardar_todo("docentes", lista)
            return redirect("/docentes")
        mostrar = datos                   # con error: mostramos lo que escribió

    return render_template("editar_docente.html", error=error, docente=mostrar)


@app.route("/docentes/ficha")
def ficha():
    return render_template("ficha.html")


@app.route("/reportes")
def reportes():
    return render_template("reportes.html")


# Esto enciende el sistema cuando escribimos: python app.py
if __name__ == "__main__":
    app.run(debug=True)
