#!/usr/bin/env python3

from gi.repository import Gtk, Gdk
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np


programInstallDirectory = "/home/wes/Personal/python"






class usefulConstantsDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Useful Constants", parent, 0)
        #self.set_default_size(600, 300)

        box = self.get_content_area()

        self.show_all()




#create new class that inherits methods from super-class
class plot2dApp(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: 2 Dimensional Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        #self.set_default_size(1000, 800)
        self.set_border_width(5)


        #some constants

        self.saveButtonImagePath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/saveButton.png")
        self.quitButtonImagePath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/quitButton.png")
        self.infoButtonImagePath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/infoButton.png")
        self.helpButtonImagePath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/helpButton.png")
        self.importButtonImagePath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/importButton.png")
        self.plotButtonImagePath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/plotButton.png")

        
        #setting up the window structure

        self.mainWindowBox = Gtk.Box()
        self.leftVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.middleVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.rightVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.leftVBoxUpper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.leftVBoxLower = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.middleUpFrame = Gtk.Frame(label='Geometry')
        self.middleMidFrame = Gtk.Frame(label='Labels')
        self.middleDownFrame = Gtk.Frame(label='Colours')


        #setting up some mid-level containers for groups of individual widgets
        
        self.mainMenu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.geometryBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.geometryGrid = Gtk.Grid()
        self.geometryGrid.set_column_spacing(10)
        self.geometryGrid.set_row_spacing(10)
        self.labelsBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.labelsGrid = Gtk.Grid()
        self.labelsGrid.set_column_spacing(10)
        self.labelsGrid.set_row_spacing(10)
        self.coloursGrid = Gtk.Grid()
        self.dataGrid = Gtk.Grid()
        self.plotAspectFrame = Gtk.Frame(label='Plot Window')
        self.plotButtonBox = Gtk.Box()
        self.dataOptionsFrame = Gtk.Frame(label='Data')


        #packing mid-level and high-level containers
        
        self.add(self.mainWindowBox)
        self.mainWindowBox.pack_start(self.leftVBox, False, True, 5)
        self.mainWindowBox.pack_start(self.middleVBox, True, True, 5)
        self.mainWindowBox.pack_start(self.rightVBox, True, True, 5)
        self.leftVBox.pack_start(self.leftVBoxUpper, False, False, 1)
        self.leftVBox.pack_end(self.leftVBoxLower, True, True, 1)
        self.leftVBoxUpper.pack_start(self.mainMenu, True, True, 0)
        self.middleVBox.pack_start(self.middleUpFrame, True, True, 5)
        self.middleVBox.pack_start(self.middleMidFrame, True, True, 5)
        self.middleVBox.pack_start(self.middleDownFrame, True, True, 5)
        self.rightVBox.pack_start(self.plotAspectFrame, True, True, 5)
        self.rightVBox.pack_start(self.plotButtonBox, False, False, 5)
        self.rightVBox.pack_start(self.dataOptionsFrame, True, True, 5)
        self.dataOptionsFrame.add(self.dataGrid)
        self.middleUpFrame.add(self.geometryBox)
        self.middleMidFrame.add(self.labelsBox)


        #making and formatting the widgets

        #button images
        self.plotButtonImage = Gtk.Image.new_from_file(self.plotButtonImagePath)
        self.saveButtonImage = Gtk.Image.new_from_file(self.saveButtonImagePath)
        self.quitButtonImage = Gtk.Image.new_from_file(self.quitButtonImagePath)
        self.infoButtonImage = Gtk.Image.new_from_file(self.infoButtonImagePath)
        self.helpButtonImage = Gtk.Image.new_from_file(self.helpButtonImagePath)
        self.importButtonImage = Gtk.Image.new_from_file(self.importButtonImagePath)

        #main menu buttons
        self.saveButton = Gtk.Button()
        self.saveButton.set_image(self.saveButtonImage)
        self.quitButton = Gtk.Button()
        self.quitButton.set_image(self.quitButtonImage)
        self.infoButton = Gtk.Button()
        self.infoButton.set_image(self.infoButtonImage)
        self.helpButton = Gtk.Button()
        self.helpButton.set_image(self.helpButtonImage)
        self.importButton = Gtk.Button()
        self.importButton.set_image(self.importButtonImage)
        self.plotButton = Gtk.Button()
        self.plotButton.set_image(self.plotButtonImage)

        #Setting up the figure and adding it to the layout
        self.fig = Figure(figsize=(10,10), dpi=80)
        self.ax = self.fig.add_subplot(111, aspect=.6)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(550, 400)
        self.fig.patch.set_facecolor('#222222')             #add get figure facecolor here (default facecolor)

        #slider to control the figure aspect ratio
        self.aspectScaleLabel = Gtk.Label('Aspect Ratio')
        self.aspectScale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.aspectScaleAdj = Gtk.Adjustment.new(1.0, 0.5, 2.0, 0.1, .5, 0)
        self.aspectScale.set_adjustment(self.aspectScaleAdj)
        self.aspectScale.set_draw_value(False)

        #more geometry options
        self.xRangeMinLabel = Gtk.Label('x-Range Min')
        self.xRangeMinEntry = Gtk.Entry()
        self.xRangeMinEntry.props.has_frame=False
        self.xRangeMinEntry.set_text('0.0')
        self.xRangeMinEntry.set_width_chars(4)
        
        self.yRangeMinLabel = Gtk.Label('y-Range Min')
        self.yRangeMinEntry = Gtk.Entry()
        self.yRangeMinEntry.props.has_frame=False
        self.yRangeMinEntry.set_text('0.0')
        self.yRangeMinEntry.set_width_chars(4)
        
        self.xRangeMaxLabel = Gtk.Label('x-Range Max')
        self.xRangeMaxEntry = Gtk.Entry()
        self.xRangeMaxEntry.props.has_frame=False
        self.xRangeMaxEntry.set_text('10.0')
        self.xRangeMaxEntry.set_width_chars(4)
        
        self.yRangeMaxLabel = Gtk.Label('y-Range Max')
        self.yRangeMaxEntry = Gtk.Entry()
        self.yRangeMaxEntry.props.has_frame=False
        self.yRangeMaxEntry.set_text('10.0')
        self.yRangeMaxEntry.set_width_chars(4)
        
        self.switchAutoXRangeLabel = Gtk.Label('Auto x-Range')
        self.switchAutoXRange = Gtk.Switch()
        self.switchAutoXRange.set_active(True)
        
        self.switchAutoYRangeLabel = Gtk.Label('Auto y-Range')
        self.switchAutoYRange = Gtk.Switch()
        self.switchAutoYRange.set_active(True)

        self.graphSwitchGridLabel = Gtk.Label("Grid")
        self.graphSwitchGrid = Gtk.Switch()
        self.graphSwitchGrid.set_active(True)


        #label options

        self.graphTitleLabel = Gtk.Label("Title")
        self.graphTitleEntry = Gtk.Entry()
        self.graphTitleEntry.props.has_frame=False
        self.graphTitleEntry.set_editable(True)
        self.graphTitleEntry.set_width_chars(6)
        self.sizeTitleSpinnerLabel = Gtk.Label('Font Size')
        self.sizeTitleSpinner = Gtk.SpinButton()
        self.sizeTitleSpinner.props.has_frame=False
        self.sizeTitleSpinner.set_digits(0)
        self.sizeTitleSpinner.set_update_policy(1)
        self.sizeTitleSpinner.set_numeric(True)
        self.sizeTitleSpinnerAdj = Gtk.Adjustment.new(15, 5, 20, 1, 2, 0)
        self.sizeTitleSpinner.set_adjustment(self.sizeTitleSpinnerAdj)

        self.graphXLabel = Gtk.Label("x Label")
        self.graphXLabelEntry = Gtk.Entry()
        self.graphXLabelEntry.props.has_frame=False
        self.graphXLabelEntry.set_editable(True)
        self.graphXLabelEntry.set_width_chars(6)
        self.sizeXLabelSpinnerLabel = Gtk.Label('Font Size')
        self.sizeXLabelSpinner = Gtk.SpinButton()
        self.sizeXLabelSpinner.props.has_frame=False
        self.sizeXLabelSpinner.set_digits(0)
        self.sizeXLabelSpinner.set_update_policy(1)
        self.sizeXLabelSpinner.set_numeric(True)
        self.sizeXLabelSpinnerAdj = Gtk.Adjustment.new(15, 5, 20, 1, 2, 0)
        self.sizeXLabelSpinner.set_adjustment(self.sizeXLabelSpinnerAdj)
        
        self.graphYLabel = Gtk.Label("y Label")
        self.graphYLabelEntry = Gtk.Entry()
        self.graphYLabelEntry.props.has_frame=False
        self.graphYLabelEntry.set_editable(True)
        self.graphYLabelEntry.set_width_chars(6)
        self.sizeYLabelSpinnerLabel = Gtk.Label('Font Size')
        self.sizeYLabelSpinner = Gtk.SpinButton()
        self.sizeYLabelSpinner.props.has_frame=False
        self.sizeYLabelSpinner.set_digits(0)
        self.sizeYLabelSpinner.set_update_policy(1)
        self.sizeYLabelSpinner.set_numeric(True)
        self.sizeYLabelSpinnerAdj = Gtk.Adjustment.new(15, 5, 20, 1, 2, 0)
        self.sizeYLabelSpinner.set_adjustment(self.sizeYLabelSpinnerAdj)

        self.graphXUnits = Gtk.Label("x Units")
        self.graphXUnitsEntry = Gtk.Entry()
        self.graphXUnitsEntry.props.has_frame=False
        self.graphXUnitsEntry.set_editable(True)
        self.graphXUnitsEntry.set_width_chars(6)
        
        self.graphYUnits = Gtk.Label("y Units")
        self.graphYUnitsEntry = Gtk.Entry()
        self.graphYUnitsEntry.props.has_frame=False
        self.graphYUnitsEntry.set_editable(True)
        self.graphYUnitsEntry.set_width_chars(6)
        
        self.graphAuthorLabel = Gtk.Label("Author")
        self.graphAuthorEntry = Gtk.Entry()
        self.graphAuthorEntry.props.has_frame=False
        self.graphAuthorEntry.set_editable(True)
        self.graphAuthorEntry.set_width_chars(6)
        self.sizeAuthorSpinnerLabel = Gtk.Label('Font Size')
        self.sizeAuthorSpinner = Gtk.SpinButton()
        self.sizeAuthorSpinner.props.has_frame=False
        self.sizeAuthorSpinner.set_digits(0)
        self.sizeAuthorSpinner.set_update_policy(1)
        self.sizeAuthorSpinner.set_numeric(True)
        self.sizeAuthorSpinnerAdj = Gtk.Adjustment.new(15, 5, 20, 1, 2, 0)
        self.sizeAuthorSpinner.set_adjustment(self.sizeAuthorSpinnerAdj)

        self.switchMajorTicsLabel = Gtk.Label('Major Tics')
        self.switchMajorTicsRange = Gtk.Switch()
        self.switchMajorTicsRange.set_active(True)

        self.switchMinorTicsLabel = Gtk.Label('Minor Tics')
        self.switchMinorTicsRange = Gtk.Switch()
        self.switchMinorTicsRange.set_active(False)



        #packing widgets into containers


        self.mainMenu.pack_start(self.importButton, True, True, 5)
        self.mainMenu.pack_start(self.helpButton, True, True, 5)
        self.mainMenu.pack_start(self.infoButton, True, True, 5)
        self.mainMenu.pack_start(self.quitButton, True, True, 5)
        self.plotButtonBox.pack_start(self.plotButton, False, False, 0)
        self.plotButtonBox.pack_start(self.saveButton, False, False, 0)
        self.plotAspectFrame.add(self.canvas)

        self.geometryBox.pack_start(self.aspectScaleLabel, True, True, 5)
        self.geometryBox.pack_start(self.aspectScale, True, True, 5)
        self.geometryBox.pack_start(self.geometryGrid, True, True, 5)
        self.geometryGrid.attach(self.xRangeMinLabel, 0, 0, 1, 1)
        self.geometryGrid.attach(self.xRangeMinEntry, 1, 0, 1, 1)
        self.geometryGrid.attach(self.xRangeMaxLabel, 2, 0, 1, 1)
        self.geometryGrid.attach(self.xRangeMaxEntry, 3, 0, 1, 1)
        self.geometryGrid.attach(self.yRangeMinLabel, 0, 1, 1, 1)
        self.geometryGrid.attach(self.yRangeMinEntry, 1, 1, 1, 1)
        self.geometryGrid.attach(self.yRangeMaxLabel, 2, 1, 1, 1)
        self.geometryGrid.attach(self.yRangeMaxEntry, 3, 1, 1, 1)
        self.geometryGrid.attach(self.switchAutoXRangeLabel, 0, 2, 1, 1)
        self.geometryGrid.attach(self.switchAutoXRange, 1, 2, 1, 1)
        self.geometryGrid.attach(self.switchAutoYRangeLabel, 2, 2, 1, 1)
        self.geometryGrid.attach(self.switchAutoYRange, 3, 2, 1, 1)
        self.geometryGrid.attach(self.graphSwitchGridLabel, 0, 3, 1, 1)
        self.geometryGrid.attach(self.graphSwitchGrid, 1, 3, 1, 1)


        self.labelsBox.pack_start(self.labelsGrid, True, True, 5)
        self.labelsGrid.attach(self.graphXLabel, 0, 0, 1, 1)
        self.labelsGrid.attach(self.graphXLabelEntry, 1, 0, 1, 1)
        self.labelsGrid.attach(self.graphYLabel, 0, 2, 1, 1)
        self.labelsGrid.attach(self.graphYLabelEntry, 1, 2, 1, 1)
        self.labelsGrid.attach(self.graphXUnits, 0, 1, 1, 1)
        self.labelsGrid.attach(self.graphXUnitsEntry, 1, 1, 1, 1)
        self.labelsGrid.attach(self.graphYUnits, 0, 3, 1, 1)
        self.labelsGrid.attach(self.graphYUnitsEntry, 1, 3, 1, 1)
        self.labelsGrid.attach(self.graphTitleLabel, 0, 4, 1, 1)
        self.labelsGrid.attach(self.graphTitleEntry, 1, 4, 1, 1)
        self.labelsGrid.attach(self.graphAuthorLabel, 0, 5, 1, 1)
        self.labelsGrid.attach(self.graphAuthorEntry, 1, 5, 1, 1)
        self.labelsGrid.attach(self.sizeXLabelSpinnerLabel, 2, 0, 1, 1)
        self.labelsGrid.attach(self.sizeXLabelSpinner, 3, 0, 1, 1)
        self.labelsGrid.attach(self.sizeYLabelSpinnerLabel, 2, 2, 1, 1)
        self.labelsGrid.attach(self.sizeYLabelSpinner, 3, 2, 1, 1)
        self.labelsGrid.attach(self.sizeTitleSpinnerLabel, 2, 4, 1, 1)
        self.labelsGrid.attach(self.sizeTitleSpinner, 3, 4, 1, 1)
        self.labelsGrid.attach(self.sizeAuthorSpinnerLabel, 2, 5, 1, 1)
        self.labelsGrid.attach(self.sizeAuthorSpinner, 3, 5, 1, 1)



        #connect signals to callbacks

        self.aspectScale.connect("value-changed", self.onAspectChanged)
        self.canvas.draw()



#        css = b"""
#        GtkWindow {
#        background-image: -gtk-gradient(radial, center center, 0, center center, 1, from(#555), to(#000)) ;
#        }
#        GtkButton {
#        background-color: #000000 ;
#        color: #000000 ;
#        }

#        """
        
#        style_provider = Gtk.CssProvider()
#        style_provider.load_from_data(css)
        
#        Gtk.StyleContext.add_provider_for_screen(
#            Gdk.Screen.get_default(),
#            style_provider,
#            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
#        )




    def onAspectChanged(self, widget):
        self.ax.set_aspect(aspect=self.aspectScale.get_value(), adjustable='box', anchor='C')
        self.fig.canvas.draw()








    #define a function that clears the plot, resets limits, and refreshes the grid
    def resetplot(self, axisChoice="both", autox=False, autoy=False):
        xmin = float(self.xRangeMinEntry.get_text())
        ymin = float(self.yRangeMinEntry.get_text())
        xmax = float(self.xRangeMaxEntry.get_text())
        ymax = float(self.yRangeMaxEntry.get_text())
        self.ax.cla()
        if self.graphAuthorEntry.get_text() == '':
            pass
        else:
            self.ax.annotate("Author: " + self.graphAuthorEntry.get_text(), xy=(.02,.94), xycoords='axes fraction')
        self.ax.grid(self.graphSwitchGrid.get_active())
        self.ax.set_title(self.graphTitleEntry.get_text())
        self.ax.set_xlabel(self.graphXLabelEntry.get_text() + " (" + self.graphXUnitsEntry.get_text() + ")")
        self.ax.set_ylabel(self.graphYLabelEntry.get_text() + " (" + self.graphYUnitsEntry.get_text() + ")")

        if autox:
            self.xRangeMinEntry.set_editable(False)
            self.xRangeMaxEntry.set_editable(False)
            self.ax.autoscale(enable=autox, axis="x")
        else:
            self.xRangeMaxEntry.set_editable(True)
            self.xRangeMinEntry.set_editable(True)
            self.ax.set_xlim(xmin,xmax)

        if autoy:
            self.yRangeMaxEntry.set_editable(False)
            self.yRangeMinEntry.set_editable(False)
            self.ax.autoscale(enable=autoy, axis="y")
        else:
            self.yRangeMaxEntry.set_editable(True)
            self.yRangeMinEntry.set_editable(True)
            self.ax.set_ylim(ymin,ymax)

        if autox and autoy:
            self.xRangeMinEntry.set_editable(False)
            self.xRangeMaxEntry.set_editable(False)
            self.yRangeMinEntry.set_editable(False)
            self.yRangeMaxEntry.set_editable(False)
            self.ax.autoscale(enable=True, axis="both")
        self.plotPoints()


    #define function to clear and replot the graph
    #one row in table = 1 point on graph
    def plotPoints(self):
        self.x, self.y = self.getPoints()
        if self.graphPlotComboBox.get_active_text() == "Lines":
            if self.graphYLabelEntry.get_text() == '':
                self.ax.plot(x, y, linestyle='solid', marker='+', label='data')
            else:
                self.ax.plot(x, y, linestyle='solid', marker='+', label=self.graphYLabelEntry.get_text())
        elif self.graphPlotComboBox.get_active_text() == "Scatter":
            if self.graphYLabelEntry.get_text() == '':
                self.ax.scatter(x, y, marker='+', label='data')
            else:
                self.ax.scatter(x, y, marker='+', label=self.graphYLabelEntry.get_text())
        elif self.graphPlotComboBox.get_active_text() == "Error Bars":
            if self.graphYLabelEntry.get_text() == '':
                self.ax.errorbar(x, y, xerr=dx, yerr=dy, marker='+', label='data')
            else:
                self.ax.errorbar(x, y, xerr=dx, yerr=dy, linestyle='solid', marker='+', label=self.graphYLabelEntry.get_text())
        self.ax.legend()
        self.fig.canvas.draw()




    def importDataDialog(self, parent):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        message = ""
        title = "Import Data"
        dialogWindow = Gtk.MessageDialog(parent,
                                         Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                         Gtk.MessageType.OTHER,
                                         Gtk.ButtonsType.OK_CANCEL,
                                         message)
        dialogWindow.set_title(title)
        dialogBox = dialogWindow.get_content_area()
        fileChooser = Gtk.FileChooserWidget()
        fileChooser.set_action(0)
        fileFilter = Gtk.FileFilter()
        fileFilter.add_mime_type("text/plain")
        fileFilter.set_name("TXT/DAT")
        fileChooser.add_filter(fileFilter)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.pack_start(fileChooser, True, True, 5)
        dialogBox.pack_start(vbox, True, True, 5)
        dialogWindow.show_all()
        response = dialogWindow.run()
        text = fileChooser.get_filename()
        dialogWindow.destroy()
        if (response == Gtk.ResponseType.OK) and (text != ''):
            return text
        else:
            return None












#create new class that inherits methods from super-class
class plot3dApp(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: 2 Dimensional Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(1000, 800)
        self.set_border_width(5)

        self.mainWindowBox = Gtk.Box()



#create new class that inherits methods from super-class
class linFitApp(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: 2 Dimensional Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(1000, 800)
        self.set_border_width(5)

        self.mainWindowBox = Gtk.Box()



#create new class that inherits methods from super-class
class rootFindApp(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: 2 Dimensional Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(1000, 800)
        self.set_border_width(5)

        self.mainWindowBox = Gtk.Box()



#create new class that inherits methods from super-class
class smootheApp(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: 2 Dimensional Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(1000, 800)
        self.set_border_width(5)

        self.mainWindowBox = Gtk.Box()



#create new class that inherits methods from super-class
class timeSeriesApp(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: 2 Dimensional Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(1000, 800)
        self.set_border_width(5)

        self.mainWindowBox = Gtk.Box()










#create new class that inherits methods from super-class
class mainMenu(Gtk.Window):

    def __init__(self):

        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGGR: Data Graphing, Regression, and Reduction')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(400, 800)
        self.set_border_width(100)

        #set up some constants

        self.mainIconPath = os.path.abspath(programInstallDirectory + "/DigGRR/assets/mainIcon.png")


        #set up containers

        self.mainWindowBox = Gtk.Box()
        self.innerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)


        
        #make and format widgets
        
        self.start2dPlot = Gtk.Button(label='2D Plot')
        self.start3dPlot = Gtk.Button(label='3D Plot')
        self.startLinFit = Gtk.Button(label='  Linear\nRegression')
        self.startLinFit.set_halign(.5)
        self.startRootFind = Gtk.Button(label='Root Finding')
        self.startSmoothe = Gtk.Button(label='Smoothing')
        self.startTimeSeries = Gtk.Button(label='Time Series')
        self.mainIcon = Gtk.Image.new_from_file(self.mainIconPath)        

        #pack widgets into containers

        self.add(self.mainWindowBox)
        self.mainWindowBox.pack_start(self.innerBox, True, False, 0)
        self.innerBox.pack_start(self.mainIcon, True, True, 5)
        self.innerBox.pack_start(self.start2dPlot, True, True, 5)
        self.innerBox.pack_start(self.start3dPlot, True, True, 5)
        self.innerBox.pack_start(self.startLinFit, True, True, 5)
        self.innerBox.pack_start(self.startRootFind, True, True, 5)
        self.innerBox.pack_start(self.startSmoothe, True, True, 5)
        self.innerBox.pack_start(self.startTimeSeries, True, True, 5)



        #connect button signals to callbacks
        self.start2dPlot.connect("clicked", self.on2dPlotClicked)
        self.start3dPlot.connect("clicked", self.on3dPlotClicked)
        self.startLinFit.connect("clicked", self.onLinFitClicked)
        self.startRootFind.connect("clicked", self.onRootFindClicked)
        self.startSmoothe.connect("clicked", self.onSmootheClicked)
        self.startTimeSeries.connect("clicked", self.onTimeSeriesClicked)


        #function definitions
        





        css = b"""
        GtkWindow {
        background-image: -gtk-gradient(radial, center center, 0, center center, 1, from(#888), to(#030303)) ;
        }
        GtkButton {
        border-image: none ;
        background-image: none ;
        background-color: #1f1f1f ;
        }
        GtkEntry {
        border-radius: 5px ;
        }
        GtkFrame {
        background-color: alpha(#000, .8) ;
        border-radius: 6px ;
        }
        GtkLabel {
        color: #bbb ;
        font: TlwgTypewriter, 10px ;
        font-weight: bold ;
        }
        """
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )





    def on2dPlotClicked(self, event):
        #create main application window and start Gtk loop
        plot2dWindow = plot2dApp()
        plot2dWindow.connect("delete-event", Gtk.main_quit)
        plot2dWindow.show_all()
        Gtk.main()

    def on3dPlotClicked(self, event):
        #create main application window and start Gtk loop
        plot3dWindow = plot3dApp()
        plot3dWindow.connect("delete-event", Gtk.main_quit)
        plot3dWindow.show_all()
        Gtk.main()

    def onLinFitClicked(self, event):
        #create main application window and start Gtk loop
        linFitWindow = linFitApp()
        linFitWindow.connect("delete-event", Gtk.main_quit)
        linFitWindow.show_all()
        Gtk.main()

    def onRootFindClicked(self, event):
        #create main application window and start Gtk loop
        rootFindWindow = rootFindApp()
        rootFindWindow.connect("delete-event", Gtk.main_quit)
        rootFindWindow.show_all()
        Gtk.main()

    def onSmootheClicked(self, event):
        #create main application window and start Gtk loop
        smootheWindow = smootheApp()
        smootheWindow.connect("delete-event", Gtk.main_quit)
        smootheWindow.show_all()
        Gtk.main()

    def onTimeSeriesClicked(self, event):
        #create main application window and start Gtk loop
        timeSeriesWindow = timeSeriesApp()
        timeSeriesWindow.connect("delete-event", Gtk.main_quit)
        timeSeriesWindow.show_all()
        Gtk.main()







#create main application window and start Gtk loop
titleWindow = mainMenu()
titleWindow.connect("delete-event", Gtk.main_quit)
titleWindow.show_all()
Gtk.main()
