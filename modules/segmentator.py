# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Segmentator
                                 A QGIS plugin
 Herramientas para generar capas a partir de archivos Excel
                             -------------------
        begin                : 2025-04-21
        copyright            : (C) 2025 by Yuri Caller
        email                : yuricaller@gmail.com
 ****************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ****************************************************************************/
"""

from math import atan2, degrees
from qgis.core import (
    QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject,
    QgsSimpleLineSymbolLayer, QgsSingleSymbolRenderer, QgsFillSymbol,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling,
    QgsWkbTypes, QgsMessageLog, Qgis
)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor, QFont
import traceback


class Segmentator:
    """Clase para segmentar polígonos en líneas y vértices"""
    
    def __init__(self):
        """Constructor."""
        pass
    
    def calcular_angulo_norte(self, punto_inicio, punto_fin):
        """
        Calcula el ángulo respecto al norte (Azimut)
        
        :param punto_inicio: Punto de inicio
        :type punto_inicio: QgsPointXY
        
        :param punto_fin: Punto de fin
        :type punto_fin: QgsPointXY
        
        :returns: Ángulo respecto al norte en grados [0, 360)
        :rtype: float
        """
        dx = punto_fin.x() - punto_inicio.x()
        dy = punto_fin.y() - punto_inicio.y()
        # Evitar atan2(0, 0)
        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return 0.0
        angulo = degrees(atan2(dx, dy))  # Ángulo respecto al eje Y positivo (Norte)
        if angulo < 0:
            angulo += 360
        return angulo
    
    def segment_polygon(self, capa_poligonos):
        """
        Segmenta un polígono en líneas y vértices, calculando ángulos internos/externos.
        Cada polígono tiene su propia numeración independiente de vértices.
        
        :param capa_poligonos: Capa de polígonos a segmentar
        :type capa_poligonos: QgsVectorLayer
        
        :returns: True si la segmentación fue exitosa, False en caso contrario
        :rtype: bool
        """
        try:
            if not capa_poligonos or capa_poligonos.geometryType() != QgsWkbTypes.PolygonGeometry:
                QgsMessageLog.logMessage("La capa seleccionada no es válida o no es de tipo polígono.", "YF Tools", Qgis.Critical)
                return False
            
            # Crear una nueva capa para las polilíneas (segmentos)
            uri_lineas = f"LineString?crs={capa_poligonos.crs().toWkt()}"
            capa_polilineas = QgsVectorLayer(uri_lineas, "Segmentos", "memory")
            prov_lineas = capa_polilineas.dataProvider()
            prov_lineas.addAttributes([
                QgsField("ID_Global", QVariant.Int),      # ID único global
                QgsField("ID_Poligono", QVariant.Int),    # ID del polígono al que pertenece
                QgsField("ID_Segmento", QVariant.Int),    # ID del segmento dentro del polígono
                QgsField("longitud", QVariant.Double),
                QgsField("azimut", QVariant.Double)
            ])
            capa_polilineas.updateFields()
            
            # Crear una nueva capa para los puntos (vértices)
            uri_puntos = f"Point?crs={capa_poligonos.crs().toWkt()}"
            capa_puntos = QgsVectorLayer(uri_puntos, "Vertices", "memory")
            prov_puntos = capa_puntos.dataProvider()
            prov_puntos.addAttributes([
                QgsField("ID_Global", QVariant.Int),      # ID único global
                QgsField("ID_Poligono", QVariant.Int),    # ID del polígono al que pertenece
                QgsField("ID_Vertice", QVariant.Int),     # ID del vértice dentro del polígono
                QgsField("LADO", QVariant.String),        # Descripción del segmento
                QgsField("Este", QVariant.Double),
                QgsField("Norte", QVariant.Double),
                QgsField("Distancia", QVariant.Double),
                QgsField("Azimut", QVariant.Double),
                QgsField("ang_int", QVariant.Double),
                QgsField("ang_extr", QVariant.Double)
            ])
            capa_puntos.updateFields()
            
            # Contador global para IDs únicos
            id_global_counter = 1
            
            # Contador de polígonos procesados
            id_poligono = 1
            
            # Procesar cada polígono en la capa de entrada
            for feature in capa_poligonos.getFeatures():
                geom = feature.geometry()
                if not geom or geom.isEmpty():
                    continue

                if geom.isMultipart():
                    # Tomar solo la primera parte si es multiparte
                    poligonos = geom.asMultiPolygon()
                    if not poligonos: 
                        continue
                    anillos = poligonos[0]
                else:
                    poligono = geom.asPolygon()
                    if not poligono: 
                        continue
                    anillos = poligono

                if not anillos: 
                    continue
                anillo_exterior = anillos[0]

                # Convertir anillo a QgsPointXY
                vertices_xy = [QgsPointXY(punto) for punto in anillo_exterior]
                
                # Validar y limpiar anillo
                if len(vertices_xy) < 3:
                    QgsMessageLog.logMessage(f"Polígono con ID {feature.id()} tiene menos de 3 vértices. Omitiendo.", "YF Tools", Qgis.Warning)
                    continue
                    
                # Eliminar punto duplicado al final si existe (cierra el anillo)
                if vertices_xy[0].compare(vertices_xy[-1], 1e-9):
                    vertices_xy.pop()
                    
                if len(vertices_xy) < 3:
                    QgsMessageLog.logMessage(f"Polígono con ID {feature.id()} tiene menos de 3 vértices únicos. Omitiendo.", "YF Tools", Qgis.Warning)
                    continue

                # Encontrar el vértice más al norte (mayor Y, desempatar con menor X)
                vertice_norte = max(vertices_xy, key=lambda p: (p.y(), -p.x()))
                indice_norte = vertices_xy.index(vertice_norte)
                
                # Reorganizar los vértices para que comiencen desde el norte
                vertices_ordenados = vertices_xy[indice_norte:] + vertices_xy[:indice_norte]
                num_vertices = len(vertices_ordenados)

                # Procesar cada vértice del polígono actual
                for i in range(num_vertices):
                    # Índices para vértice actual, siguiente y anterior (manejo cíclico)
                    idx_curr = i
                    idx_next = (i + 1) % num_vertices
                    idx_prev = (i - 1 + num_vertices) % num_vertices
                    
                    punto_inicio = vertices_ordenados[idx_curr]
                    punto_fin = vertices_ordenados[idx_next]
                    punto_prev = vertices_ordenados[idx_prev]

                    # Crear el segmento (línea)
                    segmento_geom = QgsGeometry.fromPolylineXY([punto_inicio, punto_fin])
                    if not segmento_geom or segmento_geom.isEmpty(): 
                        continue
                    
                    longitud = round(segmento_geom.length(), 4)
                    
                    # Omitir si la longitud es prácticamente cero
                    if longitud < 1e-6: 
                        QgsMessageLog.logMessage(f"Segmento de longitud cero detectado en polígono {id_poligono}, vértice {i+1}. Omitiendo.", "YF Tools", Qgis.Warning)
                        continue
                    
                    # Calcular azimut del segmento actual (inicio -> fin)
                    azimut = self.calcular_angulo_norte(punto_inicio, punto_fin)
                    azimut = round(azimut, 1)
                    
                    # --- Calcular Ángulos Interno y Externo ---
                    azimut_prev_curr = self.calcular_angulo_norte(punto_prev, punto_inicio)
                    azimut_curr_next = azimut
                    internal_angle = (azimut_prev_curr - azimut_curr_next + 180) % 360
                    external_angle = 360.0 - internal_angle
                    if abs(external_angle - 360) < 1e-6: 
                        external_angle = 0.0
                    elif external_angle < 0: 
                        external_angle += 360
                    internal_angle = round(internal_angle, 2)
                    external_angle = round(external_angle, 2)
                    # --- Fin Cálculo Ángulos ---

                    # ID del vértice dentro del polígono actual (1-based)
                    id_vertice_local = i + 1
                    id_vertice_siguiente_local = ((i + 1) % num_vertices) + 1

                    # Crear característica para la capa de polilíneas (segmentos)
                    linea_feature = QgsFeature(capa_polilineas.fields())
                    linea_feature.setGeometry(segmento_geom)
                    linea_feature.setAttributes([
                        id_global_counter,           # ID_Global
                        id_poligono,                 # ID_Poligono
                        id_vertice_local,            # ID_Segmento (corresponde al vértice de inicio)
                        longitud,                    # longitud
                        azimut                       # azimut
                    ])
                    prov_lineas.addFeature(linea_feature)
                    
                    # Crear característica para la capa de puntos (vértices)
                    punto_feature = QgsFeature(capa_puntos.fields())
                    punto_feature.setGeometry(QgsGeometry.fromPointXY(punto_inicio))
                    
                    # Generar string LADO usando solo los IDs de vértices (sin prefijo de polígono)
                    lado_str = f"V{id_vertice_local} a V{id_vertice_siguiente_local}"
                    
                    punto_feature.setAttributes([
                        id_global_counter,                  # ID_Global
                        id_poligono,                        # ID_Poligono
                        id_vertice_local,                   # ID_Vertice
                        lado_str,                           # LADO
                        round(punto_inicio.x(), 6),         # Este
                        round(punto_inicio.y(), 6),         # Norte
                        longitud,                           # Distancia
                        azimut,                             # Azimut
                        internal_angle,                     # ang_int
                        external_angle                      # ang_extr
                    ])
                    prov_puntos.addFeature(punto_feature)
                    
                    # Incrementar el contador global
                    id_global_counter += 1
                
                # Incrementar el ID del polígono para el siguiente
                id_poligono += 1
            
            # Actualizar extensión de las capas
            capa_polilineas.updateExtents()
            capa_puntos.updateExtents()

            # Configurar etiquetas para la capa de polilíneas
            etiquetas_polilineas = QgsPalLayerSettings()
            etiquetas_polilineas.fieldName = "concat(round(\"longitud\", 2) || ' m' || '\\n' || round(\"azimut\", 1) || '°')"
            etiquetas_polilineas.isExpression = True
            formato_texto_polilineas = QgsTextFormat()
            formato_texto_polilineas.setFont(QFont("Arial", 7))
            formato_texto_polilineas.setColor(QColor(0, 0, 0))
            formato_texto_polilineas.setSize(7)
            buffer_polilineas = QgsTextBufferSettings()
            buffer_polilineas.setEnabled(True)
            buffer_polilineas.setSize(0.5)
            buffer_polilineas.setColor(QColor(255, 255, 255))
            formato_texto_polilineas.setBuffer(buffer_polilineas)
            etiquetas_polilineas.setFormat(formato_texto_polilineas)
            etiquetas_polilineas.placement = QgsPalLayerSettings.Line
            etiquetas_polilineas.placementFlags = QgsPalLayerSettings.OnLine | QgsPalLayerSettings.AboveLine
            capa_polilineas.setLabeling(QgsVectorLayerSimpleLabeling(etiquetas_polilineas))
            capa_polilineas.setLabelsEnabled(True)
            
            # Configurar etiquetas para la capa de puntos - muestra solo V{ID_Vertice}
            etiquetas_puntos = QgsPalLayerSettings()
            etiquetas_puntos.fieldName = "'V' || \"ID_Vertice\""
            etiquetas_puntos.isExpression = True
            formato_texto_puntos = QgsTextFormat()
            formato_texto_puntos.setFont(QFont("Arial", 9))
            formato_texto_puntos.setColor(QColor(0, 0, 255))
            formato_texto_puntos.setSize(9)
            buffer_puntos = QgsTextBufferSettings()
            buffer_puntos.setEnabled(True)
            buffer_puntos.setSize(0.5)
            buffer_puntos.setColor(QColor(255, 255, 255))
            formato_texto_puntos.setBuffer(buffer_puntos)
            etiquetas_puntos.setFormat(formato_texto_puntos)
            etiquetas_puntos.placement = QgsPalLayerSettings.AroundPoint
            etiquetas_puntos.quadOffset = QgsPalLayerSettings.QuadrantAboveRight
            etiquetas_puntos.dist = 1.0
            capa_puntos.setLabeling(QgsVectorLayerSimpleLabeling(etiquetas_puntos))
            capa_puntos.setLabelsEnabled(True)
            
            # Agregar las capas al proyecto QGIS
            QgsProject.instance().addMapLayer(capa_polilineas)
            QgsProject.instance().addMapLayer(capa_puntos)
            
            QgsMessageLog.logMessage(
                f"Segmentación completada. Procesados {id_poligono - 1} polígono(s).", 
                "YF Tools", 
                Qgis.Success
            )
            return True
            
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error al segmentar polígono: {str(e)}\n{traceback.format_exc()}", 
                "YF Tools", 
                Qgis.Critical
            )
            raise Exception(f"Error al segmentar polígono: {str(e)}")