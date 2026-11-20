# Legajo Docente CERTUS - Semana 5 (pasos 4 al 7) + Paso 7B: roles.
from flask import Flask, render_template, request, redirect, session

import unicodedata

import almacen

app = Flask(__name__)
# Clave para que Flask pueda "firmar" la memoria (session) de cada persona.
app.secret_key = "legajo-certus-grupo5"

# Los tres roles del sistema y el administrador con el que empieza todo.
ROLES = ["administrador", "gestor", "docente"]
ADMIN_INICIAL = "admin@certus.edu.pe"


def correo_valido(correo):
    # Un correo de CERTUS tiene algo ANTES de "@certus.edu.pe", sin otra "@" ni espacios.
    if not correo.endswith("@certus.edu.pe"):
        return False
    usuario = correo[:-len("@certus.edu.pe")]
    return usuario != "" and "@" not in usuario and " " not in usuario


def limpiar(texto):
    # Pasa a minúsculas y quita las tildes: "María" -> "maria".
    separado = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in separado if not unicodedata.combining(c))


def coincide(buscado, valor):
    # True si lo buscado es el inicio del texto o el inicio de alguna de sus palabras.
    # Ej.: "medina" coincide con "Rosa Medina"; "maria" coincide con "María Torres".
    buscado = limpiar(buscado)
    valor = limpiar(valor)
    if valor.startswith(buscado):
        return True
    for palabra in valor.split():
        if palabra.startswith(buscado):
            return True
    return False


def leer_usuarios():
    # Trae todos los usuarios. Si todavía no hay ninguno, crea al administrador inicial.
    usuarios = almacen.leer("usuarios")
    if not usuarios:
        almacen.agregar("usuarios", {"nombre": "Administrador", "correo": ADMIN_INICIAL, "rol": "administrador"})
        usuarios = almacen.leer("usuarios")
    return usuarios


def buscar_usuario(correo):
    # Devuelve el usuario con ese correo, o None si no está registrado.
    for u in leer_usuarios():
        if u["correo"] == correo:
            return u
    return None


def ficha_propia(correo):
    # La ficha de un docente se enlaza con su usuario por el correo.
    for d in almacen.leer("docentes"):
        if d["correo"] == correo:
            return d
    return None


def pantalla_de_inicio():
    # A dónde va cada persona al entrar (y cuando intenta abrir una pantalla que no le toca).
    rol = session.get("rol")
    if rol == "docente":
        ficha = ficha_propia(session.get("correo"))
        if ficha:
            return "/docentes/" + str(ficha["id"]) + "/ficha"
        return "/login"
    if rol:
        return "/docentes"
    return "/login"


def sin_permiso(*roles):
    # Si el rol de la persona NO está entre los permitidos, devuelve el redirect que la saca de ahí.
    # Si está permitido, devuelve None y la pantalla sigue con normalidad.
    if session.get("rol") not in roles:
        return redirect(pantalla_de_inicio())
    return None


def leer_formulario_usuario():
    return {
        "nombre": request.form["nombre"].strip(),
        "correo": request.form["correo"].strip().lower(),
        "rol": request.form["rol"],
    }


def validar_usuario(datos):
    # Devuelve un TEXTO con el problema, o None si todo está bien.
    if not datos["nombre"] or not datos["correo"] or not datos["rol"]:
        return "Nombre, correo y rol son obligatorios."
    if datos["rol"] not in ROLES:
        return "El rol debe ser administrador, gestor o docente."
    if not correo_valido(datos["correo"]):
        return "El correo debe terminar en @certus.edu.pe."
    if buscar_usuario(datos["correo"]) is not None:
        return "Ese correo ya está registrado como usuario."
    return None


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
    if not correo_valido(datos["correo"]):
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
        if not correo_valido(correo):
            return render_template("login.html", error="Usa tu correo institucional (@certus.edu.pe).")
        usuario = buscar_usuario(correo)
        if usuario is None:
            return render_template("login.html", error="Tu correo no está registrado. Pide al administrador que te registre.")
        session["correo"] = correo
        session["rol"] = usuario["rol"]
        destino = pantalla_de_inicio()
        if destino == "/login":          # es docente, pero todavía no tiene ficha
            session.clear()
            return render_template("login.html", error="Todavía no tienes una ficha registrada. Consulta a Gestión Docente.")
        return redirect(destino)
    session.clear()  # al entrar o pulsar "Salir", se olvida el correo y el rol
    return render_template("login.html", error=None)


@app.route("/docentes")
def docentes():
    bloqueo = sin_permiso("administrador", "gestor")
    if bloqueo:
        return bloqueo

    lista = almacen.leer("docentes")
    escrito = request.args.get("buscar", "").strip()   # lo que se escribió en la barra
    if escrito:                                        # solo filtramos si escribió algo
        encontrados = []
        for d in lista:
            if coincide(escrito, d["nombre"]) or coincide(escrito, d["carrera"]):
                encontrados.append(d)
        lista = encontrados
    return render_template("docentes.html", docentes=lista, buscar=escrito)


@app.route("/docentes/nuevo", methods=["GET", "POST"])
def registrar_docente():
    bloqueo = sin_permiso("administrador", "gestor")
    if bloqueo:
        return bloqueo

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
    bloqueo = sin_permiso("administrador", "gestor")
    if bloqueo:
        return bloqueo

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


@app.route("/docentes/<int:id>/ficha")
def ficha(id):
    bloqueo = sin_permiso("administrador", "gestor", "docente")
    if bloqueo:
        return bloqueo
    docente = None
    for x in almacen.leer("docentes"):
        if x["id"] == id:
            docente = x
    if docente is None:                   # ese número no existe
        return redirect(pantalla_de_inicio())
    if session["rol"] == "docente" and docente["correo"] != session["correo"]:
        return redirect(pantalla_de_inicio())   # un docente solo ve SU ficha
    return render_template("ficha.html", docente=docente)


@app.route("/usuarios")
def usuarios():
    bloqueo = sin_permiso("administrador")
    if bloqueo:
        return bloqueo
    return render_template("usuarios.html", usuarios=leer_usuarios())


@app.route("/usuarios/nuevo", methods=["GET", "POST"])
def registrar_usuario():
    bloqueo = sin_permiso("administrador")
    if bloqueo:
        return bloqueo
    error = None
    mostrar = {}

    if request.method == "POST":
        datos = leer_formulario_usuario()
        error = validar_usuario(datos)
        if not error:
            almacen.agregar("usuarios", datos)
            return redirect("/usuarios")
        mostrar = datos

    return render_template("usuarios_nuevo.html", error=error, usuario=mostrar, roles=ROLES)


@app.route("/reportes")
def reportes():
    bloqueo = sin_permiso("administrador", "gestor")
    if bloqueo:
        return bloqueo

    return render_template("reportes.html")


# Esto enciende el sistema cuando escribimos: python app.py
if __name__ == "__main__":
    app.run(debug=True)
