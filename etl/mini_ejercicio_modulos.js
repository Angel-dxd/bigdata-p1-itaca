// Mini-ejercicio: agregar a cada Modulo los datos del Curso (ya aplanado).
// Se parte del "Lookup con 2 campos" de la actividad guiada. Como contenidos no
// tiene el campo "ensenanza", la segunda condición del enlace pasa a ser "anyo"
// (un módulo pertenece a un curso de un año concreto).

db.contenidos.aggregate([
{
    $lookup: {
    from: "cursos_planos",
    let: { curso: "$curso", anyo: "$anyo" },                // antes: ensenanza
    pipeline: [
        {
        $match: {
            $expr: {
            $and: [
                { $eq: ["$curso_codigo", "$$curso"] },
                { $eq: ["$anyo", "$$anyo"] }                // antes: "$grado" == "$$ensenanza"
            ]
            }
        }
        },
        { $project: { _id: 0, anyo: 0 } }                   // no duplicar anyo
    ],
    as: "curso_datos"
    }
},
{ $unwind: { path: "$curso_datos", preserveNullAndEmptyArrays: true } },
{ $replaceRoot: { newRoot: { $mergeObjects: ["$$ROOT", "$curso_datos"] } } },
{ $project: { curso_datos: 0 } },
{ $out: "modulos" }                                         // colección modulos del modelo
])
