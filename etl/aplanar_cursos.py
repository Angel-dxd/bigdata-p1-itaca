import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
contrasenya = quote_plus(os.environ["MONGO_PASSWORD"])

cliente = MongoClient(f"mongodb://admin:{contrasenya}@localhost:27017/")
db = cliente["itaca"]
coleccion = db["cursos"]

pipeline = [
    {"$match": {"nombre_cas": {"$regex": "^(Primero|Segundo)"}}},

    {"$lookup": {"from": "cursos", "localField": "padre", "foreignField": "codigo", "as": "ciclo"}},
    {"$unwind": "$ciclo"},
    {"$lookup": {"from": "cursos", "localField": "ciclo.padre", "foreignField": "codigo", "as": "grado"}},
    {"$unwind": "$grado"},
    {"$lookup": {"from": "cursos", "localField": "grado.padre", "foreignField": "codigo", "as": "familia"}},
    {"$unwind": "$familia"},

    {"$project": {
        "_id": 0,
        "anyo": "$anyo",  # añadido: necesario para el lookup del mini-ejercicio
        "familia": "$familia.nombre_cas",
        "grado": "$grado.nombre_cas",
        "ciclo": "$ciclo.nombre_cas",
        "ciclo_abreviatura": "$ciclo.abreviatura",
        "primseg": {"$arrayElemAt": [{"$split": ["$nombre_cas", " "]}, 0]},
        "curso_codigo": "$codigo",
        "curso_abreviatura": "$abreviatura",
    }},
    {"$out": "cursos_planos"},
]

coleccion.aggregate(pipeline)
print("Colección cursos_planos creada:", db["cursos_planos"].count_documents({}), "documentos")
