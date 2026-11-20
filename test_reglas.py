# Pruebas unitarias de las reglas del negocio - Legajo Docente CERTUS (Grupo 5)
# Cada prueba tiene 3 pasos: Preparar, Ejecutar, Verificar.
import tempfile
import almacen
import app as legajo


# ======================= funciones =======================
def datos_nuevos():
    """Cada prueba empieza con una carpeta de datos vacía y temporal (no toca los datos reales)."""
    almacen.CARPETA = tempfile.mkdtemp()


def usuario_registrado(correo, rol="gestor"):
    """Deja a una persona ya registrada con un rol (sin pasar por la pantalla de usuarios)."""
    almacen.agregar("usuarios", {"nombre": "Persona de prueba", "correo": correo, "rol": rol})


def cliente_con_rol(rol, correo="persona@certus.edu.pe"):
    """Un navegador que YA ingresó con ese rol. Sirve para probar a qué pantallas puede entrar."""
    cliente = legajo.app.test_client()
    with cliente.session_transaction() as sesion:
        sesion["correo"] = correo
        sesion["rol"] = rol
    return cliente


def puede_abrir(cliente, direccion):
    """True si la pantalla se abre; False si el sistema lo manda a otro lado.
    Si la pantalla ni siquiera existe, la prueba falla (así no sale verde por error)."""
    respuesta = cliente.get(direccion)
    assert respuesta.status_code != 404, "la pantalla " + direccion + " no existe"
    return respuesta.status_code == 200


def ingresar(correo):
    """Escribe el correo en el login. Devuelve True si el sistema deja entrar."""
    respuesta = legajo.app.test_client().post("/login", data={"correo": correo})
    return respuesta.status_code == 302


def intentar_ingresar(correo, rol="gestor"):
    """Igual que ingresar, pero la persona ya está registrada con un rol.
    Así las Reglas 01 solo prueban cómo está escrito el correo."""
    datos_nuevos()
    usuario_registrado(correo.strip().lower(), rol)
    return ingresar(correo)


def registrar_docente(nombre="Ana Ruiz", correo="ana@certus.edu.pe", carrera="Sistemas", telefono="", ingreso=""):
    """Llena el formulario 'Registrar docente' (como gestor). Devuelve True si el docente se guardó."""
    datos = {"nombre": nombre, "correo": correo, "carrera": carrera, "telefono": telefono, "ingreso": ingreso}
    respuesta = cliente_con_rol("gestor").post("/docentes/nuevo", data=datos)
    return respuesta.status_code == 302


def corregir_docente(id, nombre="Ana Ruiz", correo="ana@certus.edu.pe", carrera="Sistemas"):
    """Llena el formulario 'Editar docente' (como gestor). Devuelve True si los cambios se guardaron."""
    datos = {"nombre": nombre, "correo": correo, "carrera": carrera, "telefono": "", "ingreso": ""}
    respuesta = cliente_con_rol("gestor").post(f"/docentes/{id}/editar", data=datos)
    return respuesta.status_code == 302


def registrar_usuario(nombre="Ana Ruiz", correo="ana@certus.edu.pe", rol="gestor", quien="administrador"):
    """Llena el formulario 'Registrar usuario'. Devuelve True si el usuario se guardó."""
    datos = {"nombre": nombre, "correo": correo, "rol": rol}
    respuesta = cliente_con_rol(quien).post("/usuarios/nuevo", data=datos)
    assert respuesta.status_code != 404, "la pantalla /usuarios/nuevo no existe"
    return respuesta.status_code == 302 and respuesta.headers["Location"].endswith("/usuarios")


def ids_guardados():
    return [d["id"] for d in almacen.leer("docentes")]


def buscar(texto):
    """Escribe en el buscador y devuelve lo que aparece en pantalla."""
    return cliente_con_rol("gestor").get("/docentes?buscar=" + texto).get_data(as_text=True)


# ===================== REGLA 01: solo entra correo @certus.edu.pe =====================
def test_regla01_entra_con_correo_de_certus():
    correo = "ana@certus.edu.pe"                  # Preparar
    entra = intentar_ingresar(correo)             # Ejecutar
    assert entra == True                          # Verificar

