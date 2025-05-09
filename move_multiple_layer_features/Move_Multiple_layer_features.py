# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Move_Multiple_layer_features
                                 A QGIS plugin
 used to move multiple layers features at once.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-05-07
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Bhavani R
        email                : rbhavani@datacollectionindia.co.in
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Move_Multiple_layer_features_dialog import Move_Multiple_layer_featuresDialog
import os.path
from qgis.gui import QgsMapTool
from qgis.core import (
    QgsPointXY, QgsGeometry, QgsProject, QgsCoordinateTransform, QgsVectorLayer
)
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt
from qgis.utils import iface

class Move_Multiple_layer_features:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Move_Multiple_layer_features_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Move_Multiple_layer_features')
        self.first_start = None
        self.move_tool = None
        self.move_action = None
        self.undo_action = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
        return QCoreApplication.translate('Move_Multiple_layer_features', message)

    class MoveSelectedFeaturesTool(QgsMapTool):
        def __init__(self, iface, callback):
            self.iface = iface
            self.canvas = iface.mapCanvas()
            super().__init__(self.canvas)
            self.callback = callback
            self.start_point = None
            self.first_click = True

        #def canvasReleaseEvent(self, event):
#             point = self.toMapCoordinates(event.pos())
#             if self.first_click:
#                 self.start_point = point
#                 self.first_click = False
#                 self.iface.messageBar().pushMessage("Move Tool", "Click destination point", level=0, duration=2)
#             else:
#                 dx = point.x() - self.start_point.x()
#                 dy = point.y() - self.start_point.y()
#                 self.callback(dx, dy)
#                 self.first_click = True
#                 self.iface.messageBar().pushMessage("Move Tool", "Features moved", level=0, duration=2)
				
        def canvasReleaseEvent(self, event):
            point = self.toMapCoordinates(event.pos())

            if self.first_click:
                # First click - check if any features are selected in editable layers
                has_selected = False
                debug_info = []

                layers = QgsProject.instance().layerTreeRoot().findLayers()

                for layer in layers:
                    vl = layer.layer()
                    if isinstance(vl, QgsVectorLayer):
                        editable = vl.isEditable()
                        selected = vl.selectedFeatureCount()
                        debug_info.append(f"{vl.name()} - Editable: {editable}, Selected: {selected}")
                        if editable and selected > 0:
                            has_selected = True

                if not has_selected:
                    self.iface.messageBar().pushMessage(
                        "Move Tool",
                        "No features selected in editable layers",
                        level=2,  # Warning level
                        duration=4
                    )
                    print("\n".join(debug_info))  # Print for debugging
                    # self.deactivate()  # Optional: comment this to allow retry
                    return

                # If we get here, at least one layer has selected features
                self.start_point = point
                self.first_click = False
                self.iface.messageBar().pushMessage(
                    "Move Tool",
                    "Click destination point",
                    level=0,  # Info level
                    duration=2
                )

            else:
                # Second click - perform the move
                dx = point.x() - self.start_point.x()
                dy = point.y() - self.start_point.y()
                self.callback(dx, dy)
                self.first_click = True
                self.iface.messageBar().pushMessage(
                    "Move Tool",
                    f"Features moved by {dx:.2f}, {dy:.2f}",
                    level=0,
                    duration=3
                )

        def deactivate(self):
            super().deactivate()
            self.first_click = True
            self.start_point = None

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar."""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = r'C:\Users\BhavaniR.DCILU1\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\move_multiple_layer_features\icon_01.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Move Multiple Layer Features'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Move_Multiple_layer_features'),
                action)
            self.iface.removeToolBarIcon(action)
        if self.move_tool:
            self.iface.mapCanvas().unsetMapTool(self.move_tool)
        if self.move_action:
            self.iface.removeToolBarIcon(self.move_action)
        if self.undo_action:
            self.iface.removeToolBarIcon(self.undo_action)

  # def move_features(self, dx, dy):
    #     """Move selected features in all editable layers."""
    #     moved = False
    #     layers = QgsProject.instance().layerTreeRoot().findLayers()
        
    #     for layer in layers:
    #         if isinstance(layer.layer(), QgsVectorLayer):
    #             vector_layer = layer.layer()
    #             vector_layer.startEditing()				
    #             if vector_layer.isEditable():
    #                 selected_features = vector_layer.selectedFeatures()
    #                 if selected_features:
    #                     for feat in selected_features:
    #                         geom = feat.geometry()
    #                         if geom and not geom.isEmpty():
    #                             geom.translate(dx, dy)
    #                             vector_layer.changeGeometry(feat.id(), geom)
    #                     moved = True
        
    #     if moved:
    #         self.iface.mapCanvas().refresh()
    #     else:
    #         QMessageBox.warning(None, "Warning", "No editable layers with selected features found.")
	
    # def move_features(self, dx, dy):
    #     """Move selected features in all editable layers and store original geometries for undo."""
    #     self._moved_features = {}  # Dictionary: { layer_id: {feat_id: original_geometry} }
    #     moved = False
    #     layers = QgsProject.instance().layerTreeRoot().findLayers()

    #     for layer in layers:
    #         if isinstance(layer.layer(), QgsVectorLayer):
    #             vector_layer = layer.layer()
    #             vector_layer.startEditing()
    #             if vector_layer.isEditable():
    #                 selected_features = vector_layer.selectedFeatures()
    #                 if selected_features:
    #                     QMessageBox.warning(None, "Warning", "Layer Feature was not selected.")
    #                     self._moved_features[vector_layer.id()] = {}
    #                     for feat in selected_features:
    #                         geom = feat.geometry()
    #                         if geom and not geom.isEmpty():
    #                             # Store original geometry
    #                             self._moved_features[vector_layer.id()][feat.id()] = QgsGeometry(geom)
    #                             # Translate geometry
    #                             geom.translate(dx, dy)
    #                             vector_layer.changeGeometry(feat.id(), geom)
    #                     moved = True

    #     if moved:
    #         self.iface.mapCanvas().refresh()
    #     else:
    #         QMessageBox.warning(None, "Warning", "No editable layers with selected features found.")
	
    def move_features(self, dx, dy):
        """Move selected features in all editable vector layers and store original geometries for undo."""
        self._moved_features = {}  # Dictionary: { layer_id: {feat_id: original_geometry} }
        moved = False
        has_selected_features = False
        debug_info = []

        layers = QgsProject.instance().layerTreeRoot().findLayers()

        for layer in layers:
            vl = layer.layer()
            if isinstance(vl, QgsVectorLayer):  # Ignore raster and non-vector layers
                editable = vl.isEditable()
                selected_features = vl.selectedFeatures()
                debug_info.append(f"{vl.name()} - Editable: {editable}, Selected: {len(selected_features)}")

                if editable and selected_features:
                    has_selected_features = True

        if not has_selected_features:
            QMessageBox.warning(None, "Warning", "No features are selected in any editable vector layer.")
            print("\n".join(debug_info))
            return

        for layer in layers:
            vl = layer.layer()
            if isinstance(vl, QgsVectorLayer) and vl.isEditable():
                selected_features = vl.selectedFeatures()
                if selected_features:
                    if not vl.isEditable():
                        vl.startEditing()
                    self._moved_features[vl.id()] = {}
                    for feat in selected_features:
                        geom = feat.geometry()
                        if geom and not geom.isEmpty():
                            # Store original geometry
                            self._moved_features[vl.id()][feat.id()] = QgsGeometry(geom)
                            # Translate and update geometry
                            geom.translate(dx, dy)
                            vl.changeGeometry(feat.id(), geom)
                    moved = True

        if moved:
            self.iface.mapCanvas().refresh()
            print("Features moved successfully.")
        else:
            print("No features were moved.")


    def undo_move_features(self, dx=None, dy=None):
        """Undo the last move by restoring original geometries."""
        if not hasattr(self, '_moved_features') or not self._moved_features:
           # QMessageBox.information(None, "Undo", "No previous move found to undo.")
            self.iface.messageBar().pushMessage(
                "Undo Tool",
                 "No previous move found to undo.",
                  level=2,  # Warning level
                  duration=4
            )
            return

        for layer_id, features in self._moved_features.items():
            vector_layer = QgsProject.instance().mapLayer(layer_id)
            if vector_layer and vector_layer.isEditable():
                for feat_id, original_geom in features.items():
                    vector_layer.changeGeometry(feat_id, original_geom)

        self.iface.mapCanvas().refresh()
        self._moved_features = {}  # Clear after undo


    def run(self):
        """Run method that performs all the real work"""
        if self.first_start:
            self.first_start = False
            self.dlg = Move_Multiple_layer_featuresDialog()
       
        # Create the move tool if it doesn't exist
        if not self.move_tool:
            self.move_tool = self.MoveSelectedFeaturesTool(self.iface, self.move_features)
        
        # Create the move action
        if not self.move_action:
            self.move_action = QAction(
                "",
                self.iface.mainWindow()
            )####Move Feature
            self.move_action.setCheckable(True)
            self.move_action.setShortcut(QKeySequence("M"))
            self.move_action.toggled.connect(self.toggle_move_tool)
            self.move_action.setStatusTip("Click first to set base point, then click to move selected features.")
            self.iface.addToolBarIcon(self.move_action)
			
        # Create the undo action (no need for a tool)
        if not self.undo_action:
            self.undo_action = QAction(
                "",
                self.iface.mainWindow()
            )##Undo Features
            # Not checkable since it's not a tool
            self.undo_action.setShortcut(QKeySequence("Z")) 
            # Connect directly to undo function, not a toggle
            self.undo_action.triggered.connect(self.undo_move_features)
            self.undo_action.setStatusTip("Undo last move operation")
            self.iface.addToolBarIcon(self.undo_action)
        
        # Only activate the move tool
        self.move_action.setChecked(True)
        self.toggle_move_tool(True)
        #self.dlg.show()
        #self.iface.removeToolBarIcon(self.move_action)
    # Remove the toggle_undo_tool method completely as it's not needed

    def toggle_move_tool(self, checked):
        """Toggle the move tool on or off."""
        if checked:
            self.iface.mapCanvas().setMapTool(self.move_tool)
        else:
            self.iface.mapCanvas().setMapTool(self.move_tool)
			
			