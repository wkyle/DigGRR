#!/usr/bin/env python3

from gi.repository import Gtk, GLib
import os
programInstallDirectory = "/home/wes/Personal/python/DigGRR"

class window(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self)
        self.set_default_size(220, 40)
        self.button = Gtk.Button('button')
        self.add(self.button)
        
        self.button.connect("clicked", self.onButtonClicked)

    def onButtonClicked(self, widget):
        lst = self.getColumnIndices()
        print(lst)


    def getColumnIndices(self):
        self.getColumnIndicesDialog = Gtk.Dialog(title='Selection of Columns')
        self.getColumnIndicesDialog.set_default_size(500, 80)
        contentBox = self.getColumnIndicesDialog.get_content_area()

        vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hBox3 = Gtk.Box()
        hBox2 = Gtk.Box()
        hBox1 = Gtk.Box()
        xLabel = Gtk.Label('x')
        yLabel = Gtk.Label('y')
        dxLabel = Gtk.Label('dx')
        dyLabel = Gtk.Label('dy')
        message = Gtk.Label('\n Select data columns for plotting:\n')
        warningImagePath = os.path.abspath(programInstallDirectory + "/assets/warning.png")
        warningIcon = Gtk.Image.new_from_file(warningImagePath)
        warningLabel = Gtk.Label('You must select data columns for x and y')

        columnList = ['0', '1', '2', '3', '4']
        xCombo = Gtk.ComboBoxText()
        yCombo = Gtk.ComboBoxText()
        dxCombo = Gtk.ComboBoxText()
        dyCombo = Gtk.ComboBoxText()
        dxCombo.append_text('None')
        dyCombo.append_text('None')
        for i in columnList:
            xCombo.append_text(i)
            yCombo.append_text(i)
            dxCombo.append_text(i)
            dyCombo.append_text(i)

        self.getColumnIndicesDialog.add_button('Cancel', -13)
        self.getColumnIndicesDialog.add_button('OK', -14)
        contentBox.pack_start(vBox, True, True, 0)
        vBox.pack_start(message, True, True, 0)
        vBox.pack_start(hBox1, True, True, 0)
        hBox1.pack_start(xLabel, True, True, 0)
        hBox1.pack_start(yLabel, True, True, 0)
        hBox1.pack_start(dxLabel, True, True, 0)
        hBox1.pack_start(dyLabel, True, True, 0)
        vBox.pack_start(hBox2, True, True, 0)
        hBox2.pack_start(xCombo, True, True, 0)
        hBox2.pack_start(yCombo, True, True, 0)
        hBox2.pack_start(dxCombo, True, True, 0)
        hBox2.pack_start(dyCombo, True, True, 0)
        vBox.pack_start(hBox3, True, True, 15)
        hBox3.pack_start(warningIcon, False, True, 0)
        hBox3.pack_start(warningLabel, False, True, 0)





        
        self.getColumnIndicesDialog.show_all()


        response = self.getColumnIndicesDialog.run()
        self.getColumnIndicesDialog.hide()
        if (response == -14):
            finalList = []
            if xCombo.get_active_text() == None or xCombo.get_active_text() == 'None':
                finalList.append(None)
            else:
                finalList.append(int(xCombo.get_active_text()))
            if yCombo.get_active_text() == None or yCombo.get_active_text() == 'None':
                finalList.append(None)
            else:
                finalList.append(int(yCombo.get_active_text()))
            if dxCombo.get_active_text() == None or dxCombo.get_active_text() == 'None':
                finalList.append(None)
            else:
                finalList.append(int(dxCombo.get_active_text()))
            if dyCombo.get_active_text() == None or dyCombo.get_active_text() == 'None':
                finalList.append(None)
            else:
                finalList.append(int(dyCombo.get_active_text()))
            if finalList[0] == None or finalList[1] == None:
                return None
            else:
                return finalList
        else:
            return None
















    def defineNewFunction(self):
        self.newFunctionDialog = Gtk.Dialog(title='New Function Definition')
        self.newFunctionDialog.set_default_size(200, 80)
        contentBox = self.newFunctionDialog.get_content_area()
        vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hBox = Gtk.Box()
        message = Gtk.Label('Define a function to plot:')
        entryLabel = Gtk.Label('f(x)= ')
        self.newFunctionDialogEntry = Gtk.Entry()
        self.newFunctionDialogEntry.set_editable(True)
        self.newFunctionDialog.add_button('Cancel', -13)
        self.newFunctionDialog.add_button('Define', -14)
        cancelButton = self.newFunctionDialog.get_widget_for_response(-13)
        defineButton = self.newFunctionDialog.get_widget_for_response(-14)
        self.newFunctionDialog.set_response_sensitive(-14, False)

        contentBox.pack_start(vBox, True, True, 0)
        vBox.pack_start(message, True, True, 0)
        vBox.pack_start(hBox, True, True, 0)
        hBox.pack_start(entryLabel, True, True, 0)
        hBox.pack_start(self.newFunctionDialogEntry, True, True, 0)
        timeoutID = GLib.timeout_add(1000, self.checkValidEntry, 
                                     self.newFunctionDialogEntry.get_text())
        self.newFunctionDialog.show_all()

        response = self.newFunctionDialog.run()
        text = self.newFunctionDialogEntry.get_text()
        self.newFunctionDialog.hide()
        if (response == -14) and (text != ''):
            GLib.source_remove(timeoutID)
            print(timeoutID)
            return text
        else:
            GLib.source_remove(timeoutID)
            print(timeoutID)
            return None

    def checkValidEntry(self, funcStr):
        print('checking...')
        try:
            temp = functionType(funcStr)
            self.newFunctionDialog.set_response_sensitive(-14, True)
        except:
            self.newFunctionDialog.set_response_sensitive(-14, False)
        return True


win = window()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