def test_regla01_no_entra_con_gmail():
    correo = "ana@gmail.com"
    entra = intentar_ingresar(correo)
    assert entra == False

def test_regla01_no_entra_solo_con_el_dominio():
    correo = "@certus.edu.pe"
    entra = intentar_ingresar(correo)
    assert entra == False

def test_regla01_entra_con_mayusculas_y_espacios():
    correo = "  ANA@CERTUS.EDU.PE "
    entra = intentar_ingresar(correo)
    assert entra == True

def test_regla01_no_entra_con_gmail_pegado_a_certus():
    correo = "ana@gmail.com@certus.edu.pe"
    entra = intentar_ingresar(correo)
    assert entra == False

def test_regla01_no_entra_con_dos_arrobas_seguidas():
    correo = "@@certus.edu.pe"
    entra = intentar_ingresar(correo)
    assert entra == False


# ============ REGLA 02: no se registra un docente incompleto ============
def test_regla02_registra_un_docente_completo():
    datos_nuevos()
    guardado = registrar_docente(nombre="Ana Ruiz", correo="ana@certus.edu.pe", carrera="Sistemas")
    assert guardado == True

def test_regla02_no_registra_sin_nombre():
    datos_nuevos()
    guardado = registrar_docente(nombre="")
    assert guardado == False

def test_regla02_no_registra_sin_carrera():
    datos_nuevos()
    guardado = registrar_docente(carrera="")
    assert guardado == False

def test_regla02_telefono_y_fecha_son_opcionales():
    datos_nuevos()
    guardado = registrar_docente(telefono="", ingreso="")
    assert guardado == True


# ============ REGLA 03: no hay dos docentes con el mismo correo ============
def test_regla03_no_registra_un_correo_repetido():
    datos_nuevos()
    registrar_docente(correo="ana@certus.edu.pe")
    guardado = registrar_docente(nombre="Otra Persona", correo="ana@certus.edu.pe")
    assert guardado == False

def test_regla03_no_registra_el_mismo_correo_en_mayusculas():
    datos_nuevos()
    registrar_docente(correo="ana@certus.edu.pe")
    guardado = registrar_docente(nombre="Otra Persona", correo="ANA@CERTUS.EDU.PE")
    assert guardado == False

def test_regla03_al_corregir_no_se_puede_usar_el_correo_de_otro():
    datos_nuevos()
    registrar_docente(nombre="Ana", correo="ana@certus.edu.pe")
    registrar_docente(nombre="Beto", correo="beto@certus.edu.pe")
    id_de_beto = ids_guardados()[1]
    guardado = corregir_docente(id_de_beto, nombre="Beto", correo="ana@certus.edu.pe")
    assert guardado == False

def test_regla03_al_corregir_si_se_puede_dejar_su_propio_correo():
    datos_nuevos()
    registrar_docente(nombre="Ana", correo="ana@certus.edu.pe")
    id_de_ana = ids_guardados()[0]
    guardado = corregir_docente(id_de_ana, nombre="Ana María", correo="ana@certus.edu.pe")
    assert guardado == True


# ============ REGLA 04: cada docente tiene su propio número único ============
def test_regla04_el_primer_docente_recibe_el_numero_1():
    datos_nuevos()
    registrar_docente(correo="a@certus.edu.pe")
    assert ids_guardados() == [1]

def test_regla04_el_segundo_docente_recibe_el_numero_2():
    datos_nuevos()
    registrar_docente(correo="a@certus.edu.pe")
    registrar_docente(correo="b@certus.edu.pe")
    assert ids_guardados() == [1, 2]

def test_regla04_un_numero_borrado_no_se_vuelve_a_usar():
    datos_nuevos()
    for letra in "abc":
        registrar_docente(correo=letra + "@certus.edu.pe")     # números 1, 2 y 3
    almacen.guardar_todo("docentes", almacen.leer("docentes")[:2])   # se borra el docente 3
    registrar_docente(correo="d@certus.edu.pe")                 # docente nuevo
    assert ids_guardados()[-1] != 3


