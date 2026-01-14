YF Tools Plus para QGIS 3.30+
Plugin unificado que combina las funcionalidades de YF_Tools y Export to Excel (Un Clic) en una sola herramienta completa para trabajos topográficos y de georeferenciación.

🎯 Características
1. Exportar a Excel (Un Clic)

Exporta la tabla de atributos de cualquier capa vectorial activa a Excel (.xlsx)
Con un solo clic desde la barra de herramientas
Abre automáticamente el archivo generado
No requiere configuración adicional

2. Convertir Excel a CSV

Transforma archivos Excel en formato CSV para su uso en QGIS
Soporta formatos .xlsx y .xls
Codificación UTF-8 por defecto

3. Crear Polígonos desde Coordenadas

Genera polígonos a partir de coordenadas almacenadas en archivos CSV
Calcula automáticamente área y perímetro
Configuración personalizable de estilos y etiquetas
Soporta diferentes sistemas de coordenadas (CRS)

4. Segmentador de Polígonos

Divide polígonos en segmentos y vértices individuales
Calcula longitudes y azimuts de cada segmento
Calcula ángulos internos y externos en cada vértice
Reorganiza vértices comenzando desde el norte
Genera dos capas nuevas: una de líneas (segmentos) y otra de puntos (vértices)
Etiquetas automáticas con información detallada

📦 Instalación
Instalación Manual

Descarga el plugin:

Descarga el archivo YF_Tools_Plus.zip

[IMAGEN: Captura de pantalla del botón de descarga del plugin]

Localiza el directorio de plugins de QGIS:

Windows: C:\Users\<tu_usuario>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
macOS: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python\plugins

Instala el plugin:

Descomprime el archivo ZIP en el directorio de plugins
Esto creará una carpeta llamada YF_Tools_Plus

[IMAGEN: Captura de pantalla de la carpeta del plugin en el directorio de plugins]

Activa el plugin en QGIS:

Abre QGIS
Ve a Complementos → Administrar e Instalar Complementos...
Busca "YF Tools Plus"
Marca la casilla para activarlo

[IMAGEN: Captura de pantalla del administrador de complementos de QGIS con el plugin activado]

🚀 Uso
Exportación Rápida a Excel (Un Clic)

Selecciona la capa vectorial que deseas exportar
Haz clic en el botón "Exportar a Excel (Un Clic)" en la barra de herramientas
El archivo se guardará automáticamente en tu carpeta de usuario y se abrirá

[IMAGEN: Captura de pantalla del botón 'Exportar a Excel (Un Clic)' en la barra de herramientas]

Nota: El botón solo estará habilitado cuando tengas una capa vectorial activa.

Herramientas Completas (Diálogo Principal)

Haz clic en el botón "YF Tools Plus" en la barra de herramientas
Se abrirá un diálogo con 4 pestañas:

[IMAGEN: Captura de pantalla del diálogo principal del plugin con las pestañas]

Pestaña 1: Excel a CSV

Selecciona un archivo Excel (.xlsx o .xls)
Especifica dónde guardar el archivo CSV
Haz clic en "Convertir Excel a CSV"

[IMAGEN: Captura de pantalla de la pestaña 'Excel a CSV']

Pestaña 2: Crear Polígono

Selecciona un archivo CSV con coordenadas
Configura los campos de coordenadas X e Y (por defecto: ESTE, NORTE)
Especifica el sistema de coordenadas (por defecto: EPSG:32719)
Personaliza el estilo del polígono y las etiquetas
Haz clic en "Crear Polígono"

[IMAGEN: Captura de pantalla de la pestaña 'Crear Polígono']

Pestaña 3: Segmentador

Selecciona una capa de polígono existente del menú desplegable
Usa el botón "Actualizar" si acabas de crear una nueva capa
Haz clic en "Segmentar Polígono"
Se crearán dos nuevas capas:

Segmentos: Líneas con longitud y azimut
Vértices: Puntos con coordenadas, ángulos internos y externos

