# Legajo Docente CERTUS - Paso 4: una direccion para cada pantalla.
from flask import Flask, render_template

app = Flask(__name__)


# Cuando el navegador pide "/" o "/login", mostramos la pantalla de ingreso.
@app.route("/")
@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/docentes")
def docentes():
    return render_template("docentes.html")


@app.route("/docentes/nuevo")
def registrar_docente():
    return render_template("registrar_docente.html")


@app.route("/docentes/editar")
def editar_docente():
    return render_template("editar_docente.html")


@app.route("/docentes/ficha")
def ficha():
    return render_template("ficha.html")


@app.route("/reportes")
def reportes():
    return render_template("reportes.html")


# Esto enciende el sistema cuando escribimos: python app.py
if __name__ == "__main__":
    app.run(debug=True)
