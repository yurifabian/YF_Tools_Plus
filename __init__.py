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

def classFactory(iface):
    """Load YF_Tools_Plus class from file yf_tools_plus.py"""
    from .yf_tools_plus import YF_Tools_Plus
    return YF_Tools_Plus(iface)
