# Proyecto N · [bigdata-p1-itaca]

> **Plantilla.** Sustituye todo lo que va entre corchetes y borra las indicaciones en cursiva a medida que completes cada sección. Borra también las secciones de bloques que tu proyecto no trabaje.

## Descripción y objetivo

Construir un dashboard de análisis académico en Power BI a partir de datos reales de la plataforma ITACA de la Conselleria de Educación, extraídos como ficheros XML.

[Descripción]

## Arquitectura

*Diagrama del pipeline completo. Empieza con uno provisional en el Bloque 0 y actualízalo al terminar cada bloque.*

```mermaid
graph LR
    A[Fuente de datos] --> B[Ingesta]
    B --> C[Almacenamiento]
    C --> D[Procesamiento]
    D --> E[Visualización / modelo]