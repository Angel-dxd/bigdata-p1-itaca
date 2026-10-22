import os
import hashlib
import json
import logging
import xml.etree.ElementTree as ET
from datetime import date

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ingesta_itaca_xml")

RUTA_ORIGEN = "data/exportaciones/Analisis_Academico"
RUTA_RAW = "data/raw"

TABLAS = ["alumnos", "cursos", "calificaciones", "contenidos", "grupos"]
TABLAS_CON_NIA = ["alumnos", "calificaciones"]

# Campo del modelo -> atributo en el XML de ITACA ("Anyo" se añade desde la raíz)
CAMPOS = {
    "alumnos": {"NIA": "NIA", "Curso": "curso", "Turno": "turno", "Grupo": "grupo"},
    "cursos": {"Codigo": "codigo", "Nombre_Cas": "nombre_cas", "Nombre_Val": "nombre_val", "Padre": "padre"},
    "calificaciones": {"NIA": "alumno", "Curso": "curso", "Modulo": "contenido",
                       "Nota": "nota_numerica", "Evaluacion": "evaluacion"},
    "contenidos": {"Curso": "curso", "Modulo": "codigo", "Nombre_Modulo": "nombre_cas"},
    "grupos": {"Grupo": "codigo", "Nombre": "nombre", "Turno": "turno",
               "Modalidad": "modalidad", "Capacidad": "capacidad"},
}


def limpiar(valor: str | None) -> str | None:
    """ITACA marca los campos vacíos con un espacio: los convertimos en None."""
    if valor is None or not valor.strip():
        return None
    return valor.strip()


def listar_anyos() -> list[str]:
    return sorted(
        d for d in os.listdir(RUTA_ORIGEN)
        if os.path.isdir(os.path.join(RUTA_ORIGEN, d))
    )


def parsear_xml(ruta: str, tabla: str) -> list[dict]:
    raiz = ET.parse(ruta).getroot()          # <centro curso="2021" ...>
    anyo = raiz.get("curso")
    contenedor = raiz.find(tabla)            # <alumnos>, <cursos>...
    if contenedor is None:
        raise ValueError(f"no se encuentra el nodo <{tabla}>")
    registros = []
    for nodo in contenedor:                  # cada <alumno .../>
        fila = {"Anyo": anyo}
        for campo, atributo in CAMPOS[tabla].items():
            fila[campo] = limpiar(nodo.get(atributo))
        registros.append(fila)
    return registros


# NIA original -> NIA anónimo. Se calcula una sola vez por NIA y se reutiliza
# en todas las tablas, para que alumnos y calificaciones se sigan pudiendo cruzar.
NIAS_ANONIMOS: dict[str, str] = {}


def anonimizar_nia(nia: str) -> str:
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]


def anonimizar_registros(registros: list[dict]) -> None:
    for fila in registros:
        nia = fila["NIA"]
        if nia not in NIAS_ANONIMOS:
            NIAS_ANONIMOS[nia] = anonimizar_nia(nia)
        fila["NIA"] = NIAS_ANONIMOS[nia]


def guardar(datos: list[dict], anyo: str, tabla: str) -> None:
    fecha = date.today().isoformat()
    carpeta = os.path.join(RUTA_RAW, anyo)              # data/raw/2021-22
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{tabla}_{fecha}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    logger.info("Guardados %d registros en %s", len(datos), ruta)


if __name__ == "__main__":
    errores = 0
    for anyo in listar_anyos():                         # bucle 1: cada año
        for tabla in TABLAS:                            # bucle 2: cada tabla
            ruta = os.path.join(RUTA_ORIGEN, anyo, f"{tabla}.xml")
            try:
                registros = parsear_xml(ruta, tabla)
            except (FileNotFoundError, ET.ParseError, ValueError) as e:
                logger.error("No se pudo leer %s: %s", ruta, e)
                errores += 1
                continue
            if tabla in TABLAS_CON_NIA:
                anonimizar_registros(registros)     # antes de guardar, nunca después
            guardar(registros, anyo, tabla)

    logger.info("NIA anonimizados: %d alumnos distintos", len(NIAS_ANONIMOS))

    if errores:
        logger.warning("Ingesta terminada con %d ficheros con error", errores)
    else:
        logger.info("Ingesta completada sin errores")
