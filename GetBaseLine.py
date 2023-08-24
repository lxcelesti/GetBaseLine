# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetBaseLine
                                 A QGIS plugin
 GetBaseLine
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-07-24
        git sha              : $Format:%H$
        copyright            : (C) 2023 by LX
        email                : celesti@lx.or.kr
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsProject, QgsVectorLayer, Qgis, QgsVectorFileWriter, QgsField, QgsExpression, QgsExpressionContextUtils, QgsExpressionContext, QgsFillSymbol, QgsMapLayer, QgsProcessingException
from qgis.PyQt.QtCore import QVariant
import processing

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .GetBaseLine_dialog import GetBaseLineDialog
import os.path


class GetBaseLine:
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
            'GetBaseLine_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GetBaseLine')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GetBaseLine', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GetBaseLine/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GetBaseLine'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GetBaseLine'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_output_file(self):
        output_filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select   output file ", "", '*.shp')
        self.dlg.lineEdit.setText(output_filename)

    def select_input_file(self):
        input_filename, _filter = QFileDialog.getOpenFileName(
            self.dlg, "Select input file ", "", '*.shp')

        for i in range(0, self.dlg.comboBox.count()) :
            if input_filename == self.dlg.comboBox.itemText(i):
                self.dlg.comboBox.removeItem(i)
            else:
                pass

        self.dlg.comboBox.addItems([input_filename])

        self.dlg.comboBox.setCurrentIndex(self.dlg.comboBox.count() - 1)

    def run(self):
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = GetBaseLineDialog()
            self.dlg.pushButton.clicked.connect(self.select_output_file)
            self.dlg.inputButton.clicked.connect(self.select_input_file)

        self.dlg.comboBox.clear()
        layers = QgsProject.instance().layerTreeRoot().children()
        self.dlg.comboBox.addItems([layer.name() for layer in layers])

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed

        flayer = QgsVectorLayer()
        vlayer = QgsVectorLayer()
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "ESRI Shapefile"
        save_options.fileEncoding = "UTF-8"
        transform_context = QgsProject.instance().transformContext()
        error = []
        is_vector_layer = False
        is_filewriter = False
        black_symbol = QgsFillSymbol.createSimple(
            {"outline_style": "solid", "outline_color": "black", "color": "#00ff0000", "outline_width": "0.5"})
        red_symbol = QgsFillSymbol.createSimple(
            {"outline_style": "solid", "outline_color": "Red", "color": "#00ff0000", "outline_width": "1"})

        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            output_fieldnames = self.dlg.lineEdit.text()

            input_filename = self.dlg.comboBox.currentText()
            self.iface.messageBar().pushMessage("msg", "input_filename(layer): " + input_filename, level=Qgis.Info)
            self.iface.messageBar().pushMessage("msg", "QGIS version check: " + str(Qgis.QGIS_VERSION_INT), level=Qgis.Info)
            if Qgis.QGIS_VERSION_INT < 29999:
                self.iface.messageBar().pushMessage("msg", "This plug-in is compatible on QGIS 3.0 above. It won't work for this computer. Please upgrade your QGIS to the latest one", level=Qgis.Info)

            # 입력레이어가 레이어 형식인 경우
            if ":/" not in input_filename:
                for layer in layers:
                    if input_filename == layer.name():
                        if hasattr(layer, 'layer'):
                            vlayer = layer.layer()
                            self.iface.messageBar().pushMessage("msg", "selected layer is " + str(type(vlayer).__name__), level=Qgis.Info)
                            if str(type(vlayer).__name__) == "QgsVectorLayer":
                                is_vector_layer = True
                            else:
                                is_vector_layer = False
                        else:
                            is_vector_layer = False
                            self.iface.messageBar().pushMessage("msg", "No layer: " + str(type(layer).__name__), level=Qgis.Info)
                        break

            # S 입력레이어가 파일 형식인 경우
            else:
                self.iface.messageBar().pushMessage("msg", input_filename + " is file type", level=Qgis.Info)

                flayer = QgsVectorLayer(input_filename, "poly", "ogr")
                if not flayer.isValid():
                    self.iface.messageBar().pushMessage("msg", "Layer failed to load!: " + input_filename, level=Qgis.Info)
                else:
                    is_vector_layer = True
                    self.iface.messageBar().pushMessage("msg", "Layer loaded", level=Qgis.Info)

                f_name = os.path.splitext(os.path.basename(input_filename))[0] + "_temp"
                file_num = 0
                dup_chk_fin = False
                dup_chk_num = 0
                new_name = f_name

                self.iface.messageBar().pushMessage("msg", "# of layer: " + str(len(layers)), level=Qgis.Info)

                while dup_chk_fin == False:
                    file_num += 1
                    dup_chk_num = 0

                    for layer in layers:
                        if new_name == layer.name():
                            self.iface.messageBar().pushMessage("msg", "The same layer exists. Renaming " + new_name,
                                                                level=Qgis.Info)
                            new_name = f_name + "(" + str(file_num) + ")"
                            break
                        else:
                            dup_chk_num += 1
                    if len(layers) == dup_chk_num:
                        dup_chk_fin = True
                        f_name = new_name
                self.iface.messageBar().pushMessage("msg", "# of check: " + str(dup_chk_num), level=Qgis.Info)

                temp_filename = ''.join(os.path.dirname(input_filename)) + "/" + f_name + ".shp"

                if hasattr(QgsVectorFileWriter, 'writeAsVectorFormatV3'):
                    self.iface.messageBar().pushMessage("msg", "writeAsVectorFormatV3", level=Qgis.Info)
                    error = QgsVectorFileWriter.writeAsVectorFormatV3(flayer, temp_filename, transform_context, save_options)
                elif hasattr(QgsVectorFileWriter, 'writeAsVectorFormatV2'):
                    self.iface.messageBar().pushMessage("msg", "writeAsVectorFormatV2", level=Qgis.Info)
                    error = QgsVectorFileWriter.writeAsVectorFormatV2(flayer, temp_filename, transform_context, save_options)
                elif hasattr(QgsVectorFileWriter, 'writeAsVectorFormat'):
                    self.iface.messageBar().pushMessage("msg", "writeAsVectorFormat", level=Qgis.Info)
                    error = QgsVectorFileWriter.writeAsVectorFormat(flayer, temp_filename, 'utf-8', flayer.crs(), 'ESRI Shapefile')
                else:
                    self.iface.messageBar().pushMessage("msg", "no writeAsVectorFormatV, Can't save temp file. Check the Qgis version", level=Qgis.Info)

                if error[0] == QgsVectorFileWriter.NoError:
                    is_filewriter = True
                    self.iface.messageBar().pushMessage("msg", "Created temp layer.", level=Qgis.Info)
                else:
                    self.iface.messageBar().pushMessage("ERROR", "Fail to create temp layer. " + str(error[1]), level=Qgis.Critical)
                    is_filewriter = False
                    print(error)

                path_to_poly_layer = temp_filename
                vlayer = QgsVectorLayer(path_to_poly_layer, f_name, "ogr")
                if not vlayer.isValid():
                    print("Copy Layer failed to load!")
                else:
                    QgsProject.instance().addMapLayer(vlayer)
                    print("Copy Layer loaded!")
            # E 입력레이어가 파일 형식인 경우

            bfield_cnt = 0
            pnu_field_cnt = 0

            if hasattr(vlayer, 'fields'):
                for f in vlayer.fields():
                    if f.name() == "BUNGI" or f.name() == "bungi":
                        bfield_cnt += 1
                    elif f.name() == "PNU" or f.name() == "pnu":
                        pnu_field_cnt += 1

            if not is_vector_layer:
                self.iface.messageBar().pushMessage("msg", input_filename + " is not Vector layer.", level=Qgis.Info)
            elif not is_filewriter:
                if Qgis.QGIS_VERSION_INT < 29999:
                    self.iface.messageBar().pushMessage("msg", "Check the QGis version. Please change the version to 3.0 or above.", level=Qgis.Info)
                else:
                    self.iface.messageBar().pushMessage("msg",
                                                        "ERROR: Fail to write a file.",
                                                        level=Qgis.Info)

            elif pnu_field_cnt < 1:
                self.iface.messageBar().pushMessage("msg", input_filename + " doesn't have PNU.", level=Qgis.Info)
            else:
                print("PNU validation checked OK")

                if bfield_cnt > 0:
                    print("bungi validation checked OK")
                else:
                    pr = vlayer.dataProvider()
                    pr.addAttributes([QgsField("bungi", QVariant.String)])
                    vlayer.updateFields()
                    print("bungi field is created")

                expression1 = QgsExpression('left("PNU", 15)')
                expression2 = QgsExpression('length("PNU" )')
                context = QgsExpressionContext()
                context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vlayer))

                pnu_count = 0
                pnu_valid = 0
                pnu_len = 0

                vlayer.beginEditCommand("Feature triangulation")
                vlayer.startEditing()

                for field in vlayer.getFeatures():
                    pnu_count += 1

                    context.setFeature(field)
                    field["bungi"] = expression1.evaluate(context)
                    pnu_len = expression2.evaluate(context)
                    if pnu_len == 19:
                        pnu_valid += 1
                        vlayer.updateFeature(field)

                        print(field["bungi"], pnu_count)

                vlayer.commitChanges()
                vlayer.endEditCommand()

                vlayer.updateFields()

                vlayer.renderer().setSymbol(black_symbol)
                vlayer.triggerRepaint()

                self.iface.layerTreeView().refreshLayerSymbology(vlayer.id())

                self.iface.messageBar().pushMessage("msg", str(pnu_valid) + " of " + str(pnu_count)
                                                    + " PNUs are valid and processed.", level=Qgis.Info)

                output_filename = self.dlg.lineEdit.text()

                try:
                    dissolve_result = processing.runAndLoadResults("native:dissolve", {'INPUT': vlayer, 'FIELD': "bungi",
                                                                                   'OUTPUT': 'TEMPORARY_OUTPUT'})
                except:
                    self.iface.messageBar().pushMessage("msg", "Errors occurred while processing", level=Qgis.Info)

                olayer = self.iface.activeLayer()
                olayer.renderer().setSymbol(red_symbol)
                olayer.triggerRepaint()
                self.iface.layerTreeView().refreshLayerSymbology(olayer.id())

                if hasattr(QgsVectorFileWriter, 'writeAsVectorFormatV3'):
                    error = QgsVectorFileWriter.writeAsVectorFormatV3(olayer,
                                                                      output_filename,
                                                                      transform_context,
                                                                      save_options)
                elif hasattr(QgsVectorFileWriter, 'writeAsVectorFormatV2'):
                    error = QgsVectorFileWriter.writeAsVectorFormatV2(olayer,
                                                                      output_filename,
                                                                      transform_context,
                                                                      save_options)

                elif hasattr(QgsVectorFileWriter, 'writeAsVectorFormat'):
                    error = QgsVectorFileWriter.writeAsVectorFormat(olayer,
                                                                    output_filename,
                                                                    'utf-8',
                                                                    olayer.crs(),
                                                                    'ESRI Shapefile')

                else:
                    self.iface.messageBar().pushMessage("msg", "no writeAsVectorFormat, Can't save output file. Check the Qgis version", level=Qgis.Info)

                if error[0] == QgsVectorFileWriter.NoError:
                    self.iface.messageBar().pushMessage("Success", "Output file written at " + output_filename,
                                                        level=Qgis.Success, duration=3)
                else:
                    self.iface.messageBar().pushMessage("Error", str(error[1]), level=Qgis.Critical, duration=3)










