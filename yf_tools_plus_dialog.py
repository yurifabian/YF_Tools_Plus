# -*- coding: utf-8 -*-
"""
/***************************************************************************
 YF_Tools_PlusDialog
                                 A QGIS plugin
 Diálogo principal del plugin.
                             -------------------
        begin                : 2025-04-21
        copyright            : (C) 2025 by Yuri Caller
        email                : yuricaller@gmail.com
 ****************************************************************************/
"""

import os
import json
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QSize
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.PyQt import uic
from qgis.core import (
    QgsMessageLog, Qgis, QgsProject, QgsMapLayerProxyModel, 
    QgsVectorLayer, QgsCoordinateReferenceSystem
)
from qgis.utils import iface

# Importar las clases de módulos
from .modules.excel_to_csv import ExcelToCsv
from .modules.polygon_creator import PolygonCreator
from .modules.segmentator import Segmentator
from .modules.excel_exporter import ExcelExporter

# Cargar el archivo .ui
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'yf_tools_plus_dialog_base.ui'))

class YF_Tools_PlusDialog(QDialog, FORM_CLASS):
    """Diálogo principal del plugin YF Tools Plus."""

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(YF_Tools_PlusDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(self.plugin_dir, 'config.json')
        
        # Inicializar clases de módulos
        self.excel_to_csv = ExcelToCsv()
        self.polygon_creator = PolygonCreator()
        self.segmentator = Segmentator()
        self.excel_exporter = ExcelExporter()
        
        # Conectar señales
        self.pushButton_convert_csv.clicked.connect(self.run_excel_to_csv)
        self.pushButton_create_polygon.clicked.connect(self.run_create_polygon)
        self.pushButton_segment_polygon.clicked.connect(self.run_segmentator)
        self.pushButton_export_excel.clicked.connect(self.run_export_excel)
        self.pushButton_save_config.clicked.connect(self.save_config)
        self.pushButton_refresh_layers.clicked.connect(self.refresh_layer_comboboxes)
        
        # Conectar cambio de archivo CSV para actualizar campos
        self.mFileWidget_csv_polygon.fileChanged.connect(self.update_csv_fields)
        
        # Configuración inicial de widgets
        try:
            # Configurar CRS selector
            self.mCrsSelector_polygon.setCrs(QgsProject.instance().crs())
            
            # Configurar filtros de capas
            self.mLayerComboBox_polygon.setFilters(QgsMapLayerProxyModel.PolygonLayer)
            self.mLayerComboBox_export.setFilters(QgsMapLayerProxyModel.VectorLayer)
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al configurar widgets: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Warning
            )
        
        # Cargar configuración guardada
        self.load_config()

    def tr(self, message):
        """Obtiene la cadena traducida de QGIS."""
        return QCoreApplication.translate('YF_Tools_PlusDialog', message)

    def update_csv_fields(self, filepath):
        """
        Actualiza los ComboBox de campos X e Y cuando se selecciona un archivo CSV
        
        :param filepath: Ruta al archivo CSV seleccionado
        :type filepath: str
        """
        try:
            if not filepath or not os.path.exists(filepath):
                return
            
            QgsMessageLog.logMessage(
                f"Detectando campos en: {filepath}", 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            # Obtener campos del CSV
            fields = self.polygon_creator.get_csv_fields(filepath)
            
            if not fields:
                QgsMessageLog.logMessage(
                    "No se pudieron detectar campos en el CSV", 
                    "YF Tools Plus", 
                    Qgis.Warning
                )
                return
            
            # Guardar el texto actual (si existe)
            current_x = self.comboBox_x_field.currentText()
            current_y = self.comboBox_y_field.currentText()
            
            # Limpiar y llenar los comboboxes
            self.comboBox_x_field.clear()
            self.comboBox_y_field.clear()
            
            self.comboBox_x_field.addItems(fields)
            self.comboBox_y_field.addItems(fields)
            
            # Intentar restaurar valores anteriores o detectar automáticamente
            x_set = False
            y_set = False
            
            # Primero intentar restaurar valores anteriores
            if current_x:
                index = self.comboBox_x_field.findText(current_x)
                if index >= 0:
                    self.comboBox_x_field.setCurrentIndex(index)
                    x_set = True
            
            if current_y:
                index = self.comboBox_y_field.findText(current_y)
                if index >= 0:
                    self.comboBox_y_field.setCurrentIndex(index)
                    y_set = True
            
            # Si no se restauraron, intentar detección automática
            if not x_set:
                for i, field in enumerate(fields):
                    field_upper = field.upper()
                    if any(keyword in field_upper for keyword in ['X', 'ESTE', 'EAST', 'LON', 'EASTING', 'E']):
                        self.comboBox_x_field.setCurrentIndex(i)
                        break
            
            if not y_set:
                for i, field in enumerate(fields):
                    field_upper = field.upper()
                    if any(keyword in field_upper for keyword in ['Y', 'NORTE', 'NORTH', 'LAT', 'NORTHING', 'N']):
                        self.comboBox_y_field.setCurrentIndex(i)
                        break
            
            QgsMessageLog.logMessage(
                f"✓ Campos detectados: {', '.join(fields)}", 
                "YF Tools Plus", 
                Qgis.Success
            )
            
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al actualizar campos: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Warning
            )

    def refresh_layer_comboboxes(self):
        """Fuerza la actualización de los QgsMapLayerComboBox."""
        try:
            self.mLayerComboBox_polygon.setLayer(None)
            self.mLayerComboBox_polygon.setCurrentIndex(0)
            self.mLayerComboBox_export.setLayer(None)
            self.mLayerComboBox_export.setCurrentIndex(0)
            
            self.iface.messageBar().pushMessage(
                "YF Tools Plus",
                "✓ Listas de capas actualizadas",
                level=Qgis.Success,
                duration=2
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al actualizar listas: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Warning
            )

    def run_excel_to_csv(self):
        """Ejecuta la conversión de Excel a CSV."""
        try:
            input_file = self.mFileWidget_excel_input.filePath()
            output_file = self.mFileWidget_csv_output.filePath()
            
            if not input_file or not output_file:
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "Debe seleccionar un archivo de entrada y uno de salida."
                )
                return
            
            QgsMessageLog.logMessage(
                "Iniciando conversión de Excel a CSV...", 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            result = self.excel_to_csv.convert(input_file, output_file)
            
            if result:
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"✓ Archivo convertido exitosamente a:\n{output_file}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se pudo convertir el archivo. Revise el registro de mensajes."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al convertir archivo:\n{str(e)}"
            )
            QgsMessageLog.logMessage(
                f"Error en ExcelToCsv: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )

    def run_create_polygon(self):
        """Ejecuta la creación de polígonos desde CSV."""
        try:
            csv_file = self.mFileWidget_csv_polygon.filePath()
            x_field = self.comboBox_x_field.currentText().strip()
            y_field = self.comboBox_y_field.currentText().strip()
            crs = self.mCrsSelector_polygon.crs()
            
            if not csv_file:
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "Debe seleccionar un archivo CSV."
                )
                return
            
            if not x_field or not y_field:
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "Debe especificar los campos X e Y."
                )
                return
            
            QgsMessageLog.logMessage(
                f"Creando polígono con campos X='{x_field}', Y='{y_field}'", 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            # Crear parámetros de estilo por defecto
            style_params = {
                'polygon_color': '#ffffff',
                'border_color': '#ff340b',
                'border_width': '0.26',
                'label_font': 'Arial',
                'label_size': '9',
                'label_color': '#ff340b'
            }
            
            result = self.polygon_creator.create_polygon(
                csv_file, 
                x_field, 
                y_field, 
                crs.authid(), 
                style_params
            )
            
            if result:
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    "✓ Polígono creado exitosamente"
                )
                self.refresh_layer_comboboxes()
            else:
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "No se pudo crear el polígono.\n\nRevise el Panel de Registro de Mensajes:\nVer → Paneles → Registro de mensajes → YF Tools Plus"
                )
            
        except Exception as e:
            error_msg = f"Error al crear polígono:\n{str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            QgsMessageLog.logMessage(
                f"Error en PolygonCreator: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )

    def run_segmentator(self):
        """Ejecuta la segmentación de polígonos."""
        try:
            layer = self.mLayerComboBox_polygon.currentLayer()
            
            if not layer or not layer.isValid():
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "Debe seleccionar una capa de polígono válida."
                )
                return
            
            QgsMessageLog.logMessage(
                f"Segmentando capa: {layer.name()}", 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            result = self.segmentator.segment_polygon(layer)
            
            if result:
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    "✓ Polígono segmentado exitosamente\n\nCapas creadas:\n• Segmentos\n• Vertices"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "La segmentación no se completó correctamente."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al segmentar polígono:\n{str(e)}"
            )
            QgsMessageLog.logMessage(
                f"Error en Segmentator: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )

    def run_export_excel(self):
        """Ejecuta la exportación a Excel desde el diálogo."""
        try:
            layer = self.mLayerComboBox_export.currentLayer()
            output_path = self.mFileWidget_excel_output.filePath()
            open_file = self.checkBox_auto_open.isChecked()
            
            if not layer or not layer.isValid():
                QMessageBox.warning(
                    self, 
                    "Advertencia", 
                    "Debe seleccionar una capa vectorial válida para exportar."
                )
                return
            
            if not output_path:
                layer_name = layer.name().replace(" ", "_")
                output_dir = os.path.expanduser("~")
                output_path = os.path.join(output_dir, f"{layer_name}_atributos.xlsx")
            
            QgsMessageLog.logMessage(
                f"Exportando capa: {layer.name()}", 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            self.excel_exporter.export_to_excel(layer, output_path, open_file)
            
            msg = f"✓ Exportación completada:\n{output_path}"
            if open_file:
                msg += "\n\n(Archivo abierto automáticamente)"
            
            QMessageBox.information(self, "Éxito", msg)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al exportar a Excel:\n{str(e)}"
            )
            QgsMessageLog.logMessage(
                f"Error en ExcelExporter: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )

    def save_config(self):
        """Guarda la configuración actual."""
        config = {
            "excel_input_path": self.mFileWidget_excel_input.filePath(),
            "csv_output_path": self.mFileWidget_csv_output.filePath(),
            "csv_polygon_path": self.mFileWidget_csv_polygon.filePath(),
            "x_field": self.comboBox_x_field.currentText(),
            "y_field": self.comboBox_y_field.currentText(),
            "crs_authid": self.mCrsSelector_polygon.crs().authid(),
            "excel_output_path": self.mFileWidget_excel_output.filePath(),
            "auto_open": self.checkBox_auto_open.isChecked(),
            "current_tab": self.tabWidget.currentIndex()
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.iface.messageBar().pushMessage(
                "YF Tools Plus",
                "✓ Configuración guardada",
                level=Qgis.Success,
                duration=2
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al guardar configuración: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )

    def load_config(self):
        """Carga la configuración guardada."""
        if not os.path.exists(self.config_path):
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.mFileWidget_excel_input.setFilePath(config.get("excel_input_path", ""))
            self.mFileWidget_csv_output.setFilePath(config.get("csv_output_path", ""))
            
            csv_path = config.get("csv_polygon_path", "")
            if csv_path:
                self.mFileWidget_csv_polygon.setFilePath(csv_path)
                if os.path.exists(csv_path):
                    self.update_csv_fields(csv_path)
            
            # Establecer valores de campos
            x_field = config.get("x_field", "ESTE")
            y_field = config.get("y_field", "NORTE")
            
            self.comboBox_x_field.setEditText(x_field)
            self.comboBox_y_field.setEditText(y_field)
            
            crs_authid = config.get("crs_authid")
            if crs_authid:
                crs = QgsCoordinateReferenceSystem(crs_authid)
                if crs.isValid():
                    self.mCrsSelector_polygon.setCrs(crs)
            
            self.mFileWidget_excel_output.setFilePath(config.get("excel_output_path", ""))
            self.checkBox_auto_open.setChecked(config.get("auto_open", True))
            self.tabWidget.setCurrentIndex(config.get("current_tab", 0))
            
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al cargar configuración: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Warning
            )