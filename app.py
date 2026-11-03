import os
from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
cliente = MongoClient(os.getenv("MONGODB_URI"))
db = cliente["legajo_docente"]

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/prueba-db")
def prueba_db():
    db.pruebas.insert_one({"mensaje": "hola desde Flask"})
    total = db.pruebas.count_documents({})
    return f"Conectado a MongoDB. Documentos de prueba: {total}"