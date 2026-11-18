import json
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient

# La contraseña se lee del .env para no subirla a GitHub
load_dotenv()
contrasenya = quote_plus(os.environ["MONGO_PASSWORD"])

cliente = MongoClient(f"mongodb://admin:{contrasenya}@localhost:27017/")
db = cliente["itaca"]


def cargar_contenidos() -> None:
    with open("data/raw/2025-26/contenidos_2026-10-28.json", encoding="utf-8") as f:
        modulos = json.load(f)
    documentos = [
        {
            "anyo": m["Anyo"],
            "curso": m["Curso"],
            "modulo": m["Modulo"],
            "nombre_modulo": m["Nombre_Modulo"],
        }
        for m in modulos
    ]
    db["contenidos"].insert_many(documentos)


def cargar_cursos() -> None:
    # Necesaria para la actividad guiada (aplanar cursos)
    with open("data/raw/2025-26/cursos_2026-10-28.json", encoding="utf-8") as f:
        cursos = json.load(f)
    documentos = [
        {
            "anyo": c["Anyo"],
            "codigo": c["Codigo"],
            "nombre_cas": c["Nombre_Cas"],
            "nombre_val": c["Nombre_Val"],
            "padre": c["Padre"],
        }
        for c in cursos
    ]
    db["cursos"].insert_many(documentos)


def cargar_alumnos() -> None:
    with open("data/raw/2025-26/alumnos_2026-10-28.json", encoding="utf-8") as f:
        alumnos = json.load(f)
    documentos = [
        {
            "nia": a["NIA"],
            "anyo": a["Anyo"],
            "curso": a["Curso"],
            "turno": a["Turno"],
            "grupo": a["Grupo"],
        }
        for a in alumnos
    ]
    db["alumnos"].insert_many(documentos)


def cargar_calificaciones() -> None:
    with open("data/raw/2025-26/calificaciones_2026-10-28.json", encoding="utf-8") as f:
        calificaciones = json.load(f)
    documentos = [
        {
            "nia": c["NIA"],
            "anyo": c["Anyo"],
            "curso": c["Curso"],
            "modulo": c["Modulo"],
            "nota": c["Nota"],
            "evaluacion": c["Evaluacion"],
        }
        for c in calificaciones
    ]
    db["calificaciones"].insert_many(documentos)


def crear_indices() -> None:
    db["calificaciones"].create_index([("curso", 1), ("anyo", 1), ("evaluacion", 1)])
    db["calificaciones"].create_index("nia")
    # Sin unique: en ITACA un alumno puede aparecer en varios grupos/cursos el mismo año
    db["alumnos"].create_index([("nia", 1), ("anyo", 1)])
    db["contenidos"].create_index([("modulo", 1), ("anyo", 1), ("curso", 1)], unique=True)


if __name__ == "__main__":
    cargar_contenidos()
    cargar_cursos()
    cargar_alumnos()
    cargar_calificaciones()
    crear_indices()
    print("Carga completada.")
