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

    def refresh_layer_comboboxes(self):
        """Fuerza la actualización de los QgsMapLayerComboBox."""
        try:
            self.mLayerComboBox_polygon.setLayer(None)
            self.mLayerComboBox_polygon.setCurrentIndex(0)
            self.mLayerComboBox_export.setLayer(None)
            self.mLayerComboBox_export.setCurrentIndex(0)
            QgsMessageLog.logMessage(
                self.tr("Listas de capas actualizadas."), 
                "YF Tools Plus", 
                Qgis.Info
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
                    self.tr("Advertencia"), 
                    self.tr("Debe seleccionar un archivo de entrada y uno de salida.")
                )
                return
            
            QgsMessageLog.logMessage(
                self.tr("Iniciando conversión de Excel a CSV..."), 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            self.excel_to_csv.convert(input_file, output_file)
            QMessageBox.information(
                self, 
                self.tr("Éxito"), 
                self.tr(f"Archivo convertido exitosamente a:\n{output_file}")
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Error al convertir archivo:\n{str(e)}")
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
            x_field = self.lineEdit_x_field.text()
            y_field = self.lineEdit_y_field.text()
            crs = self.mCrsSelector_polygon.crs()
            
            if not csv_file or not x_field or not y_field:
                QMessageBox.warning(
                    self, 
                    self.tr("Advertencia"), 
                    self.tr("Debe seleccionar un archivo CSV y especificar los campos X e Y.")
                )
                return
            
            QgsMessageLog.logMessage(
                self.tr("Iniciando creación de polígono..."), 
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
            
            self.polygon_creator.create_polygon(
                csv_file, 
                x_field, 
                y_field, 
                crs.authid(), 
                style_params
            )
            
            QMessageBox.information(
                self, 
                self.tr("Éxito"), 
                self.tr("Polígono creado exitosamente.")
            )
            
            # Actualizar lista de capas
            self.refresh_layer_comboboxes()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Error al crear polígono:\n{str(e)}")
            )
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
                    self.tr("Advertencia"), 
                    self.tr("Debe seleccionar una capa de polígono válida.")
                )
                return
            
            QgsMessageLog.logMessage(
                self.tr(f"Iniciando segmentación de capa: {layer.name()}..."), 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            result = self.segmentator.segment_polygon(layer)
            
            if result:
                QMessageBox.information(
                    self, 
                    self.tr("Éxito"), 
                    self.tr("Polígono segmentado exitosamente.\n\nCapas 'Segmentos' y 'Vertices' añadidas al proyecto.")
                )
            else:
                QMessageBox.warning(
                    self, 
                    self.tr("Advertencia"), 
                    self.tr("La segmentación no se completó correctamente.")
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Error al segmentar polígono:\n{str(e)}")
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
                    self.tr("Advertencia"), 
                    self.tr("Debe seleccionar una capa vectorial válida para exportar.")
                )
                return
            
            # Si no hay ruta de salida, usar por defecto
            if not output_path:
                layer_name = layer.name().replace(" ", "_")
                output_dir = os.path.expanduser("~")
                output_path = os.path.join(output_dir, f"{layer_name}_atributos.xlsx")
            
            QgsMessageLog.logMessage(
                self.tr(f"Iniciando exportación de capa: {layer.name()} a Excel..."), 
                "YF Tools Plus", 
                Qgis.Info
            )
            
            self.excel_exporter.export_to_excel(layer, output_path, open_file)
            
            if open_file:
                msg = self.tr(f"Exportación completada y archivo abierto:\n{output_path}")
            else:
                msg = self.tr(f"Exportación completada:\n{output_path}")
            
            QMessageBox.information(self, self.tr("Éxito"), msg)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Error al exportar a Excel:\n{str(e)}")
            )
            QgsMessageLog.logMessage(
                f"Error en ExcelExporter: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )

    def save_config(self):
        """Guarda la configuración actual de los widgets en un archivo JSON."""
        config = {
            "excel_input_path": self.mFileWidget_excel_input.filePath(),
            "csv_output_path": self.mFileWidget_csv_output.filePath(),
            "csv_polygon_path": self.mFileWidget_csv_polygon.filePath(),
            "x_field": self.lineEdit_x_field.text(),
            "y_field": self.lineEdit_y_field.text(),
            "crs_authid": self.mCrsSelector_polygon.crs().authid(),
            "excel_output_path": self.mFileWidget_excel_output.filePath(),
            "auto_open": self.checkBox_auto_open.isChecked(),
            "current_tab": self.tabWidget.currentIndex()
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            QgsMessageLog.logMessage(
                self.tr("Configuración guardada exitosamente."), 
                "YF Tools Plus", 
                Qgis.Success
            )
            QMessageBox.information(
                self, 
                self.tr("Éxito"), 
                self.tr("Configuración guardada.")
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al guardar configuración: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Critical
            )
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Error al guardar configuración:\n{str(e)}")
            )

    def load_config(self):
        """Carga la configuración guardada desde un archivo JSON."""
        if not os.path.exists(self.config_path):
            # Establecer valores por defecto
            self.lineEdit_x_field.setText("ESTE")
            self.lineEdit_y_field.setText("NORTE")
            self.checkBox_auto_open.setChecked(True)
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.mFileWidget_excel_input.setFilePath(config.get("excel_input_path", ""))
            self.mFileWidget_csv_output.setFilePath(config.get("csv_output_path", ""))
            self.mFileWidget_csv_polygon.setFilePath(config.get("csv_polygon_path", ""))
            self.lineEdit_x_field.setText(config.get("x_field", "ESTE"))
            self.lineEdit_y_field.setText(config.get("y_field", "NORTE"))
            
            crs_authid = config.get("crs_authid")
            if crs_authid:
                crs = QgsCoordinateReferenceSystem(crs_authid)
                if crs.isValid():
                    self.mCrsSelector_polygon.setCrs(crs)
            
            self.mFileWidget_excel_output.setFilePath(config.get("excel_output_path", ""))
            self.checkBox_auto_open.setChecked(config.get("auto_open", True))
            self.tabWidget.setCurrentIndex(config.get("current_tab", 0))
            
            QgsMessageLog.logMessage(
                self.tr("Configuración cargada exitosamente."), 
                "YF Tools Plus", 
                Qgis.Info
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al cargar configuración: {str(e)}", 
                "YF Tools Plus", 
                Qgis.Warning
            )
            # Establecer valores por defecto en caso de error
            self.lineEdit_x_field.setText("ESTE")
            self.lineEdit_y_field.setText("NORTE")
            self.checkBox_auto_open.setChecked(True)