# ============ REGLA 05: lo guardado se conserva igual (tildes y ñ) ============
def test_regla05_se_conservan_las_tildes_y_la_enie():
    datos_nuevos()
    registrar_docente(nombre="María Peña Núñez")
    assert almacen.leer("docentes")[0]["nombre"] == "María Peña Núñez"

def test_regla05_el_archivo_se_lee_con_letras_normales():
    datos_nuevos()
    registrar_docente(nombre="María Peña")
    texto = open(almacen.ruta("docentes"), encoding="utf-8").read()
    assert "María Peña" in texto

def test_regla05_varios_docentes_se_conservan_en_orden():
    datos_nuevos()
    for nombre, letra in [("Ana", "a"), ("Beto", "b"), ("Carla", "c")]:
        registrar_docente(nombre=nombre, correo=letra + "@certus.edu.pe")
    nombres = [d["nombre"] for d in almacen.leer("docentes")]
    assert nombres == ["Ana", "Beto", "Carla"]

def test_regla05_un_dato_vacio_se_conserva_vacio():
    datos_nuevos()
    registrar_docente(telefono="")
    assert almacen.leer("docentes")[0]["telefono"] == ""


# ============ REGLA 06: el buscador encuentra por nombre o carrera ============
def preparar_buscador():
    datos_nuevos()
    registrar_docente(nombre="Rosa Medina", correo="r@certus.edu.pe", carrera="Contabilidad")
    registrar_docente(nombre="María Torres", correo="m@certus.edu.pe", carrera="Administración")

def test_regla06_encuentra_por_nombre():
    preparar_buscador()
    pantalla = buscar("Rosa")
    assert "Rosa Medina" in pantalla

def test_regla06_encuentra_por_carrera():
    preparar_buscador()
    pantalla = buscar("Cont")
    assert "Rosa Medina" in pantalla

def test_regla06_no_importan_las_mayusculas():
    preparar_buscador()
    pantalla = buscar("ROSA")
    assert "Rosa Medina" in pantalla

def test_regla06_no_importan_las_tildes():
    preparar_buscador()
    pantalla = buscar("maria")
    assert "María Torres" in pantalla

def test_regla06_encuentra_por_apellido():
    preparar_buscador()
    pantalla = buscar("Medina")
    assert "Rosa Medina" in pantalla


# ============ REGLA 07: corregir un docente que no existe vuelve a la lista ============
def test_regla07_abrir_un_docente_que_no_existe_vuelve_a_la_lista():
    datos_nuevos()
    respuesta = cliente_con_rol("gestor").get("/docentes/99/editar")
    assert respuesta.status_code == 302 and respuesta.headers["Location"].endswith("/docentes")

def test_regla07_guardar_un_docente_que_no_existe_no_crea_nada():
    datos_nuevos()
    corregir_docente(99, nombre="Fantasma", correo="f@certus.edu.pe")
    assert almacen.leer("docentes") == []


# ============ REGLA 08: solo entra quien está registrado con un rol ============
def test_regla08_entra_el_administrador_inicial():
    datos_nuevos()
    entra = ingresar("admin@certus.edu.pe")
    assert entra == True

def test_regla08_no_entra_un_correo_de_certus_sin_rol():
    datos_nuevos()
    entra = ingresar("ana@certus.edu.pe")
    assert entra == False

def test_regla08_no_abre_la_lista_sin_haber_ingresado():
    datos_nuevos()
    sin_ingresar = legajo.app.test_client()
    assert puede_abrir(sin_ingresar, "/docentes") == False

def test_regla08_entra_un_registrado_aunque_escriba_mayusculas():
    datos_nuevos()
    usuario_registrado("ana@certus.edu.pe", "gestor")
    entra = ingresar("  ANA@CERTUS.EDU.PE ")
    assert entra == True


# ============ REGLA 09: cada persona ve solo lo de su rol ============
def test_regla09_el_gestor_entra_a_la_lista_de_docentes():
    datos_nuevos()
    assert puede_abrir(cliente_con_rol("gestor"), "/docentes") == True

