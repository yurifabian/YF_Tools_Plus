# -*- coding: utf-8 -*-
"""
/***************************************************************************
 YF_Tools_Plus
                                 A QGIS plugin
 Plugin unificado que combina las funcionalidades de YF_Tools y Export to Excel (Un Clic)
                             -------------------
        begin                : 2025-04-21
        copyright            : (C) 2025 by Yuri Caller
        email                : yuricaller@gmail.com
 ****************************************************************************/
"""

import os.path
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar
from qgis.core import QgsApplication, QgsMessageLog, Qgis, QgsVectorLayer

# Inicializar la traducción de QGIS
class YF_Tools_Plus(QObject):

    def __init__(self, iface):
        super(YF_Tools_Plus, self).__init__()
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.toolbar = self.iface.addToolBar("YF Tools Plus")
        self.toolbar.setObjectName("YF_Tools_PlusToolbar")
        
        # Importar la clase del diálogo - NOMBRE CORRECTO CON GUIÓN BAJO
        from .yf_tools_plus_dialog import YF_Tools_PlusDialog
        self.dialog = YF_Tools_PlusDialog(self.iface)
        
        # Importar el exportador de Excel para la acción rápida
        from .modules.excel_exporter import ExcelExporter
        self.excel_exporter = ExcelExporter()

        # Inicializar acciones
        self.actions = []
        self.menu = self.tr(u"&YF Tools Plus")

        # Cargar traducciones
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'YF_Tools_Plus_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QgsApplication.installTranslator(self.translator)

    def tr(self, message):
        """Obtiene la cadena traducida de QGIS."""
        return QCoreApplication.translate('YF_Tools_Plus', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        parent=None,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        enabled_by_default=True,
        checkable=False):
        """Añade una acción a la barra de herramientas y al menú."""

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_by_default)
        action.setCheckable(checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Crea los elementos de la interfaz de usuario."""
        
        # Acción única para abrir el diálogo principal
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action_main_dialog = self.add_action(
            icon_path,
            text=self.tr(u'YF Tools Plus'),
            callback=self.run,
            parent=self.iface.mainWindow(),
            status_tip=self.tr(u'Herramientas para Excel, Polígonos y Segmentación'),
            add_to_toolbar=True)

    def unload(self):
        """Elimina los elementos de la interfaz de usuario."""
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.iface.removePluginMenu(self.tr(u'&YF Tools Plus'), action)
            
        del self.toolbar

    def run(self):
        """Muestra el diálogo principal del plugin."""
        self.dialog.show()