import almacen

almacen.agregar("docentes", {
    "nombre": "María Torres Quispe",
    "correo": "mtorres@certus.edu.pe",
    "carrera": "Administración",
    "telefono": "987 654 321",
    "ingreso": "2019-03-01",
})
almacen.agregar("docentes", {
    "nombre": "Luis Ramos Peña",
    "correo": "lramos@certus.edu.pe",
    "carrera": "Sistemas",
    "telefono": "",
    "ingreso": "2020-08-10",
})

for d in almacen.leer("docentes"):
    print(d["id"], d["nombre"])