def test_regla09_el_gestor_no_entra_a_usuarios():
    datos_nuevos()
    assert puede_abrir(cliente_con_rol("gestor"), "/usuarios") == False

def test_regla09_el_docente_no_entra_a_usuarios():
    datos_nuevos()
    assert puede_abrir(cliente_con_rol("docente"), "/usuarios") == False

def test_regla09_el_docente_no_entra_a_la_lista_de_docentes():
    datos_nuevos()
    assert puede_abrir(cliente_con_rol("docente"), "/docentes") == False

def test_regla09_el_docente_no_entra_a_reportes():
    datos_nuevos()
    assert puede_abrir(cliente_con_rol("docente"), "/reportes") == False


# ============ REGLA 10: un docente solo ve su propia ficha ============
def test_regla10_el_docente_ve_su_propia_ficha():
    datos_nuevos()
    registrar_docente(nombre="Ana", correo="ana@certus.edu.pe")           # ficha número 1
    ana = cliente_con_rol("docente", "ana@certus.edu.pe")
    assert puede_abrir(ana, "/docentes/1/ficha") == True

def test_regla10_el_docente_no_ve_la_ficha_de_otro():
    datos_nuevos()
    registrar_docente(nombre="Ana", correo="ana@certus.edu.pe")           # ficha número 1
    registrar_docente(nombre="Beto", correo="beto@certus.edu.pe")         # ficha número 2
    ana = cliente_con_rol("docente", "ana@certus.edu.pe")
    assert puede_abrir(ana, "/docentes/2/ficha") == False

def test_regla10_un_docente_sin_ficha_no_entra():
    datos_nuevos()
    usuario_registrado("beto@certus.edu.pe", "docente")                   # tiene rol, pero no tiene ficha
    entra = ingresar("beto@certus.edu.pe")
    assert entra == False


# ============ REGLA 11: solo el administrador registra usuarios, y el rol es uno de los tres ============
def test_regla11_el_administrador_registra_un_usuario():
    datos_nuevos()
    guardado = registrar_usuario(correo="ana@certus.edu.pe", rol="gestor", quien="administrador")
    assert guardado == True

def test_regla11_el_gestor_no_puede_registrar_usuarios():
    datos_nuevos()
    guardado = registrar_usuario(correo="ana@certus.edu.pe", quien="gestor")
    assert guardado == False

def test_regla11_no_registra_un_rol_que_no_existe():
    datos_nuevos()
    guardado = registrar_usuario(rol="jefe")
    assert guardado == False

def test_regla11_no_registra_un_correo_que_no_es_de_certus():
    datos_nuevos()
    guardado = registrar_usuario(correo="ana@gmail.com")
    assert guardado == False


# ============ REGLA 12: no hay dos usuarios con el mismo correo ============
def test_regla12_no_registra_un_correo_repetido():
    datos_nuevos()
    registrar_usuario(correo="ana@certus.edu.pe")
    guardado = registrar_usuario(nombre="Otra Persona", correo="ana@certus.edu.pe")
    assert guardado == False

def test_regla12_no_registra_el_mismo_correo_en_mayusculas():
    datos_nuevos()
    registrar_usuario(correo="ana@certus.edu.pe")
    guardado = registrar_usuario(nombre="Otra Persona", correo="ANA@CERTUS.EDU.PE")
    assert guardado == False


# ============ Ejecutor simple: no necesita pytest ============
if __name__ == "__main__":
    pruebas = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    pruebas.sort(key=lambda p: p[1].__code__.co_firstlineno)
    verdes = 0
    for i, (nombre, f) in enumerate(pruebas, 1):
        try:
            f(); estado = "VERDE"; verdes += 1
        except AssertionError:
            estado = "ROJO "
        except Exception as e:
            estado = "ERROR"
        regla = nombre.split("_")[1].replace("regla", "Regla ")
        print(f"PU-{i:02d}  {regla}  {estado}  {nombre[len('test_regla00_'):]}")
    print(f"\n{verdes} verdes y {len(pruebas) - verdes} en rojo, de {len(pruebas)} pruebas")
