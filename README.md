# YF Tools Plus para QGIS 3.30+

[![QGIS](https://img.shields.io/badge/QGIS-3.30+-green.svg)](https://qgis.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**YF Tools Plus** es un plugin de topografía que permite crear polígonos rápidamente desde Excel, acortando significativamente el tiempo de elaboración de mapas. Adicionalmente, permite crear y segmentar el polígono en líneas cortadas por los vértices, obteniendo así medidas perimétricas y de azimut.
La herramienta organiza automáticamente la tabla de datos de manera que pueda incluirse directamente en el compositor de mapas, cumpliendo con la estructura que exigen las normas de catastro peruanas. Asimismo, se ha incluido una función que permite exportar las tablas a Excel, el cual se abre automáticamente con un clic, sin necesidad de generar archivos temporales.
YF Tools y Export to Excel (Un Clic) se integran en una sola herramienta integral diseñada para optimizar flujos de trabajo topográficos y de georeferenciación.

---

## 🎯 Características Principales

El plugin se organiza en una interfaz intuitiva con pestañas y accesos rápidos desde la barra de herramientas:

### 1. Exportación Rápida a Excel (Un Clic)
- Exporta la tabla de atributos de cualquier capa vectorial activa a formato Excel (`.xlsx`).
- Ejecución inmediata desde la barra de herramientas.
- Apertura automática del archivo generado para revisión instantánea.

### 2. Conversión de Excel a CSV
- Transforma archivos Excel (`.xlsx`, `.xls`) a formato CSV compatible con QGIS.
- Codificación UTF-8 garantizada para evitar problemas con caracteres especiales.

### 3. Generación de Polígonos desde Coordenadas
- Crea polígonos a partir de listados de coordenadas en archivos CSV.
- Cálculo automático de **Área** (en hectáreas) y **Perímetro** (en metros).
- Soporte para múltiples sistemas de coordenadas (CRS).
- Configuración personalizable de estilos y etiquetado automático.

### 4. Segmentador Avanzado de Polígonos
- Divide polígonos en segmentos y vértices individuales.
- **Cálculos detallados:** Longitudes, azimuts (respecto al norte verdadero), ángulos internos y externos.
- **Orden Inteligente:** Reorganiza los vértices comenzando desde el punto más al norte.
- **Salida Estructurada:** Genera capas independientes de líneas (segmentos) y puntos (vértices) con atributos completos.

---

## 📦 Instalación

### Instalación Manual
1. Descarga el repositorio como un archivo ZIP.
2. Localiza el directorio de plugins de QGIS en tu sistema:
   - **Windows:** `%AppData%\QGIS\QGIS3\profiles\default\python\plugins`
   - **Linux/macOS:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
3. Descomprime el contenido en una carpeta llamada `YF_Tools_Plus`.
4. Abre QGIS y activa el plugin desde el menú `Complementos` -> `Administrar e instalar complementos`.

---

## 🚀 Guía de Uso

### Herramientas en la Barra de Herramientas
- **Icono de Exportación:** Exporta la capa seleccionada a Excel inmediatamente.
- **Icono Principal:** Abre el panel de herramientas completo.

### Panel de Herramientas (4 Pestañas)
1. **Excel a CSV:** Selección de archivo origen y destino para conversión.
2. **Crear Polígono:** Configuración de columnas X/Y, CRS y estilos.
3. **Segmentador:** Selección de capa de polígono y ejecución del proceso de división.
4. **Exportar a Excel:** Opciones avanzadas de exportación con selección de ruta y apertura automática.

---

## 📊 Estructura de Datos de Salida

| Capa | Atributos Generados |
| :--- | :--- |
| **Polígonos** | ID, ÁREA (ha), PERÍMETRO (m) |
| **Segmentos** | ID, Longitud, Azimut (0-360°) |
| **Vértices** | ID, Lado (V-n a V-m), Este, Norte, Distancia, Azimut, Ángulo Interno, Ángulo Externo |

---

## ⚙️ Requisitos y Dependencias
- **QGIS 3.30** o superior.
- **Python 3.9+** (incluido en QGIS).
- Librerías: `PyQt5`, `pandas`, `qgis.core`.

---

## 👤 Autor
**Yuri Caller**
- 📧 Email: [yuricaller@gmail.com](mailto:yuricaller@gmail.com)
- 💻 GitHub: [@yuricaller](https://github.com/yuricaller)

---

## 📄 Licencia
Este proyecto está bajo la **Licencia Pública General GNU v3.0 (GPL-3.0)**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---
*¿Te resulta útil este plugin? ¡Dale una ⭐ en GitHub!*