[IMAGEN: Captura de pantalla de la pestaña 'Segmentador' y las capas resultantes]

Pestaña 4: Exportar a Excel

Selecciona la capa vectorial que deseas exportar
Opcionalmente, especifica una ubicación personalizada para el archivo
Haz clic en "Exportar a Excel"
Elige si deseas abrir el archivo automáticamente

[IMAGEN: Captura de pantalla de la pestaña 'Exportar a Excel']

Guardar Configuración

Configura tus preferencias en el diálogo
Haz clic en "Guardar Configuración" en la parte inferior
La próxima vez que abras el plugin, se cargarán estos valores automáticamente

[IMAGEN: Captura de pantalla del botón 'Guardar Configuración']

🔧 Configuración
El plugin guarda automáticamente:

Últimas rutas de archivos utilizadas
Campos de coordenadas preferidos
Sistema de coordenadas predeterminado
Estilos de polígonos y etiquetas

La configuración se almacena en: YF_Tools_Plus/config.json
📊 Datos de Salida
Capa de Polígonos

ID: Identificador del polígono
AREA: Área en hectáreas
PERIMETRO: Perímetro en metros

Capa de Segmentos

ID: Identificador del segmento
longitud: Longitud en metros
azimut: Azimut respecto al norte (0-360°)

Capa de Vértices

ID: Identificador del vértice
LADO: Descripción del segmento (V-n a V-m)
Este: Coordenada X
Norte: Coordenada Y
Distancia: Longitud del segmento que inicia en este vértice
Azimut: Azimut del segmento que inicia en este vértice
ang_int: Ángulo interno en este vértice
ang_extr: Ángulo externo en este vértice

⚙️ Requisitos

QGIS 3.30 o superior
Dependencias:

PyQt5 (incluida con QGIS)
pandas (para conversión Excel a CSV)

**Instalación de pandas:**

Si `pandas` no está disponible en tu entorno QGIS, puedes instalarlo usando el OSGeo4W Shell (en Windows) o el terminal (Linux/macOS) con pip:

```bash
pip install pandas
```

[IMAGEN: Captura de pantalla de la instalación de pandas en el terminal/OSGeo4W Shell]

🐛 Solución de Problemas
El botón de exportación rápida está deshabilitado

Asegúrate de tener una capa vectorial seleccionada en el panel de capas

Error al convertir Excel

Verifica que el archivo Excel existe y no está corrupto
Asegúrate de tener permisos de lectura

Error al crear polígono

Verifica que el CSV contiene las columnas especificadas
Asegúrate de tener al menos 3 puntos válidos
Verifica que las coordenadas son numéricas

Error al segmentar

Asegúrate de que la capa es de tipo polígono
Verifica que el polígono tiene una geometría válida
Usa el botón "Actualizar" si la capa no aparece en la lista

📝 Notas Adicionales

Los archivos Excel exportados se guardan por defecto en la carpeta de usuario
La segmentación comienza desde el vértice más al norte del polígono
Los azimuts se calculan respecto al norte verdadero
Los ángulos internos y externos se calculan automáticamente en cada vértice

👤 Autor
Yuri Caller

Email: yuricaller@gmail.com
GitHub: @yurifabian

📄 Licencia
Este programa es software libre; puedes redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública General GNU versión 2 o posterior. Consulta el archivo `LICENSE` para más detalles.

🤝 Contribuciones
¿Encontraste un bug o tienes una sugerencia?

Reporta problemas en: GitHub Issues
Contribuye con pull requests

📚 Historial de Versiones
v2.0 (2025-04-21)

Fusión de YF_Tools y Export to Excel
Interfaz unificada con pestañas
Exportación rápida a Excel con un clic
Cálculo de ángulos internos y externos en segmentador
Mejoras en la gestión de capas
Guardado de configuración persistente

¿Te gusta este plugin? ⭐ Dale una estrella en GitHub y compártelo con tus colegas!
