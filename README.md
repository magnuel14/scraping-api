# Web Scraping – Catálogo de productos Fitpoint

## 📌 Descripción

Este proyecto consiste en la extracción, limpieza y estructuración de datos desde una página web pública de comercio electrónico:

👉 https://fitpoint.ec/

Se desarrolló un proceso completo de web scraping para obtener el catálogo de productos de diferentes marcas, procesar los datos y generar un dataset final en formato CSV y Excel.

---

## 🎯 Objetivos de la actividad

- Elegir una página pública
- Extraer datos estructurados
- Limpiar y procesar datos
- Generar un dataset útil
- Guardar los resultados en formato CSV
- Subir el proyecto a un repositorio

---

## 🌐 Fuente de datos

Se utilizó la tienda en línea Fitpoint, extrayendo productos de las siguientes marcas:

- Asics
- 2XU
- Champion
- Ecco
- Fjallraven
- Hydro Flask

Cada marca contiene múltiples productos distribuidos en varias páginas (paginación).

---

## ⚙️ Tecnologías utilizadas

- Python
- Requests
- BeautifulSoup
- Pandas
- JSON / CSV / Excel

---

## 🔄 Flujo del proceso

El proyecto se desarrolló en tres etapas:

### 1. Extracción de datos

Se realizó scraping del catálogo de productos desde Fitpoint:

- navegación automática por paginación
- extracción de:
  - marca
  - nombre del producto
  - precio
  - URL del producto

Los datos se almacenaron inicialmente en formato JSON:

```bash
data/dataInicial/
```

Ejemplo de estructura:


```bash
{
  "brand": "Asics",
  "title": "Zapatos Asics Gel-Cumulus 27 Mujer",
  "price": "$129.43",
  "url": "https://fitpoint.ec/..."
}
```

### 2. Limpieza y procesamiento

Se procesaron los datos para mejorar su calidad:

- eliminación de productos duplicados
- limpieza de caracteres innecesarios en precios (ej: "$")
- normalización de valores numéricos
- estandarización de texto (espacios y formato)

Los datos limpios se almacenaron en:

```bash
data/dataClean/
```

### 2. Limpieza y procesamiento

Se procesaron los datos para mejorar su calidad::

- eliminación de productos duplicados
- limpieza de caracteres innecesarios en precios (ej: "$")
- normalización de valores numéricos
- estandarización de texto (espacios y formato)

Los datos limpios se almacenaron en:

```bash
data/dataClean/
```
### 2. Consolidación del dataset

Se unificaron todos los catálogos en un solo dataset:

- combinación de múltiples marcas
- estructura uniforme de datos
- integración de todos los registros en una sola base

Los resultados finales se guardaron en:

```bash
data/dataFinal/
```
Archivos generados:

- baseProductos.csv
- baseProductos.xlsx

## 📊 Estructura del dataset final

Cada registro contiene:

- brand → marca del producto
- title → nombre del producto
- price → precio (valor numérico limpio)
- url → enlace del producto

---

📌 Conclusión

El proyecto demuestra la capacidad de:

- extraer datos desde páginas web reales
- transformar datos no estructurados en datasets útiles
- aplicar técnicas de limpieza y procesamiento de datos
- generar información lista para análisis

Además, se construyó un dataset completo de productos de múltiples marcas, que puede ser utilizado para análisis posteriores.

---

## 👨‍💻 Equipo de desarrollo

- **Erick Cárdenas**
- **Santiago Bravo**
- **Manuel Vicente**
