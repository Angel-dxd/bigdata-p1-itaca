# Proyecto 1 · Analítica académica ITACA (origen XML)

## Descripción y objetivo

Construir un dashboard de análisis académico en Power BI a partir de datos reales de la plataforma ITACA de la Conselleria de Educación, extraídos como ficheros XML.


## Arquitectura

*Diagrama del pipeline completo. Empieza con uno provisional en el Bloque 0 y actualízalo al terminar cada bloque.*

```mermaid
graph LR
    A[Fuente de datos] --> B[Ingesta]
    B --> C[Almacenamiento]
    C --> D[Procesamiento]
    D --> E[Visualización / modelo]
```

## Fuentes de datos

**Origen:** exportación XML de ITACA (CIPFP Mislata, código 46019660), un directorio por curso
escolar en `data/exportaciones/Analisis_Academico/<AAAA-AA>/` (2021-22 a 2025-26).

**Mecanismo de acceso:** ficheros XML exportados manualmente desde ITACA. Cada fichero tiene un
nodo raíz `<centro curso="AAAA">` (de donde sale el `Anyo`), un nodo contenedor y un elemento por
registro con los datos como **atributos**. No requiere credenciales.

| Tabla | Fichero | Campos disponibles (relevantes) |
|---|---|---|
| Alumnos | `alumnos.xml` | NIA, curso, grupo, turno, ensenanza, linea, modalidad, repite, estado_matricula (+ datos personales que **no** se ingestan) |
| Calificaciones | `calificaciones.xml` | alumno (NIA), curso, contenido (módulo), nota_numerica, evaluacion, tipo_nota |
| Contenidos (módulos) | `contenidos.xml` | codigo, nombre_cas, nombre_val, curso |
| Cursos | `cursos.xml` | codigo, nombre_cas, nombre_val, abreviatura, padre (jerarquía familia → grado → ciclo → curso) |
| Grupos | `grupos.xml` | codigo, nombre, turno, linea, modalidad, aula, capacidad |


**Frecuencia de actualización esperada:** una exportación completa por curso escolar, con
reexportaciones al cierre de cada evaluación para actualizar las calificaciones.
