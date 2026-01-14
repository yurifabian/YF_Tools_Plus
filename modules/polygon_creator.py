# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PolygonCreator
                                 A QGIS plugin
 Herramientas para generar capas a partir de archivos Excel
                             -------------------
        begin                : 2025-04-21
        copyright            : (C) 2025 by Yuri Caller
        email                : yuricaller@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.core import (
    QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject,
    QgsSimpleLineSymbolLayer, QgsSingleSymbolRenderer, QgsFillSymbol,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling
)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor, QFont
from qgis.core import QgsMessageLog, Qgis

class PolygonCreator:
    """Clase para crear polígonos a partir de archivos CSV"""
    
    def __init__(self):
        """Constructor."""
        pass
        
    def create_polygon(self, csv_path, field_x, field_y, crs, style_params=None):
        """
        Crea un polígono a partir de coordenadas en un archivo CSV
        
        :param csv_path: Ruta al archivo CSV
        :type csv_path: str
        
        :param field_x: Nombre del campo que contiene la coordenada X
        :type field_x: str
        
        :param field_y: Nombre del campo que contiene la coordenada Y
        :type field_y: str
        
        :param crs: Sistema de referencia de coordenadas (ej. QgsCrs)
        :type crs: QgsCrs
        
        :param style_params: Parámetros de estilo para el polígono
        :type style_params: dict
        
        :returns: Capa de polígono creada
        :rtype: QgsVectorLayer or None
        """
        try:
            # Verificar que el archivo CSV existe
            if not os.path.exists(csv_path):
                QgsMessageLog.logMessage(f"El archivo CSV no existe: {csv_path}", "YF Tools Plus", Qgis.Critical)
                return None
            
            # Configurar parámetros de estilo predeterminados si no se proporcionan
            if style_params is None:
                style_params = {
                    'polygon_color': '#ffffff',
                    'border_color': '#ff340b',
                    'border_width': '0.26',
                    'label_font': 'Arial',
                    'label_size': '9',
                    'label_color': '#ff340b'
                }
            
            # 1. Cargar la capa de puntos desde el archivo CSV
            # Nota: El CRS debe ser pasado como WKT o AuthID para la URI, pero el diálogo pasa un objeto QgsCrs.
            # Usaremos el objeto QgsCrs para la capa de memoria.
            uri = f"file:///{csv_path}?encoding=UTF-8&delimiter=,&xField={field_x}&yField={field_y}&crs={crs.authid()}"
            points_layer = QgsVectorLayer(uri, "points_layer", "delimitedtext")
            
            # Verificar si la capa se cargó correctamente
            if not points_layer.isValid():
                QgsMessageLog.logMessage("Error al cargar la capa de puntos. Verifica la ruta y el formato del archivo.", "YF Tools Plus", Qgis.Critical)
                return None
            
            # 2. Crear una capa de polígonos
            polygon_layer = QgsVectorLayer(f"Polygon?crs={crs.toWkt()}", "Polígono", "memory")
            provider = polygon_layer.dataProvider()
            provider.addAttributes([
                QgsField("ID", QVariant.Int),
                QgsField("AREA", QVariant.Double),
                QgsField("PERIMETRO", QVariant.Double)
            ])
            polygon_layer.updateFields()
            
            # 3. Crear un polígono a partir de las coordenadas
            points = []
            for feature in points_layer.getFeatures():
                # Asumiendo que los campos son numéricos y existen
                try:
                    east = feature[field_x]
                    north = feature[field_y]
                    points.append(QgsPointXY(east, north))
                except Exception as e:
                    QgsMessageLog.logMessage(f"Error al leer coordenadas de la fila {feature.id()}: {str(e)}", "YF Tools Plus", Qgis.Warning)
                    continue
            
            # Verificar que hay suficientes puntos para crear un polígono
            if len(points) < 3:
                QgsMessageLog.logMessage("Se necesitan al menos 3 puntos para crear un polígono.", "YF Tools Plus", Qgis.Critical)
                return None
            
            # Crear la geometría del polígono
            polygon = QgsGeometry.fromPolygonXY([points])
            feature = QgsFeature()
            feature.setGeometry(polygon)
            
            # 4. Calcular área y perímetro
            # QGIS usa el CRS de la capa para los cálculos.
            # Se asume que el CRS es proyectado (UTM) para que los cálculos sean en metros/hectáreas.
            area = polygon.area() / 10000  # Convertir a hectáreas
            perimeter = polygon.length()  # Perímetro en metros
            
            # 5. Añadir atributos
            feature.setAttributes([1, round(area, 4), round(perimeter, 2)])
            provider.addFeature(feature)
            polygon_layer.updateExtents()
            
            # 6. Añadir la capa al proyecto
            QgsProject.instance().addMapLayer(polygon_layer)
            
            # 7. Aplicar la simbología
            symbol = QgsFillSymbol.createSimple({
                'color': style_params.get('polygon_color', '#ffffff'),
                'color_border': style_params.get('border_color', '#ff340b'),
                'width_border': style_params.get('border_width', '0.26')
            })
            polygon_layer.renderer().setSymbol(symbol)
            polygon_layer.triggerRepaint()
            
            # 8. Aplicar etiquetas
            label_settings = QgsPalLayerSettings()
            label_settings.fieldName = "'PARCELA GEOREFERENCIADA' || '\n' || 'AREA : ' || Round(\"AREA\", 4) || ' Ha.' || '\n' || 'PERIMETRO : ' || Round(\"PERIMETRO\", 2) || ' m.'"
            label_settings.isExpression = True
            
            text_format = QgsTextFormat()
            text_format.setColor(QColor(style_params.get('label_color', '#ff340b')))
            text_format.setSize(float(style_params.get('label_size', '9')))
            text_format.setFont(QFont(style_params.get('label_font', 'Arial'), int(style_params.get('label_size', '9')), QFont.Bold))
            
            buffer_settings = QgsTextBufferSettings()
            buffer_settings.setEnabled(True)
            buffer_settings.setSize(1.0)
            buffer_settings.setColor(QColor("white"))
            text_format.setBuffer(buffer_settings)
            
            label_settings.setFormat(text_format)
            label_settings.placement = QgsPalLayerSettings.Placement.OverPoint
            label_settings.centroidWhole = True
            
            polygon_layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
            polygon_layer.setLabelsEnabled(True)
            polygon_layer.triggerRepaint()
            
            return polygon_layer
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error al crear polígono: {str(e)}", "YF Tools Plus", Qgis.Critical)
            return None
