#!/usr/bin/env python3
# version 1.1.0

from gi.repository import Gtk, Gdk, GLib, Poppler, GdkPixbuf
import csv
import os
import time
from matplotlib.figure import Figure
from matplotlib import rc
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from itertools import zip_longest
import xml.etree.ElementTree as et
programInstallDirectory = "/home/wes/Personal/python/DigGRR"
temp_file_storage = "/tmp/linefit_file_to_print.pdf"


class dataManager():

    """
    numberColumns: the number of columns held in storage
    columnData: the columns of stored data
    shortestLength: the number of values in the shortest column

    Currently needs csv, itertools.zip_longest, numpy

    15/11/15
    UPDATE: I'm going to modify this to take only 2(x,y), 3(x,y,dy) or 4(x,y,dx,dy) columns
            to simplify the structure of this program. It's getting a
            bit unwieldy trying to manage an arbitrary number of columns
    """
    
    def __init__(self):
        self.func_string = ''
        self.hasFilename = False
        self.hasData = False
        self.isLineFitted = False
        self.canFitLine = False
        self.filename = None
        self.numCols = 0
        self.isTruncated = True
        self.shortColumn = 0
        self.longColumn = 0
        self.delimDict = {0 : "\t",
                          '0' : "\t",
                          1 : " ",
                          '1' : " ",
                          2 : ",",
                          '2' : ","}
        self.delimiter = self.delimDict[0]
        self.x = []
        self.y = []
        self.dx = []
        self.dy = []
        self.lin_param = [None, None, None, None, None, None, None]

    def getLinParam(self):
        return self.lin_param

    def setLinParam(self, m=None, b=None, dm=None, db=None, root=None, droot=None, corr=None):
        self.lin_param = [m,b,dm,db,root,droot,corr]


    def loadFromFile(self, filename, use_cols=(True,True,True,True), cols=(0,1,2,3)):
        if filename.endswith('.csv'):
            if len(cols) == 4:
                self.x, self.y, self.dx, self.dy = np.loadtxt(filename, usecols=cols, delimiter=',', unpack=True)
                self.x, self.y, self.dx, self.dy = zip(*zip(self.x, self.y, self.dx, self.dy))
                self.hasData = True
            elif len(cols) == 3:
                if use_cols[2] == False:
                    self.x, self.y, self.dy = np.loadtxt(filename, usecols=cols, delimiter=',', unpack=True)
                    self.x, self.y, self.dy = zip(*zip(self.x, self.y, self.dy))
                    self.dx = [float(0) for i in self.x]
                    self.hasData = True
                elif use_cols[3] == False:
                    self.x, self.y, self.dx = np.loadtxt(filename, usecols=cols, delimiter=',', unpack=True)
                    self.x, self.y, self.dx = zip(*zip(self.x, self.y, self.dx))
                    self.dy = [float(0) for i in self.x]
                    self.hasData = True
            elif len(cols) == 2:
                self.x, self.y = np.loadtxt(filename, usecols=cols, delimiter=',', unpack=True)
                self.x, self.y = zip(*zip(self.x, self.y))
                self.dx = [float(0) for i in self.x]
                self.dy = self.dx
                self.hasData = True
                
        else:
            if len(cols) == 4:
                self.x, self.y, self.dx, self.dy = np.loadtxt(filename, usecols=cols, unpack=True)
                self.x, self.y, self.dx, self.dy = zip(*zip(self.x, self.y, self.dx, self.dy))
                self.hasData = True
            elif len(cols) == 3:
                if use_cols[2] == False:
                    self.x, self.y, self.dy = np.loadtxt(filename, usecols=cols, unpack=True)
                    self.x, self.y, self.dy = zip(*zip(self.x, self.y, self.dy))
                    self.dx = [float(0) for i in self.x]
                    self.hasData = True
                elif use_cols[3] == False:
                    self.x, self.y, self.dx = np.loadtxt(filename, usecols=cols, unpack=True)
                    self.x, self.y, self.dx = zip(*zip(self.x, self.y, self.dx))
                    self.dy = [float(0) for i in self.x]
                    self.hasData = True
            elif len(cols) == 2:
                self.x, self.y = np.loadtxt(filename, usecols=cols, unpack=True)
                self.x, self.y = zip(*zip(self.x, self.y))
                self.dx = [float(0) for i in self.x]
                self.dy = self.dx
                self.hasData = True


    def setFuncString(self, string):
        self.func_string = string

    def setData(self, x, y, dx = float(0), dy = float(0)):
        self.x = x
        self.y = y
        if not isinstance(dx, list):
            self.dx = [dx]*len(self.x)
        else:
            self.dx = dx
        if not isinstance(dy, list):
            self.dy = [dy]*len(self.x)
        else:
            self.dy = dy
        self.hasData = True


    def setDelimiter(self, value):
        try:
            self.delimiter = self.delimDict[value]
        except:
            self.delimiter = self.delimDict[0]


    def saveData(self, filename, delimiter='\t'):
        self.filename = filename
        self.hasFilename = True
        self.delimiter = delimiter
        if self.hasData:
            with open(self.filename, "w", newline='') as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                writer.writerow(['#X', 'Y', 'DX', 'DY'])
                [writer.writerow([self.x[i], self.y[i], self.dx[i], self.dy[i]]) for i in range(len(self.x))]
            f.close()
        else:
            pass

    def getFuncString(self):
        return self.func_string

    def getFilename(self):
        return self.filename

    def getData(self):
        return self.x, self.y, self.dx, self.dy



class linFit():
    
    def __init__(self, x, y, dx=None, dy=None):
        self.x = x
        self.y = y
        if not dy:
            self.n = min(len(self.x), len(self.y))
            self.dx = [0.0] * self.n
            self.dy = self.dx
        else:
            self.dx = dx
            self.dy = dy
            self.n = min(len(self.x), len(self.y), len(self.dx), len(self.dy))
        self.is_truncated = self._check_truncation()
        self.is_simple = self._check_simple(self.dy)
        self._covar_matrix = np.cov(self.x, self.y)
        self.SSxx = self._covar_matrix.item(0)
        self.SSxy = self._covar_matrix.item(1)
        self.SSyy = self._covar_matrix.item(3)
        self.coef_correlation = None
        self.slope = None
        self.intercept = None
        self.slope_uncertainty = None
        self.intercept_uncertainty = None
        self.root = None
        self.root_uncertainty = None


#These are meant to be private - "We're all consenting adults here"

    def _check_truncation(self):
        if len(self.x) != self.n:
            del self.x[self.n:]
            truncated = True
        elif len(self.y) != self.n:
            del self.y[self.n:]
            truncated = True
        elif len(self.dx) != self.n:
            del self.dx[self.n:]
            truncated = True
        elif len(self.dy) != self.n:
            del self.dy[self.n:]
            truncated = True
        else:
            truncated = False
        return truncated


    def _check_simple(self, myDY):
        simple = False
        for each_item in myDY:
            if each_item == 0:
                simple = True
        return simple


    def _get_mean(self, myList):
        return float(sum(myList) / len(myList))


    #Returns 2x2 np array. Get covariances by result.item(index)
    #Index is counted from left to right, top to bottom
    #SSxx = 0
    #SSxy = 1
    #SSyy = 3
    def _get_covariance(self, x, y, xbar, ybar):
        return np.cov(x, y)


    def _sum1(self, sig, x=1.0):
        if x == 1.0:
            x = [1.0] * self.n
        sumnum = 0.0
        for i in range(0,self.n):
            sumnum += (x[i] / sig[i] / sig[i])
        return sumnum


    def _sum2(self, x, y, sig):
        sumnum = 0.0
        for i in range(0,self.n):
            sumnum += (x[i] * y[i] / sig[i] / sig[i])
        return sumnum        


    def _sum3(self, x):
        sumnum = 0.0
        for i in range(0,self.n):
            sumnum += (x[i] * x[i])
        return sumnum

#Yeah, go crazy! These are what I made this class for

    def get_slope(self):
        if self.is_simple:
            if self.slope:
                return self.slope
            else:
                self.simpleLinFit()
                return self.slope
        else:
            if self.slope:
                return self.slope
            else:
                self.fullLinFit()
                return self.slope


    def get_intercept(self):
        if self.is_simple:
            if self.intercept:
                return self.intercept
            else:
                self.simpleLinFit()
                return self.intercept
        else:
            if self.intercept:
                return self.intercept
            else:
                self.fullLinFit()
                return self.intercept


    def get_slope_uncertainty(self):
        if self.is_simple:
            if self.slope_uncertainty:
                return self.slope_uncertainty
            else:
                self.simpleLinFit()
                return self.slope_uncertainty
        else:
            if self.slope_uncertainty:
                return self.slope_uncertainty
            else:
                self.fullLinFit()
                return self.slope_intercept


    def get_intercept_uncertainty(self):
        if self.is_simple:
            if self.intercept_uncertainty:
                return self.intercept_uncertainty
            else:
                self.simpleLinFit()
                return self.intercept_uncertainty
        else:
            if self.intercept_uncertainty:
                return self.intercept_uncertainty
            else:
                self.fullLinFit()
                return self.intercept_uncertainty


    def get_root(self):
        if self.is_simple:
            if self.root:
                return self.root
            else:
                self.simpleLinFit()
                return self.root
        else:
            if self.root:
                return self.root
            else:
                self.fullLinFit()
                return self.root


    def get_root_uncertainty(self):
        if self.is_simple:
            if self.root_uncertainty:
                return self.root_uncertainty
            else:
                self.simpleLinFit()
                return self.root_uncertainty
        else:
            if self.root_uncertainty:
                return self.root_uncertainty
            else:
                self.fullLinFit()
                return self.root_uncertainty


    def get_coef_correlation(self):
        if self.is_simple:
            if self.coef_correlation:
                return self.coef_correlation
            else:
                self.simpleLinFit()
                return self.coef_correlation
        else:
            self.coef_correlation = self.SSxy / (np.sqrt(self.SSxx) * np.sqrt(self.SSyy))
            return self.coef_correlation


    def simpleLinFit(self):
        Sx = sum(self.x)
        Sy = sum(self.y)
        Sxy = sum([a * b for a, b in zip(self.x, self.y)])
        Sxx = sum([a * b for a, b in zip(self.x, self.x)])
        Syy = sum([a * b for a, b in zip(self.y, self.y)])
        
        self.slope = (self.n * Sxy - Sx * Sy) / (self.n * Sxx - Sx**2)
        self.intercept = (Sy / self.n) - (self.slope * Sx / self.n)
        se = np.sqrt(((self.n * Syy) - (Sy**2) - (self.slope**2 * 
                                                            ((self.n * Sxx) - Sx**2))) / (self.n * (self.n - 2)))
        self.slope_uncertainty = np.sqrt((self.n * se) / ((self.n * Sxx) - (Sx**2)))
        self.intercept_uncertainty = np.sqrt(self.slope_uncertainty**2 * Sxx / self.n)
        self.coef_correlation = ((self.n * Sxy - Sx * Sy) / 
                                 (np.sqrt((self.n * Sxx - Sx**2) * (self.n * Syy - Sy**2))))
        self.root = -1 * self.intercept / self.slope
        self.root_uncertainty = np.sqrt((self.intercept_uncertainty**2 / self.slope**2) + 
                                        (self.intercept**2 * self.slope_uncertainty**2 / self.slope**4))


    def fullLinFit(self):
        #preliminary assumption that uncertainty only due to y
        sig = self.dy
        #some temporary constants will be needed
        AA = self._sum1(sig, self.x)
        BB = self._sum1(sig)
        CC = self._sum1(sig, self.y)
        DD = self._sum2(self.x, self.x, sig)
        EE = self._sum2(self.x, self.y, sig)
        FF = self._sum2(self.y, self.y, sig)
        #estimate slope to map dx --> dy
        m = (EE * BB - CC * AA)/(DD * BB - AA * AA)
        #map dx --> dy
        for i in range(0,self.n):
            sig[i] = np.sqrt(sig[i]**2 + m * self.dx[i]**2)
        #make final pass with new estimation of uncertainty embedded in dy
        AA = self._sum1(sig, self.x)
        BB = self._sum1(sig)
        CC = self._sum1(sig, self.y)
        DD = self._sum2(self.x, self.x, sig)
        EE = self._sum2(self.x, self.y, sig)
        FF = self._sum2(self.y, self.y, sig)
        self.slope = (EE * BB - CC * AA)/(DD * BB - AA * AA)
        self.intercept = (DD * CC - EE * AA)/(DD * BB - AA * AA)
        self.slope_uncertainty = np.sqrt(BB / (DD * BB - AA * AA))
        self.intercept_uncertainty = np.sqrt(DD / (DD * BB - AA * AA))
        self.root = -1 * self.intercept / self.slope
        self.root_uncertainty = np.sqrt((self.intercept_uncertainty**2 / self.slope**2) + 
                                        (self.intercept**2 * self.slope_uncertainty**2 / self.slope**4))






class functionType():
    
    def __init__(self, funcStr, xlo=0.0, xhi=10.0, res=100):
        
        self.x = []
        self.y = []
        self.xlo = xlo
        self.xhi = xhi
        self.res = res
        self.funcStr = funcStr
        self.x = np.linspace(self.xlo, self.xhi, self.res)
        self.safe_dict = {'np':np,
                          'sin':np.sin,
                          'cos':np.cos,
                          'tan':np.tan,
                          'arcsin':np.arcsin,
                          'arccos':np.arccos,
                          'arctan':np.arctan,
                          'sinh':np.sinh,
                          'cosh':np.cosh,
                          'tanh':np.tanh,
                          'arcsinh':np.arcsinh,
                          'arccosh':np.arccosh,
                          'arctanh':np.arctanh,
                          'ln':np.log,
                          'log10':np.log10,
                          'log2':np.log2,
                          'exp':np.exp,
                          'sqrt':np.sqrt,
                          'abs':np.fabs,
                          'sinc':np.sinc,
                          'x':self.x}


        self.y = eval(self.funcStr,{'__builtins__':None},self.safe_dict)
        if not isinstance(self.y, np.ndarray):
            self.y = np.repeat(self.y, len(self.x))

    def _reMakeData(self):
        
        self.x = np.linspace(self.xlo, self.xhi, self.res)
        self.safe_dict['x'] = self.x
        self.y = eval(self.funcStr,{'__builtins__':None},self.safe_dict)
        if not isinstance(self.y, np.ndarray):
            self.y = np.repeat(self.y, len(self.x))

    def setXLow(self, value):
        self.xlo = value
        self._reMakeData()

    def setXHigh(self, value):
        self.xhi = value
        self._reMakeData()

    def setRes(self, value):
        self.res = value
        self._reMakeData()

    def getXLow(self):
        return self.xlo

    def getXHigh(self):
        return self.xhi

    def getRes(self):
        return self.res

    def getData(self):
        return self.x, self.y



#create new class that inherits methods from super-class
class linFitApp(Gtk.Window):

    def __init__(self):


        #need to call init method of super-class
        Gtk.Window.__init__(self, title='DigGRR: Linear Regression and Plotting')
        #set the initial window to open at center of screen
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(400, 100)
        self.set_border_width(5)
        self.set_icon_from_file(programInstallDirectory + "/assets/logo.png")
        self.dataSetList = []


        self.mainBox = Gtk.Box()
        self.rightVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.noteBook = Gtk.Notebook()
        self.scrollTableWindow = Gtk.ScrolledWindow()
        self.scrollDataSetsWindow = Gtk.ScrolledWindow()
        self.scrollDataSetsWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrollTableWindowVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.scrollTableWindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        #self.scrollTableWindow.set_min_content_height(300)
        self.pageBox1 = Gtk.Box()
        self.pageBox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.pageBox3 = Gtk.Box()
        self.pageBox4 = Gtk.Box()
        self.plotButtonBox = Gtk.Box()
        self.plotFrame = Gtk.Frame()
        self.plotScrolledWindow = Gtk.ScrolledWindow()
        self.plotScrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.plotScrolledWindow.set_min_content_height(450)
        self.plotScrolledWindow.set_min_content_width(650)
        self.plotScrolledWindow.connect("button_press_event", self.onCanvasRightClick)
        self.rightVBox.pack_start(self.plotScrolledWindow, True, True, 5)
        self.rightVBox.pack_start(self.noteBook, False, True, 5)
        self.rightVBox.pack_end(self.plotButtonBox, False, False, 0)
        self.noteBook.append_page(self.pageBox2, Gtk.Label('Data Sets'))
        self.noteBook.append_page(self.pageBox1, Gtk.Label('Graph Options'))
        self.noteBook.append_page(self.pageBox3, Gtk.Label('Label Options'))
        self.noteBook.append_page(self.pageBox4, Gtk.Label('Save/Print'))
        self.scrollTableWindowVBox.pack_start(self.scrollTableWindow, True, True, 0)
        self.mainBox.pack_start(self.scrollTableWindowVBox, False, False, 0)
        self.mainBox.pack_start(self.rightVBox, True, True, 0)
        self.add(self.mainBox)


        ############################################################################

        #make toolbutton image widgets
        self.path1 = os.path.abspath(programInstallDirectory + "/assets/import2.png")
        self.path2 = os.path.abspath(programInstallDirectory + "/assets/function.png")
        self.path3 = os.path.abspath(programInstallDirectory + "/assets/import_table38x38.png")
        self.path4 = os.path.abspath(programInstallDirectory + "/assets/export2.png")
        self.path5 = os.path.abspath(programInstallDirectory + "/assets/regress.png")
        self.path6 = os.path.abspath(programInstallDirectory + "/assets/add.png")
        self.path7 = os.path.abspath(programInstallDirectory + "/assets/remove.png")
        self.path8 = os.path.abspath(programInstallDirectory + "/assets/clear.png")
        self.path9 = os.path.abspath(programInstallDirectory + "/assets/plot.png")
        self.path10 = os.path.abspath(programInstallDirectory + "/assets/save53x38.png")
        self.path11 = os.path.abspath(programInstallDirectory + "/assets/print53x38.png")
        self.path12 = os.path.abspath(programInstallDirectory + "/assets/about38x38.png")
        self.path13 = os.path.abspath(programInstallDirectory + "/assets/export_to_table38x38.png")
        self.path14 = os.path.abspath(programInstallDirectory + "/assets/loadstate53x38.png")
        self.path15 = os.path.abspath(programInstallDirectory + "/assets/select38x38.png")

        self.importDataImage = Gtk.Image.new_from_file(self.path1)
        self.makeFunctionImage = Gtk.Image.new_from_file(self.path2)
        self.tableDataImage = Gtk.Image.new_from_file(self.path3)
        self.tableExportDataImage = Gtk.Image.new_from_file(self.path13)
        self.exportDataImage = Gtk.Image.new_from_file(self.path4)
        self.viewRegressionImage = Gtk.Image.new_from_file(self.path5)
        self.addImage = Gtk.Image.new_from_file(self.path6)
        self.removeSetImage = Gtk.Image.new_from_file(self.path7)
        self.removeImage = Gtk.Image.new_from_file(self.path7)
        self.clearImage = Gtk.Image.new_from_file(self.path8)
        self.plotImage = Gtk.Image.new_from_file(self.path9)
        self.saveImage1 = Gtk.Image.new_from_file(self.path10)
        self.saveImage2 = Gtk.Image.new_from_file(self.path10)
        self.printImage = Gtk.Image.new_from_file(self.path11)
        self.aboutImage = Gtk.Image.new_from_file(self.path12)
        self.loadStateImage = Gtk.Image.new_from_file(self.path14)
        self.selectImage = Gtk.Image.new_from_file(self.path15)

        self.logoPixBuf = GdkPixbuf.Pixbuf.new_from_file(os.path.abspath(programInstallDirectory + \
                                                                          "/assets/logo.png"))


        ############################################################################


        #make a menu for right clicking the data set list items
        self.dataSetMenu = Gtk.Menu()
        self.dataSetMenuItem1 = Gtk.MenuItem('Remove from list')
        self.dataSetMenuItem1.connect("activate", self.onDSMenuItem1Clicked)
        self.dataSetMenuItem2 = Gtk.MenuItem('Move to table')
        self.dataSetMenuItem2.connect("activate", self.onDSMenuItem2Clicked)
        self.dataSetMenu.attach(self.dataSetMenuItem1, 0, 1, 0, 1)
        self.dataSetMenu.attach(self.dataSetMenuItem2, 0, 1, 1, 2)


        #make a menu for right clicking the canvas to print
        self.canvasMenu = Gtk.Menu()
        self.canvasMenuItem1 = Gtk.MenuItem("Print figure")
        self.canvasMenuItem1.connect("activate", self.onPrintPlotClicked)
        self.canvasMenuItem2 = Gtk.MenuItem("Save figure")
        self.canvasMenuItem2.connect("activate", self.onSavePlotClicked)
        self.canvasMenu.attach(self.canvasMenuItem1, 0, 1, 0, 1)
        self.canvasMenu.attach(self.canvasMenuItem2, 0, 1, 1, 2)
        self.canvasMenuItem2 = Gtk.MenuItem("Show graph options")
        self.canvasMenuItem2.connect("activate", self.showGraphOptions)
        self.canvasMenu.attach(self.canvasMenuItem2, 0, 1, 2, 3)
        self.canvasMenuItem3 = Gtk.MenuItem("Show label options")
        self.canvasMenuItem3.connect("activate", self.showLabelOptions)
        self.canvasMenu.attach(self.canvasMenuItem3, 0, 1, 3, 4)

        #make a menu for right clicking the table to delete rows
        self.tableMenu = Gtk.Menu()
        self.tableMenuItem1 = Gtk.MenuItem("Delete row")
        self.tableMenuItem1.connect("activate", self.onTableDeleteRowClicked)
        self.tableMenu.attach(self.tableMenuItem1, 0, 1, 0, 1)


        ############################################################################

        #Now to set up the data table
        self.dataTableListStore = Gtk.ListStore(float, float, float, float)
        self.dataTableTreeView = Gtk.TreeView(model=self.dataTableListStore)
        self.dataTableTreeView.set_grid_lines(3)
        self.dataTableTreeView.props.hover_selection = False
        self.dataTableTreeView.props.activate_on_single_click = True
        self.dataTableTreeView.connect("key-release-event", self.onTreeNavigateKeyPress)
        self.dataTableTreeView.connect("button_press_event", self.onTableTreeMouseClick)
        
        #set up the x column
        self.xColumnTextRenderer = Gtk.CellRendererText()
        self.xColumnTextRenderer.set_property("editable", True)
        self.xColumnTextRenderer.connect("edited", self.onXChanged)
        self.xColumnTreeView = Gtk.TreeViewColumn("x", self.xColumnTextRenderer, text=0)
        self.xColumnTreeView.set_min_width(90)
        self.xColumnTreeView.set_max_width(110)
        self.xColumnTreeView.set_alignment(0.5)
        
        #set up the y column
        self.yColumnTextRenderer = Gtk.CellRendererText()
        self.yColumnTextRenderer.set_property("editable", True)
        self.yColumnTextRenderer.connect("edited",self.onYChanged)
        self.yColumnTreeView = Gtk.TreeViewColumn("y", self.yColumnTextRenderer, text=1)
        self.yColumnTreeView.set_min_width(90)
        self.yColumnTreeView.set_max_width(110)
        self.yColumnTreeView.set_alignment(0.5)

        #set up the dx column
        self.dxColumnTextRenderer = Gtk.CellRendererText()
        self.dxColumnTextRenderer.set_property("editable", True)
        self.dxColumnTextRenderer.connect("edited",self.onDxChanged)
        self.dxColumnTreeView = Gtk.TreeViewColumn("dx", self.dxColumnTextRenderer, text=2)
        self.dxColumnTreeView.set_min_width(90)
        self.dxColumnTreeView.set_max_width(110)
        self.dxColumnTreeView.set_alignment(0.5)

        #set up the dy column
        self.dyColumnTextRenderer = Gtk.CellRendererText()
        self.dyColumnTextRenderer.set_property("editable", True)
        self.dyColumnTextRenderer.connect("edited",self.onDyChanged)
        self.dyColumnTreeView = Gtk.TreeViewColumn("dy", self.dyColumnTextRenderer, text=3)
        self.dyColumnTreeView.set_min_width(90)
        self.dyColumnTreeView.set_max_width(110)
        self.dyColumnTreeView.set_alignment(0.5)

        self.dataTableTreeView.append_column(self.xColumnTreeView)
        self.dataTableTreeView.append_column(self.yColumnTreeView)
        self.dataTableTreeView.append_column(self.dxColumnTreeView)
        self.dataTableTreeView.append_column(self.dyColumnTreeView)
        self.scrollTableWindow.add(self.dataTableTreeView)

        #REMOVE THESE DATA ENTRIES FOR DISTRIBUTION
        #THEY'RE ONLY HERE FOR TESTING
        self.dataTableListStore.append([0, 4, 0, 0])
        self.dataTableListStore.append([5, 8.2, 0, 0])
        self.dataTableListStore.append([10, 11.7, 0, 0])
        self.dataTableListStore.append([15, 16.5, 0, 0])
        self.dataTableListStore.append([20, 19, 0, 0])
        self.dataTableListStore.append([25, 24.5, 0, 0])
        self.dataTableListStore.append([30, 26.2, 0, 0])

        ############################################################################

        self.tableToolbar = Gtk.Toolbar()
        #make toolbuttons
        self.addToolButton = Gtk.ToolButton.new(self.addImage)
        self.addToolButton.set_tooltip_text('Add row')
        self.removeToolButton = Gtk.ToolButton.new(self.removeImage)
        self.removeToolButton.set_tooltip_text('Remove row')
        self.clearToolButton = Gtk.ToolButton.new(self.clearImage)
        self.clearToolButton.set_tooltip_text('Clear table')
        self.aboutToolButton = Gtk.ToolButton.new(self.aboutImage)
        self.aboutToolButton.connect("clicked", self.onAboutButtonClicked)
        self.aboutToolButton.set_tooltip_text('About')
        #add toolbuttons to toolbar
        self.tableToolbar.insert(self.addToolButton, 0)
        self.tableToolbar.insert(self.removeToolButton, 1)
        self.tableToolbar.insert(self.clearToolButton, 2)
        self.tableToolbar.insert(self.aboutToolButton, 3)
        #connect table tool buttons
        self.addToolButton.connect("clicked", self.tableAddRow)
        self.removeToolButton.connect("clicked", self.tableRemoveRow)
        self.clearToolButton.connect("clicked", self.clearTable)

        ############################################################################
        
        self.listStoreDataSets = Gtk.ListStore(str, str, str, str, bool)
        self.treeViewDataSets = Gtk.TreeView(model=self.listStoreDataSets)
        self.treeViewDataSets.set_property("activate-on-single-click", True)
        self.treeViewDataSets.set_property("hover-selection", True)
        self.listStoreDataSets.connect("row-inserted", self.onDataSetRowInserted)
        self.listStoreDataSets.connect("row-deleted", self.onDataSetRowDeleted)
        self.listStoreDataSets.connect("row-changed", self.onDataSetRowChanged)

        ###############################################################################

        self.cellRendererIncludeSet = Gtk.CellRendererToggle()
        self.cellRendererIncludeSet.connect("toggled", self.onIncludeSetToggled)
        self.columnIncludeSet = Gtk.TreeViewColumn("Include Set", self.cellRendererIncludeSet, active=4)
        self.columnIncludeSet.set_property("min-width", 128)
        self.columnIncludeSet.set_property("max-width", 128)
        self.treeViewDataSets.append_column(self.columnIncludeSet)

        ############################################################################

        self.cellRendererType = Gtk.CellRendererText()
        self.cellRendererType.set_property("height", 15)
        self.cellRendererType.set_property("editable", False)
        self.columnType = Gtk.TreeViewColumn("Type", self.cellRendererType, text=0)
        self.columnType.set_property("resizable", True)
        self.columnType.set_property("min-width", 64)
        self.columnType.set_property("max-width", 128)
        self.treeViewDataSets.append_column(self.columnType)

        ############################################################################

        self.cellRendererFilename = Gtk.CellRendererText()
        self.cellRendererFilename.set_property("height", 15)
        self.cellRendererFilename.set_property("editable", True)
        self.cellRendererFilename.connect("edited",self.onFilenameChanged)
        self.columnFilename = Gtk.TreeViewColumn("Filename", self.cellRendererFilename, text=1)
        self.columnFilename.set_property("resizable", True)
        self.columnFilename.set_property("min-width", 64)
        self.columnFilename.set_property("max-width", 128)
        self.treeViewDataSets.append_column(self.columnFilename)

        #####################################################################

        self.listStorePlotTypes = Gtk.ListStore(str)
        self.listPlotTypes = ["lines", "scatter", "error bars"]
        for item in self.listPlotTypes:
            self.listStorePlotTypes.append([item])
        self.cellRendererStyle = Gtk.CellRendererCombo()
        self.cellRendererStyle.set_property("editable", True)
        self.cellRendererStyle.set_property("model", self.listStorePlotTypes)
        self.cellRendererStyle.set_property("text-column", 0)
        self.cellRendererStyle.set_property("has-entry", False)
        self.cellRendererStyle.connect("edited", self.onStyleChanged)
        self.columnStyle = Gtk.TreeViewColumn("Line Style", self.cellRendererStyle, text=2)
        self.columnStyle.set_property("resizable", True)
        self.columnStyle.set_property("min-width", 128)
        self.columnStyle.set_property("max-width", 128)
        self.treeViewDataSets.append_column(self.columnStyle)

        #####################################################################

        self.listStoreColors = Gtk.ListStore(str)
        self.listColors = ["red", "orange", "green", "cyan", "blue", "purple", "black"]
        for item in self.listColors:
            self.listStoreColors.append([item])
        self.cellRendererColor = Gtk.CellRendererCombo()
        self.cellRendererColor.set_property("editable", True)
        self.cellRendererColor.set_property("model", self.listStoreColors)
        self.cellRendererColor.set_property("text-column", 0)
        self.cellRendererColor.set_property("has-entry", False)
        self.cellRendererColor.connect("edited", self.onColorChanged)
        self.columnColor = Gtk.TreeViewColumn("Line Color", self.cellRendererColor, text=3)
        self.columnColor.set_property("resizable", True)
        self.columnColor.set_property("min-width", 64)
        self.columnColor.set_property("max-width", 128)
        self.treeViewDataSets.append_column(self.columnColor)

        #######################################################################

        self.dataSetToolbar = Gtk.Toolbar()
        self.dataSetToolbar2 = Gtk.Toolbar()
        self.dataSetToolbarHBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dataSetToolbarHBox.pack_start(self.dataSetToolbar, False, False, 0)
        #self.dataSetToolbarHBox.pack_end(self.dataSetToolbar2, False, False, 0)
        #make toolbuttons
        self.importDataToolButton = Gtk.ToolButton.new(self.importDataImage)
        self.importDataToolButton.set_tooltip_text('Import data from file')
        self.importDataToolButton.connect("clicked", self.onImportFromFileClicked)
        self.makeFunctionToolButton = Gtk.ToolButton.new(self.makeFunctionImage)
        self.makeFunctionToolButton.connect("clicked", self.onNewFunctionClicked)
        self.makeFunctionToolButton.set_tooltip_text('Define function for plotting')
        self.tableDataToolButton = Gtk.ToolButton.new(self.tableDataImage)
        self.tableDataToolButton.set_tooltip_text('Import data from table')
        self.tableDataToolButton.connect("clicked", self.onImportFromTableClicked)
        self.tableExportDataToolButton = Gtk.ToolButton.new(self.tableExportDataImage)
        self.tableExportDataToolButton.set_tooltip_text('Export selected data set to table')
        self.tableExportDataToolButton.connect("clicked", self.onExportToTableClicked)
        self.viewRegressionToolButton = Gtk.ToolButton.new(self.viewRegressionImage)
        self.viewRegressionToolButton.connect("clicked", self.onLineFitClicked)
        self.viewRegressionToolButton.set_tooltip_text('Perform linear regression on selected data set')
        self.removeSetToolButton = Gtk.ToolButton.new(self.removeSetImage)
        self.removeSetToolButton.set_tooltip_text('Remove selected data set(s) from list')
        self.removeSetToolButton.connect("clicked", self.onRemoveDataSetClicked)
        self.selectToolButton = Gtk.ToolButton.new(self.selectImage)
        self.selectToolButton.set_tooltip_text('Select/deselect all data sets')
        self.selectToolButton.connect("clicked", self.onSelectAllClicked)
        self.plotToolButton = Gtk.ToolButton.new(self.plotImage)
        self.plotToolButton.set_tooltip_text('Refresh the plot')
        self.plotToolButton.connect("clicked", self.onRefreshPlotClicked)
        self.loadStateToolButton = Gtk.ToolButton.new(self.loadStateImage)
        self.loadStateToolButton.set_tooltip_text('Load a previously saved state')
        self.loadStateToolButton.connect("clicked", self.onLoadStateClicked)
        #add toolbuttons to toolbars
        self.dataSetToolbar.insert(self.selectToolButton, 0)
        self.dataSetToolbar.insert(self.importDataToolButton, 1)
        self.dataSetToolbar.insert(self.makeFunctionToolButton, 2)
        self.dataSetToolbar.insert(self.tableDataToolButton, 3)
        self.dataSetToolbar.insert(self.tableExportDataToolButton, 4)
        #self.dataSetToolbar.insert(self.exportDataToolButton, 3) #removed, function moved to new save/print tab
        self.dataSetToolbar.insert(self.viewRegressionToolButton, 5)
        self.dataSetToolbar.insert(self.removeSetToolButton, 6)

        self.dataSetToolbar2.insert(self.loadStateToolButton, 0)
        self.dataSetToolbar2.insert(self.plotToolButton, 1)

        ########################################################################

        self.plotButtonBox.pack_end(self.dataSetToolbar2, False, False, 0)

        ########################################################################
        
        self.treeViewDataSets.set_vscroll_policy(0)
        self.treeViewDataSets.connect("button_press_event", self.onDataSetsTreeMouseClick)
        self.scrollTableWindowVBox.pack_end(self.tableToolbar, False, False, 0)
        self.scrollDataSetsWindow.add(self.treeViewDataSets)
        self.scrollDataSetsWindow.set_size_request(400,100)
        self.pageBox2.pack_start(self.scrollDataSetsWindow, True, True, 0)
        self.pageBox2.pack_end(self.dataSetToolbarHBox, False, False, 0)
        
        ##########################################################################

        self.labelOptionGrid = Gtk.Grid()

        self.titleLabel = Gtk.Label('Title')
        self.xLabelLabel = Gtk.Label('x-label')
        self.yLabelLabel = Gtk.Label('y-label')
        self.xUnitsLabel = Gtk.Label('x-units')
        self.yUnitsLabel = Gtk.Label('y-units')
        self.institutionLabel = Gtk.Label('Institution')
        self.authorLabel = Gtk.Label('Author')
        self.legendLabel = Gtk.Label('Legend')
        self.metaDataLabel = Gtk.Label('Metadata')
        self.tickLabelLabel = Gtk.Label('Tick Labels')
        self.titleSizeLabel = Gtk.Label('Title Size')
        self.labelSizeLabel = Gtk.Label('Label Size')
        self.textSizeLabel = Gtk.Label('Text Size')

        self.titleEntry = Gtk.Entry()
        self.xLabelEntry = Gtk.Entry()
        self.yLabelEntry = Gtk.Entry()
        self.xUnitEntry = Gtk.Entry()
        self.yUnitEntry = Gtk.Entry()
        self.institutionEntry = Gtk.Entry()
        self.authorEntry = Gtk.Entry()

        self.legendToggle = Gtk.CheckButton()
        self.metaDataToggle = Gtk.CheckButton()
        self.tickLabelSizeComboBox = Gtk.ComboBoxText()
        self.tick_label_sizes = ['8', '10', '12', '14', '16', '18', '20', '22', '24', '26']
        self.listStoreTickLabelSizes = Gtk.ListStore(str)
        for item in self.tick_label_sizes:
            self.listStoreTickLabelSizes.append([item])
        self.tickLabelSizeComboBox.set_property("model", self.listStoreTickLabelSizes)
        self.tickLabelSizeComboBox.set_active(1)

        self.titleSizeComboBox = Gtk.ComboBoxText()
        self.font_sizes = ['8', '10', '12', '14', '16', '18', '20', '22', '24', '26']
        self.listStoreFontSizes = Gtk.ListStore(str)
        for item in self.font_sizes:
            self.listStoreFontSizes.append([item])
        self.titleSizeComboBox.set_property("model", self.listStoreFontSizes)
        self.titleSizeComboBox.set_active(7)
        self.labelSizeComboBox = Gtk.ComboBoxText()
        self.labelSizeComboBox.set_property("model", self.listStoreFontSizes)
        self.labelSizeComboBox.set_active(4)
        self.textSizeComboBox = Gtk.ComboBoxText()
        self.textSizeComboBox.set_property("model", self.listStoreFontSizes)
        self.textSizeComboBox.set_active(0)

        self.labelOptionGrid.attach(self.titleLabel, 0,0,2,1)
        self.labelOptionGrid.attach(self.xLabelLabel, 0,1,2,1 )
        self.labelOptionGrid.attach(self.yLabelLabel, 0,2,2,1)
        self.labelOptionGrid.attach(self.xUnitsLabel, 0,3,2,1)
        self.labelOptionGrid.attach(self.yUnitsLabel, 0,4,2,1)
        self.labelOptionGrid.attach(self.titleEntry, 2,0,2,1)
        self.labelOptionGrid.attach(self.xLabelEntry, 2,1,2,1)
        self.labelOptionGrid.attach(self.yLabelEntry, 2,2,2,1)
        self.labelOptionGrid.attach(self.xUnitEntry, 2,3,2,1)
        self.labelOptionGrid.attach(self.yUnitEntry, 2,4,2,1)
        self.labelOptionGrid.attach(self.titleSizeLabel, 4,0,2,1)
        self.labelOptionGrid.attach(self.labelSizeLabel, 4,1,2,1)
        self.labelOptionGrid.attach(self.textSizeLabel, 4,2,2,1)
        self.labelOptionGrid.attach(self.institutionLabel, 4,3,2,1)
        self.labelOptionGrid.attach(self.authorLabel, 4,4,2,1)
        self.labelOptionGrid.attach(self.titleSizeComboBox, 6,0,2,1)
        self.labelOptionGrid.attach(self.labelSizeComboBox, 6,1,2,1)
        self.labelOptionGrid.attach(self.textSizeComboBox, 6,2,2,1)
        self.labelOptionGrid.attach(self.institutionEntry, 6,3,4,1)
        self.labelOptionGrid.attach(self.authorEntry, 6,4,4,1)
        self.labelOptionGrid.attach(self.legendLabel, 8,2,2,1)
        self.labelOptionGrid.attach(self.metaDataLabel, 8,1,2,1)
        self.labelOptionGrid.attach(self.tickLabelLabel, 8,0,2,1)
        self.labelOptionGrid.attach(self.legendToggle, 10,2,2,1)
        self.labelOptionGrid.attach(self.metaDataToggle, 10,1,2,1)
        self.labelOptionGrid.attach(self.tickLabelSizeComboBox, 10,0,2,1)

        self.pageBox3.pack_start(self.labelOptionGrid, True, True, 0)

        ##########################################################################

        self.graphOptionsGrid = Gtk.Grid()
        self.pageBox1.pack_start(self.graphOptionsGrid, True, True, 0)

        self.leftFrame = Gtk.Frame.new('x-Range Options')
        self.rightFrame = Gtk.Frame.new('y-Range Options')
        self.bottomHBox = Gtk.Box()
        self.bottomFrame = Gtk.Frame.new('Other Options')
        self.bottomFrame.add(self.bottomHBox)
        self.leftFrameGrid = Gtk.Grid()
        self.rightFrameGrid = Gtk.Grid()

        self.xMinLabel = Gtk.Label('x-Min')
        self.xMaxLabel = Gtk.Label('x-Max')
        self.yMinLabel = Gtk.Label('y-Min')
        self.yMaxLabel = Gtk.Label('y-Max')
        self.autoXLabel = Gtk.Label('Auto x-Range')
        self.autoYLabel = Gtk.Label('Auto y-Range')
        self.xTicsLabel = Gtk.Label('x-Tics')
        self.yTicsLabel = Gtk.Label('y-Tics')
        self.legendLocLabel = Gtk.Label('Legend')

        self.xMinEntry = Gtk.Entry()
        self.xMinEntry.set_text('0.0')
        self.xMaxEntry = Gtk.Entry()
        self.xMaxEntry.set_text('10.0')
        self.yMinEntry = Gtk.Entry()
        self.yMinEntry.set_text('0.0')
        self.yMaxEntry = Gtk.Entry()
        self.yMaxEntry.set_text('10.0')
        self.autoXSwitch = Gtk.Switch()
        self.autoXSwitch.set_active(True)
        self.autoYSwitch = Gtk.Switch()
        self.autoYSwitch.set_active(True)
        self.xTicsSwitch = Gtk.Switch()
        self.xTicsSwitch.set_active(True)
        self.yTicsSwitch = Gtk.Switch()
        self.yTicsSwitch.set_active(True)
        self.legendLocComboBox = Gtk.ComboBoxText()
        self.legendLocListStore = Gtk.ListStore(str)
        self.legendLocList = ['upper right', 'upper left',
                              'lower right', 'lower left', 
                              'center left', 'center right', 
                              'lower center', 'upper center', 
                              'center']
        for item in self.legendLocList:
            self.legendLocListStore.append([item])
        self.legendLocComboBox.set_property("model", self.legendLocListStore)
        self.legendLocComboBox.set_active(0)

        self.plotGridLabel = Gtk.Label('Grid')
        self.plotGridCheckButton = Gtk.CheckButton()
        self.plotGridCheckButton.set_active(True)

        self.setFunctionSamplesLabel = Gtk.Label('Function Samples')
        self.setFunctionSamplesSpinButton = Gtk.SpinButton()
        self.setFunctionSamplesSpinButton.set_adjustment(Gtk.Adjustment.new(500,10,5000,10,100,0))
        self.setFunctionSamplesSpinButton.set_value(500)

        self.graphOptionsGrid.attach(self.leftFrame, 0,0,1,3)
        self.graphOptionsGrid.attach(self.rightFrame, 1,0,1,3)
        self.graphOptionsGrid.attach(self.bottomFrame, 0,3,2,1)

        self.leftFrame.add(self.leftFrameGrid)
        self.rightFrame.add(self.rightFrameGrid)

        self.leftFrameGrid.attach(self.xMinLabel, 0,0,1,1)
        self.leftFrameGrid.attach(self.xMaxLabel, 0,1,1,1)
        self.leftFrameGrid.attach(self.autoXLabel, 0,2,1,1)
        self.leftFrameGrid.attach(self.xTicsLabel, 0,3,1,1)
        self.leftFrameGrid.attach(self.xMinEntry, 1,0,1,1)
        self.leftFrameGrid.attach(self.xMaxEntry, 1,1,1,1)
        self.leftFrameGrid.attach(self.autoXSwitch, 1,2,1,1)
        self.leftFrameGrid.attach(self.xTicsSwitch, 1,3,1,1)

        self.rightFrameGrid.attach(self.yMinLabel, 0,0,1,1)
        self.rightFrameGrid.attach(self.yMaxLabel, 0,1,1,1)
        self.rightFrameGrid.attach(self.autoYLabel, 0,2,1,1)
        self.rightFrameGrid.attach(self.yTicsLabel, 0,3,1,1)
        self.rightFrameGrid.attach(self.yMinEntry, 1,0,1,1)
        self.rightFrameGrid.attach(self.yMaxEntry, 1,1,1,1)
        self.rightFrameGrid.attach(self.autoYSwitch, 1,2,1,1)
        self.rightFrameGrid.attach(self.yTicsSwitch, 1,3,1,1)

        self.bottomHBox.pack_start(self.plotGridLabel, True, True, 0)
        self.bottomHBox.pack_start(self.plotGridCheckButton, True, True, 0)
        self.bottomHBox.pack_start(self.legendLocLabel, True, True, 0)
        self.bottomHBox.pack_start(self.legendLocComboBox, True, True, 0)
        self.bottomHBox.pack_start(self.setFunctionSamplesLabel, True, True, 0)
        self.bottomHBox.pack_start(self.setFunctionSamplesSpinButton, True, True, 0)


        ##########################################################################



        self.saveDataOptionsFrame = Gtk.Frame.new('Data')
        self.pageBox4.pack_start(self.saveDataOptionsFrame, True, True, 5)
        self.saveDataOptionsGrid = Gtk.Grid()

        self.saveDataVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.saveDataOptionsFrame.add(self.saveDataVBox)
        self.saveDataToolbar = Gtk.Toolbar()
        self.saveDataToolButton = Gtk.ToolButton.new(self.saveImage2)
        self.saveDataToolButton.set_tooltip_text('Save data')
        self.saveDataToolbar.insert(self.saveDataToolButton, 0)

        self.saveDataModeLabel = Gtk.Label('Save mode')
        self.saveDataFileListLabel = Gtk.Label('File list')
        self.saveDataFileExtensionListLabel = Gtk.Label('Extension')
        self.saveDataDelimiterLabel = Gtk.Label('Delimiter')

        self.saveDataSelectComboBox = Gtk.ComboBoxText()
        self.saveDataSelectListStore = Gtk.ListStore(str)
        self.saveDataSelectList = ['save single', 'save all selected', 'save state']
        for item in self.saveDataSelectList:
            self.saveDataSelectListStore.append([item])
        self.saveDataSelectComboBox.set_property("model", self.saveDataSelectListStore)
        self.saveDataSelectComboBox.set_active(0)

        self.saveDataFileListComboBox = Gtk.ComboBoxText()
        self.saveDataFileListStore = Gtk.ListStore(str)
        self.saveDataFileList = []
        for item in self.saveDataFileList:
            self.saveDataFileListStore.append([item])
        self.saveDataFileListComboBox.set_property("model", self.saveDataFileListStore)
        self.saveDataFileListComboBox.set_active(0)

        self.saveDataFileExtensionComboBox = Gtk.ComboBoxText()
        self.saveDataFileExtensionListStore = Gtk.ListStore(str)
        self.saveDataFileExtensionList = ['dat', 'txt']
        for item in self.saveDataFileExtensionList:
            self.saveDataFileExtensionListStore.append([item])
        self.saveDataFileExtensionComboBox.set_property("model", self.saveDataFileExtensionListStore)
        self.saveDataFileExtensionComboBox.set_active(0)


        self.saveDataDelimiterComboBox = Gtk.ComboBoxText()
        self.saveDataDelimiterListStore = Gtk.ListStore(str)
        self.saveDataDelimiterList = ['tabs', 'commas', 'spaces']
        for item in self.saveDataDelimiterList:
            self.saveDataDelimiterListStore.append([item])
        self.saveDataDelimiterComboBox.set_property("model", self.saveDataDelimiterListStore)
        self.saveDataDelimiterComboBox.set_active(0)

        self.saveDataOptionsGrid.attach(self.saveDataModeLabel, 0,0,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataFileListLabel, 0,1,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataFileExtensionListLabel, 0,2,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataDelimiterLabel, 0,3,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataSelectComboBox, 1,0,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataFileListComboBox, 1,1,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataFileExtensionComboBox, 1,2,1,1)
        self.saveDataOptionsGrid.attach(self.saveDataDelimiterComboBox, 1,3,1,1)

        self.savePlotOptionsFrame = Gtk.Frame.new('Figure')
        self.pageBox4.pack_start(self.savePlotOptionsFrame, True, True, 5)
        self.savePlotOptionsGrid = Gtk.Grid()

        self.saveFigureVBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.savePlotOptionsFrame.add(self.saveFigureVBox)
        self.saveFigureToolbar = Gtk.Toolbar()
        self.saveFigureToolButton = Gtk.ToolButton.new(self.saveImage1)
        self.saveFigureToolButton.set_tooltip_text('Save figure')
        self.printFigureToolButton = Gtk.ToolButton.new(self.printImage)
        self.printFigureToolButton.set_tooltip_text('Print figure')
        self.saveFigureToolbar.insert(self.saveFigureToolButton, 0)
        self.saveFigureToolbar.insert(self.printFigureToolButton, 1)

        self.figureTransparentLabel = Gtk.Label('Transparent')
        self.figureTransparentCheckButton = Gtk.CheckButton()
        self.figureTransparentCheckButton.set_active(True)

        self.figureDPILabel = Gtk.Label('DPI')
        self.figureDPIEntry = Gtk.Entry()
        self.figureDPIEntry.set_text('200')

        self.figureExtensionLabel = Gtk.Label('Extension')
        self.figureExtensionComboBox = Gtk.ComboBoxText()
        self.figureExtensionListStore = Gtk.ListStore(str)
        self.figureExtensionList = ['pdf', 'png', 'ps', 'eps', 'svg', 'jpg', 'tiff']
        for item in self.figureExtensionList:
            self.figureExtensionListStore.append([item])
        self.figureExtensionComboBox.set_property("model", self.figureExtensionListStore)
        self.figureExtensionComboBox.set_active(0)

        self.savePlotOptionsGrid.attach(self.figureExtensionLabel, 0,0,1,1)
        self.savePlotOptionsGrid.attach(self.figureExtensionComboBox, 1,0,1,1)
        self.savePlotOptionsGrid.attach(self.figureDPILabel, 0,1,1,1)
        self.savePlotOptionsGrid.attach(self.figureDPIEntry, 1,1,1,1)
        self.savePlotOptionsGrid.attach(self.figureTransparentLabel, 0,2,1,1)
        self.savePlotOptionsGrid.attach(self.figureTransparentCheckButton, 1,2,1,1)

        self.printFigureToolButton.connect("clicked", self.onPrintPlotClicked)
        self.saveFigureToolButton.connect("clicked", self.onSavePlotClicked)
        self.saveDataToolButton.connect("clicked", self.onSaveDataClicked)


        self.saveFigureVBox.pack_start(self.savePlotOptionsGrid, True, True, 5)
        self.saveFigureVBox.pack_start(self.saveFigureToolbar, True, True, 5)
        self.saveDataVBox.pack_start(self.saveDataOptionsGrid, True, True, 5)
        self.saveDataVBox.pack_start(self.saveDataToolbar, True, True, 5)


        ##########################################################################






        ##########################################################################

        #Setting up the figure and adding it to the layout
        self.fig = Figure(figsize=(10,6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(650, 450)
        self.fig.patch.set_facecolor('#eeeeee')
        self.plotScrolledWindow.add_with_viewport(self.canvas)

        ##########################################################################

        self.saveDataSelectComboBox.connect("changed", self.onSaveDataStatusToggled)


        
    ##########################################################################

    def onFilenameChanged(self, widget, path, text):
        self.listStoreDataSets[path][1] = text

    def onStyleChanged(self, widget, path, text):
        self.listStoreDataSets[path][2] = text

    def onColorChanged(self, widget, path, text):
        self.listStoreDataSets[path][3] = text

    def onIncludeSetToggled(self, widget, path):
        self.listStoreDataSets[path][4] = not self.listStoreDataSets[path][4]

    def onXChanged(self, widget, path, number):
        self.dataTableListStore[path][0]=float(number.replace(',', '.'))

    def onYChanged(self, widget, path, number):
        self.dataTableListStore[path][1]=float(number.replace(',', '.'))

    def onDxChanged(self, widget, path, number):
        self.dataTableListStore[path][2]=float(number.replace(',', '.'))

    def onDyChanged(self, widget, path, number):
        self.dataTableListStore[path][3]=float(number.replace(',', '.'))


        
    #addrow appends a row to liststore and updates the plot
    def tableAddRow(self, widget):
        self.dataTableListStore.append()


        
    #remove row queries which row is selected and removes it from liststore
    def tableRemoveRow(self, widget):
        select = self.dataTableTreeView.get_selection()
        self.model, self.treeiter = select.get_selected()
        if self.treeiter is not None:
            self.dataTableListStore.remove(self.treeiter)


            
    #clearTable wipes the liststore (table)
    def clearTable(self, widget):
        self.dataTableListStore.clear()

        
        
    def importFromTable(self):
        dataSet = dataManager()
        a = list([row[0] for row in self.dataTableListStore])
        b = list([row[1] for row in self.dataTableListStore])
        c = list([row[2] for row in self.dataTableListStore])
        d =  list([row[3] for row in self.dataTableListStore])
        dataSet.setData(a, b, c, d)
        self.dataSetList.append(dataSet)
        self.listStoreDataSets.append(["table data", "unnamed", "lines", "black", True])

        
    def onImportFromTableClicked(self, widget):
        self.importFromTable()


    def onExportToTableClicked(self,widget):
        num = 0
        for index, row in enumerate(self.listStoreDataSets):
            if row[4] == True:
                rownum = index
                num += 1
            if num > 1:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, "Whoopsie Daisy!")
                dialog.format_secondary_text("Look, I've only got one table so you'll have to select only one\ndata set to send to it. Alternatively, you can just right click the\ndata set you want and select the 'move to table' option. \n\nI don't want to tell you how to do your job or anything.\nI'm just saying it's an option.")
                image = Gtk.Image.new_from_file(programInstallDirectory + '/assets/logo50x.png')
                image.show()
                dialog.set_image(image)
                dialog.run()
                dialog.destroy()
                return None
        if num == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, "Whoopsie Daisy!")
            dialog.format_secondary_text("Yeeaahhh... I'm going to have to get you to go ahead and pick at least\none data set to send to the table. Alternatively, it would be great if\nyou could just go ahead and right click the data set you want and select\nthe 'move to table' option.\n\nI don't want to tell you how to do your job or anything. \nI'm just saying it's an option.")
            image = Gtk.Image.new_from_file(programInstallDirectory + '/assets/logo50x.png')
            image.show()
            dialog.set_image(image)
            dialog.run()
            dialog.destroy()
            return None
        else:
            x, y, dx, dy = self.dataSetList[rownum].getData()
            self.addToTable(x, y, dx, dy)


    def onDataSetRowInserted(self, widget, path, itr):
        lst = [row[1] for row in self.listStoreDataSets]
        self.saveDataFileListStore.clear()
        for item in lst:
            self.saveDataFileListStore.append([item])
        self.saveDataFileListComboBox.set_active(0)
        if len(lst) == 0:
            self.saveDataFileListComboBox.set_sensitive(False)



    def onDataSetRowDeleted(self, widget, path):
        lst = [row[1] for row in self.listStoreDataSets]
        self.saveDataFileListStore.clear()
        for item in lst:
            self.saveDataFileListStore.append([item])
        self.saveDataFileListComboBox.set_active(0)
        if len(lst) == 0:
            self.saveDataFileListComboBox.set_sensitive(False)


    def onDataSetRowChanged(self, widget, path, itr):
        lst = [row[1] for row in self.listStoreDataSets]
        self.saveDataFileListStore.clear()
        for item in lst:
            self.saveDataFileListStore.append([item])
        self.saveDataFileListComboBox.set_active(0)
        if len(lst) == 0:
            self.saveDataFileListComboBox.set_sensitive(False)        


        
    #define the callback for keypress events on the data table (x,y,dx,dy)
    def onTreeNavigateKeyPress(self, treeview, event):
        keyname = Gdk.keyval_name(event.keyval)
        path, col = treeview.get_cursor()
        columns = [c for c in treeview.get_columns()] 
        colnum = columns.index(col)
        
        if keyname == 'Tab' or keyname == 'Right':
            if colnum + 1 < len(columns):
                next_column = columns[colnum + 1]
            else: 
                next_column = columns[0]
            GLib.timeout_add(10,
                             treeview.set_cursor,
                             path, next_column, True)

        elif keyname == 'Left':
            if colnum == 0:
                next_column = columns[-1]
            else:
                next_column = columns[colnum - 1]
            GLib.timeout_add(10,
                             treeview.set_cursor,
                             path, next_column, True)            
            
        elif keyname == 'Return' or keyname == 'Down' or keyname == 'KP_Enter':
            model = treeview.get_model()
            if path.get_indices()[0] + 1 == len(model):
                path = treeview.get_path_at_pos(0,0)[0]
                GLib.timeout_add(10,
                             treeview.set_cursor,
                             path, columns[colnum], True)
            else:
                path.next()
                GLib.timeout_add(10,
                             treeview.set_cursor,
                             path, columns[colnum], True)

        elif keyname == 'Up':
            model = treeview.get_model()
            if path.get_indices()[0] != 0:
                path.prev()
                GLib.timeout_add(10,
                             treeview.set_cursor,
                             path, columns[colnum], True)
            else:
                GLib.timeout_add(10,
                             treeview.set_cursor,
                             model[-1].path, columns[colnum], True)
        else:
            pass

        

    def onNewFunctionClicked(self, widget):
        text = self.defineNewFunction()
        
        if (text != '') and (text != None):
            xmin, xmax, ymin, ymax = self.ax.axis()
            newFunctionDef = functionType(text, xmin, xmax, self.setFunctionSamplesSpinButton.get_value_as_int())
            x, y = newFunctionDef.getData()
            newFunction = dataManager()
            newFunction.setData(x,y)
            newFunction.setFuncString(text)
            self.dataSetList.append(newFunction)
            self.listStoreDataSets.append(["function", "unnamed", "lines", "blue", True])


            
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
        timeoutID = GLib.timeout_add(500, self.checkValidEntry)
        self.newFunctionDialog.show_all()

        response = self.newFunctionDialog.run()
        text = self.newFunctionDialogEntry.get_text()
        self.newFunctionDialog.destroy()
        if (response == -14) and (text != ''):
            GLib.source_remove(timeoutID)
            return text
        else:
            GLib.source_remove(timeoutID)
            return None

    def checkValidEntry(self):
        funcStr = self.newFunctionDialogEntry.get_text()
        try:
            temp = functionType(funcStr)
            self.newFunctionDialog.set_response_sensitive(-14, True)
        except:
            self.newFunctionDialog.set_response_sensitive(-14, False)
        return True


    
    def onImportFromFileClicked(self, widget):
        filename = self.importDataDialog(self)
        num_cols = self.get_data_cols(filename)
        col_list = self.select_which_cols_dialog(self, num_cols)
        if col_list:
            use_cols = tuple([True if i != None else False for i in col_list])
            cols = tuple([int(i) for i in col_list if i != None])
            dataSet = dataManager()
            dataSet.loadFromFile(filename, use_cols, cols)
            self.dataSetList.append(dataSet)
            self.listStoreDataSets.append(["data", "unnamed", "lines", "black", True])
        else:
            pass
        
        
    def importDataDialog(self, parent):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        message = "Imported data must be in two-column, tab-separated DAT or TXT file."
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



    def get_data_cols(self, filename):
        if filename.endswith('.csv'):
            f = np.loadtxt(filename, delimiter = ',', unpack=True)
        else:
            f = np.loadtxt(filename, unpack=True)
        num_cols = len(f)
        return num_cols


    def select_which_cols_dialog(self, parent, num_cols):
        # Returns user input as a list of column numbers (maximum 4) or None
        # If user does not input it returns None, NOT AN EMPTY list.
        message = "Selected file contains " + str(num_cols) + \
                  " columns of data. Please select up to 4 columns to import:"
        title = "Select Columns"
        dialogWindow = Gtk.MessageDialog(parent,
                                         Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                         Gtk.MessageType.OTHER,
                                         Gtk.ButtonsType.OK_CANCEL,
                                         message)
        dialogWindow.set_title(title)
        dialogBox = dialogWindow.get_content_area()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        headers = ['x', 'y', 'dx', 'dy']
        colComboBoxes = []
        cols = ['None'] + [str(i) for i in range(num_cols)]
        model = Gtk.ListStore(str)
        for item in cols:
            model.append([item])
        for col, header in enumerate(headers):
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            label = Gtk.Label(header)
            c = Gtk.ComboBoxText()
            c.set_property("model", model)
            c.set_active(0)
            colComboBoxes.append(c)
            vbox.pack_start(label,True, True,0)
            vbox.pack_start(c,True, True,0)
            hbox.pack_start(vbox, True, True, 5)
        
        dialogBox.pack_start(hbox, True, True, 5)
        dialogWindow.show_all()
        response = dialogWindow.run()
        col_list = [i.get_active_text() if i.get_active_text() != 'None' else None for i in colComboBoxes]
        dialogWindow.destroy()
        if (response == Gtk.ResponseType.OK) and (col_list[0] != None) and (col_list[1] != None):
            return col_list
        else:
            return None



    def saveFigureDialog(self, parent):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        message = ""
        title = "Save Figure"
        dialogWindow = Gtk.MessageDialog(parent,
                                         Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                         Gtk.MessageType.OTHER,
                                         Gtk.ButtonsType.OK_CANCEL,
                                         message)
        dialogWindow.set_title(title)
        dialogBox = dialogWindow.get_content_area()
        fileChooser = Gtk.FileChooserWidget()
        fileChooser.set_action(1)
        #fileFilter = Gtk.FileFilter()
        #fileFilter.add_mime_type("text/plain")
        #fileFilter.set_name("TXT/DAT")
        #fileChooser.add_filter(fileFilter)
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


    def showLabelOptions(self, widget):
        self.noteBook.set_current_page(2)


    def showGraphOptions(self, widget):
        self.noteBook.set_current_page(1)


    def onLineFitClicked(self, widget):
        for row in self.listStoreDataSets:
            length = len(self.dataSetList[row.path.get_indices()[0]].getData()[0])
            if row[4] == True and (row[0] == 'table data' or row[0] == 'data') and (length > 1):
                rownum = row.path.get_indices()[0]
                x, y, dx, dy = self.dataSetList[rownum].getData()

                try:
                    line = linFit(x, y, dx, dy)
                    m = line.get_slope()
                    b = line.get_intercept()
                    text = (str(m)+'*x+'+str(b)).strip()
                    xmin, xmax, ymin, ymax = self.ax.axis()
                    newFunctionDef = functionType(text, xmin, xmax, \
                                                  self.setFunctionSamplesSpinButton.get_value_as_int())
                    x, y = newFunctionDef.getData()
                    newFunction = dataManager()
                    newFunction.setData(x,y)
                    newFunction.setLinParam(m=line.get_slope(), 
                                            b=line.get_intercept(), 
                                            dm=line.get_slope_uncertainty(), 
                                            db=line.get_intercept_uncertainty(),
                                            root=line.get_root(),
                                            droot=line.get_root_uncertainty(),
                                            corr=line.get_coef_correlation())
                    newFunction.setFuncString(text)
                    self.dataSetList.append(newFunction)
                    self.listStoreDataSets.append(["linear model", row[1]+"-lin_regress", "lines", "red", True])
                except:
                    return None

    def onRemoveDataSetClicked(self, widget):
        for row in self.listStoreDataSets:
            if row[4] == True:
                rownum = row.path.get_indices()[0]
                del self.dataSetList[rownum]
                self.listStoreDataSets.remove(row.iter)


    def onSelectAllClicked(self, widget):
        check_all = False #if false, uncheck all; if true, check all
        for row in self.listStoreDataSets:
            if row[4] == False:
                check_all = True
                break
        if check_all:
            for row in self.listStoreDataSets:
                row[4] = True
        else:
            for row in self.listStoreDataSets:
                row[4] = False


    def onDataSetsTreeMouseClick(self, widget, event):
        (model, it) = widget.get_selection().get_selected()
        if it: #if user right clicked on an existing row
            if event.button == 3:
                self.showDataSetMenu()
            elif event.button == 1:
                try:
                    sel = widget.get_path_at_pos(int(event.x),int(event.y))
                    row = sel[0]
                    column = sel[1]
                    widget.set_cursor(row, column, True)
                except:
                    pass
        else: #right click happened on white space
            pass

    def onTableTreeMouseClick(self, widget, event):
        (model, it) = widget.get_selection().get_selected()
        if it: #if user right clicked on an existing row
            if event.button == 3:
                self.showTableMenu()
            elif event.button == 1: #left clicked on cell; start editing clicked cell
                try:
                    sel = widget.get_path_at_pos(int(event.x),int(event.y))
                    row = sel[0]
                    column = sel[1]
                    widget.set_cursor(row, column, True)
                except: 
                    pass
        else: #right click happened on white space
            pass

    def onTableDeleteRowClicked(self, widget):
        self.tableRemoveRow(None)

    def addToTable(self, x, y, dx, dy):
        self.dataTableListStore.clear()
        for index, value in enumerate(x):
            self.dataTableListStore.insert(-1,[x[index], y[index], dx[index], dy[index]])

    def showTableMenu(self):
        self.tableMenu.show_all()
        self.tableMenu.popup(None, None, None, None, 3, Gtk.get_current_event_time())
        return True


    def showDataSetMenu(self):
        self.dataSetMenu.show_all()
        self.dataSetMenu.popup(None, None, None, None, 3, Gtk.get_current_event_time())
        return True


    def onDSMenuItem1Clicked(self, widget): #remove item
        (model, titer) = self.treeViewDataSets.get_selection().get_selected()
        rownum = model[titer].path.get_indices()[0]
        self.listStoreDataSets.remove(titer)
        del self.dataSetList[rownum]


    def onDSMenuItem2Clicked(self, widget): #move item to table
        (model, titer) = self.treeViewDataSets.get_selection().get_selected()
        rownum = model[titer].path.get_indices()[0]
        x, y, dx, dy = self.dataSetList[rownum].getData()
        self.addToTable(x, y, dx, dy)


    def resetFigure(self):
        self.fig.clf()
        if self.metaDataToggle.get_active():
            self.ax = self.fig.add_subplot(211)
            self.metaText = self.fig.add_subplot(212)
            self.canvas.set_size_request(650, 900)
            self.metaText.spines['right'].set_visible(False)
            self.metaText.spines['top'].set_visible(False)
            self.metaText.spines['bottom'].set_visible(False)
            self.metaText.spines['left'].set_visible(False)
            self.metaText.tick_params(
                axis='both',
                which='both',
                bottom='off',
                top='off',
                labelbottom='off',
                left='off',
                right='off',
                labelleft='off')
        else:
            self.ax = self.fig.add_subplot(111)
            self.metaText = None
            self.canvas.set_size_request(650,450)
        self.fig.tight_layout()

    def resetGraphOptions(self):
        self.ax.grid(self.plotGridCheckButton.get_active())
        self.ax.set_xlabel(self.xLabelEntry.get_text()+ " (" + self.xUnitEntry.get_text() + ")", \
                           fontsize=int(self.labelSizeComboBox.get_active_text()))
        self.ax.set_ylabel(self.yLabelEntry.get_text()+ " (" + self.yUnitEntry.get_text() + ")", \
                           fontsize=int(self.labelSizeComboBox.get_active_text()))        
        self.ax.set_title(self.titleEntry.get_text(), fontsize=int(self.titleSizeComboBox.get_active_text()))
        if self.legendToggle.get_active():
            self.ax.legend(loc=self.legendLocComboBox.get_active_text(), \
                           fontsize=int(self.textSizeComboBox.get_active_text()))
        self.ax.tick_params(
            axis='x',
            which='both',
            bottom=self.xTicsSwitch.get_active(),
            top=self.xTicsSwitch.get_active(),
            labelsize=int(self.tickLabelSizeComboBox.get_active_text()))
        self.ax.tick_params(
            axis='y',
            which='both',
            left=self.yTicsSwitch.get_active(),
            right=self.yTicsSwitch.get_active(),
            labelsize=int(self.tickLabelSizeComboBox.get_active_text()))

        if self.metaText:
            self.metaString1, self.metaString2 = self.mkMetaString()
            self.metaText.text(0, 0.98,self.metaString1, transform=self.metaText.transAxes,
                               horizontalalignment='left', verticalalignment='top', \
                               fontsize=self.textSizeComboBox.get_active_text())
            self.metaText.text(0.5, 0.98,self.metaString2, transform=self.metaText.transAxes,
                               horizontalalignment='left', verticalalignment='top', \
                               fontsize=self.textSizeComboBox.get_active_text())

    def onRefreshPlotClicked(self, widget):
        self.resetFigure()

        for i in range(len(self.dataSetList)):
            if self.listStoreDataSets[i][4]:
                x, y, dx, dy = self.dataSetList[i].getData()
                if self.listStoreDataSets[i][2] == 'lines':
                    self.ax.plot(x, y, linestyle='solid', color=self.listStoreDataSets[i][3], \
                                 label=self.listStoreDataSets[i][1])
                elif self.listStoreDataSets[i][2] == 'scatter':
                    self.ax.scatter(x, y, marker='+', color=self.listStoreDataSets[i][3], \
                                    label=self.listStoreDataSets[i][1])
                else:
                    self.ax.errorbar(x, y, xerr=dx, yerr=dy, linestyle='solid', marker='+', \
                                     color=self.listStoreDataSets[i][3], label=self.listStoreDataSets[i][1])
            self.setRange()
            self.reDrawFunctions()

        self.resetGraphOptions()        
        self.fig.tight_layout()
        self.fig.canvas.draw()
        

    def reDrawFunctions(self):
        xmin, xmax, ymin, ymax = self.ax.axis()
        for i in range(len(self.dataSetList)):
            if self.listStoreDataSets[i][0] == 'function':
                newFunctionDef = functionType(self.dataSetList[i].getFuncString(), xmin, xmax, \
                                              self.setFunctionSamplesSpinButton.get_value_as_int())
                x, y = newFunctionDef.getData()[0:2]
                newFunction = dataManager()
                newFunction.setData(x,y)
                newFunction.setFuncString(self.dataSetList[i].getFuncString())
                self.dataSetList[i] = newFunction
            elif self.listStoreDataSets[i][0] == 'linear model':
                newFunctionDef = functionType(self.dataSetList[i].getFuncString(), xmin, xmax, \
                                              self.setFunctionSamplesSpinButton.get_value_as_int())
                x, y = newFunctionDef.getData()[0:2]
                newFunction = dataManager()
                newFunction.setData(x,y)
                m, b, dm, db, root, droot, corr = self.dataSetList[i].getLinParam()
                newFunction.setLinParam(m=m, b=b, dm=dm, db=db, root=root, droot=droot, corr=corr)
                newFunction.setFuncString(self.dataSetList[i].getFuncString())
                self.dataSetList[i] = newFunction                


    def onAutoScaleSwitched(self, widget):
        if self.autoXSwitch.get_active():
            self.xMinEntry.set_editable(False)
            self.xMaxEntry.set_editable(False)
        else:
            self.xMinEntry.set_editable(True)
            self.xMaxEntry.set_editable(True)
        if self.autoYSwitch.get_active():
            self.yMinEntry.set_editable(False)
            self.yMaxEntry.set_editable(False)
        else:
            self.yMinEntry.set_editable(True)
            self.yMaxEntry.set_editable(True)
            

    def setRange(self):
        if self.autoXSwitch.get_active():
            self.ax.autoscale(enable=True, axis='x')
        else:
            self.ax.set_xlim(float(self.xMinEntry.get_text()), float(self.xMaxEntry.get_text()))
        if self.autoYSwitch.get_active():
            self.ax.autoscale(enable=True, axis='y')
        else:
            self.ax.set_ylim(float(self.yMinEntry.get_text()), float(self.yMaxEntry.get_text()))


    def mkMetaString(self):
        string1 = ''
        string2 = ''
        todays_date = time.strftime("%I:%M:%S") + ' | ' + time.strftime("%d/%m/%Y")
        string1 += 'Author: ' + self.authorEntry.get_text() + '\nInstitution: ' + \
                  self.institutionEntry.get_text() + '\nDate: ' + todays_date + '\n\n'
        row_count = 0
        current_row = 0
        for i in range(len(self.dataSetList)):
            if self.listStoreDataSets[i][0] == 'linear model':
                m, b, dm, db, root, droot, corr = self.dataSetList[i].getLinParam()
                string1 += 'Dataset Filename: ' + \
                          str(self.listStoreDataSets[i][1])+'\nFit: y = mx + b\nm=' + \
                          str("{:10.3e}".format(m)).strip() + '   b=' + \
                          str("{:10.3e}".format(b)).strip() + '\nu(m)=' + \
                          str("{:10.3e}".format(dm)).strip() + '   u(b)=' + \
                          str("{:10.3e}".format(db)).strip() + '\nRoot: ' + \
                          str("{:10.3e}".format(root)).strip() + ' $\pm$ ' + \
                          str("{:10.3e}".format(droot)).strip() + '\n' + 'Correlation Coef: ' + \
                          str("{:10.7f}".format(corr)).strip() + '\n\n'
                row_count += 1
                if row_count == 3:
                    current_row = i+1
                    break
            current_row += 1
        for i in range(current_row,len(self.dataSetList)):
            if self.listStoreDataSets[i][0] == 'linear model':
                m, b, dm, db, root, droot, corr = self.dataSetList[i].getLinParam()
                string2 += 'Dataset Filename: ' + \
                          str(self.listStoreDataSets[i][1])+'\nFit: y = mx + b\nm=' + \
                          str("{:10.3e}".format(m)).strip() + '   b=' + \
                          str("{:10.3e}".format(b)).strip() + '\nu(m)=' + \
                          str("{:10.3e}".format(dm)).strip() + '   u(b)=' + \
                          str("{:10.3e}".format(db)).strip() + '\nRoot: ' + \
                          str("{:10.3e}".format(root)).strip() + ' $\pm$ ' + \
                          str("{:10.3e}".format(droot)).strip() + '\n' + 'Correlation Coef: ' + \
                          str("{:10.7f}".format(corr)).strip() + '\n\n'
        return string1, string2


    def onSavePlotClicked(self, widget):
        path_to_save_fig = self.saveFigureDialog(self)
        if path_to_save_fig:
            frameon = not self.figureTransparentCheckButton.get_active()
            if not path_to_save_fig.endswith(self.figureExtensionComboBox.get_active_text()):
                path_to_save_fig += '.' + self.figureExtensionComboBox.get_active_text()
            path_to_save_fig = path_to_save_fig.replace(" ", "_")
            self.fig.savefig(path_to_save_fig, \
                             dpi=int(self.figureDPIEntry.get_text()), \
                             transparent=self.figureTransparentCheckButton.get_active(), \
                             frameon=frameon)


    def onPrintPlotClicked(self, widget):
        self.fig.savefig(temp_file_storage, \
                         dpi=int(self.figureDPIEntry.get_text()), \
                         papertype='letter', \
                         transparent=False, \
                         frameon=True)
        file_uri = GLib.filename_to_uri(os.path.abspath(temp_file_storage))
        self.doc = Poppler.Document.new_from_file(file_uri)
        pd = Gtk.PrintOperation()
        pd.set_n_pages(1)
        pd.connect("draw_page", self.draw_page)
        result = pd.run(
            Gtk.PrintOperationAction.PRINT_DIALOG, None)


    def draw_page(self, operation, print_ctx, page_num):
        cr = print_ctx.get_cairo_context()
        page = self.doc.get_page(page_num)
        page.render(cr)


    def onSaveDataClicked(self, widget):
        folder_name = self.saveDataDialog(self)
        if folder_name:
            folder_name += '/'
            if self.saveDataFileListComboBox.is_sensitive(): #means we're saving single data set to folder
                filename = folder_name + \
                           self.saveDataFileListComboBox.get_active_text() + \
                           '.' + \
                           self.saveDataFileExtensionComboBox.get_active_text()
                filename = filename.strip().replace(" ", "_")
                self.saveOneFile(self.saveDataFileListComboBox.get_active(), filename)
            else:                                            #means we're saving all selected data sets to folder
                self.saveSelectedFiles(folder_name)
        else:
            pass

    def saveOneFile(self, index, name):
        delim = self.saveDataDelimiterComboBox.get_active_text()
        if delim == 'tabs':
            delim = '\t'
        elif delim == 'spaces':
            delim = ' '
        else:
            delim = ','
        for row in self.listStoreDataSets:
            rownum = row.path.get_indices()[0]
            if rownum == index:
                self.dataSetList[rownum].saveData(name, delim)


    def saveSelectedFiles(self, folder_name):
        delim = self.saveDataDelimiterComboBox.get_active_text()
        if delim == 'tabs':
            delim = '\t'
        elif delim == 'spaces':
            delim = ' '
        else:
            delim = ','
        for row in self.listStoreDataSets:
            if row[4] == True:
                filename = folder_name + row[1] + '.' + self.saveDataFileExtensionComboBox.get_active_text()
                filename = filename.strip().replace(" ", "_")
                rownum = row.path.get_indices()[0]
                self.dataSetList[rownum].saveData(filename, delim)


    def saveDataDialog(self, parent):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        message = ""
        title = "Select a Save Location"
        dialogWindow = Gtk.MessageDialog(parent,
                                         Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                         Gtk.MessageType.OTHER,
                                         Gtk.ButtonsType.OK_CANCEL,
                                         message)
        dialogWindow.set_title(title)
        dialogBox = dialogWindow.get_content_area()
        fileChooser = Gtk.FileChooserWidget()
        fileChooser.set_action(2)
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


    def onSaveDataStatusToggled(self, widget):         #self.saveDataSelectComboBox is the widget passed here
        if widget.get_active_text() == 'save all selected':
            self.saveDataFileListComboBox.set_sensitive(False)
            self.saveDataFileExtensionComboBox.set_sensitive(True)
            self.saveDataDelimiterComboBox.set_sensitive(True)
        elif widget.get_active_text() == 'save single':
            self.saveDataFileListComboBox.set_sensitive(True)
            self.saveDataFileExtensionComboBox.set_sensitive(True)
            self.saveDataDelimiterComboBox.set_sensitive(True)
        elif widget.get_active_text() == 'save state':
            self.saveDataFileListComboBox.set_sensitive(False)
            self.saveDataFileExtensionComboBox.set_sensitive(False)
            self.saveDataDelimiterComboBox.set_sensitive(False)
            file_path = self.saveStateDialog(self)
            if file_path:
                widget.set_active(1)
                self.saveStateXML(file_path)
            else:
                widget.set_active(1)
        else:
            pass


    def saveStateXML(self, file_path):
        if file_path.endswith('.xml'):
            file_path = file_path[:-4] + '.dgr.xml'
        else:
            file_path += '.dgr.xml'
        xml = self.generateStateXML()
        xml.write(file_path)
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Current State Saved")
        dialog.format_secondary_text("DigGRR's current state has been saved to:\n\n" + file_path)
        image = Gtk.Image.new_from_file(programInstallDirectory + '/assets/logo50x.png')
        image.show()
        dialog.set_image(image)
        dialog.run()
        dialog.destroy()


    def saveStateDialog(self, parent):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        message = ""
        title = "Save Application State"
        dialogWindow = Gtk.MessageDialog(parent,
                                         Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                         Gtk.MessageType.OTHER,
                                         Gtk.ButtonsType.OK_CANCEL,
                                         message)
        dialogWindow.set_title(title)
        dialogBox = dialogWindow.get_content_area()
        fileChooser = Gtk.FileChooserWidget()
        fileChooser.set_action(1)
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


    def generateStateXML(self):
        root = et.Element('saveState')
        graphOps = et.SubElement(root, 'graphOptions')
        xRangeOps = et.SubElement(graphOps, 'xRangeOptions')
        xmin = et.SubElement(xRangeOps, 'xMin')
        xmin.text = self.xMinEntry.get_text()
        xmax = et.SubElement(xRangeOps, 'xMax')
        xmax.text = self.xMaxEntry.get_text()
        autoX = et.SubElement(xRangeOps, 'autoXRange')
        autoX.text = str(self.autoXSwitch.get_active())
        xTicks = et.SubElement(xRangeOps, 'xTicks')
        xTicks.text = str(self.xTicsSwitch.get_active())

        yRangeOps = et.SubElement(graphOps, 'yRangeOptions')
        ymin = et.SubElement(yRangeOps, 'yMin')
        ymin.text = self.yMinEntry.get_text()
        ymax = et.SubElement(yRangeOps, 'yMax')
        ymax.text = self.yMaxEntry.get_text()
        autoY = et.SubElement(yRangeOps, 'autoYRange')
        autoY.text = str(self.autoYSwitch.get_active())
        yTicks = et.SubElement(yRangeOps, 'yTicks')
        yTicks.text = str(self.yTicsSwitch.get_active())

        otherOps = et.SubElement(graphOps, 'otherOptions')
        grid = et.SubElement(otherOps, 'grid')
        grid.text = str(self.plotGridCheckButton.get_active())
        legend = et.SubElement(otherOps, 'legend')
        legend.text = str(self.legendLocComboBox.get_active())
        samples = et.SubElement(otherOps, 'functionSamples')
        samples.text = str(int(self.setFunctionSamplesSpinButton.get_value()))

        labelOps = et.SubElement(root, 'labelOptions')
        title = et.SubElement(labelOps, 'title')
        title.text = self.titleEntry.get_text()
        xlabel = et.SubElement(labelOps, 'xLabel')
        xlabel.text = self.xLabelEntry.get_text()
        ylabel = et.SubElement(labelOps, 'yLabel')
        ylabel.text = self.yLabelEntry.get_text()
        xunit = et.SubElement(labelOps, 'xUnit')
        xunit.text = self.xUnitEntry.get_text()
        yunit = et.SubElement(labelOps, 'yUnit')
        yunit.text = self.yUnitEntry.get_text()
        titlesize = et.SubElement(labelOps, 'titleSize')
        titlesize.text = str(self.titleSizeComboBox.get_active())
        labelsize = et.SubElement(labelOps, 'labelSize')
        labelsize.text = str(self.labelSizeComboBox.get_active())
        textsize = et.SubElement(labelOps, 'textSize')
        textsize.text = str(self.textSizeComboBox.get_active())
        inst = et.SubElement(labelOps, 'institution')
        inst.text = self.institutionEntry.get_text()
        author = et.SubElement(labelOps, 'author')
        author.text = self.authorEntry.get_text()
        ticklabelsize = et.SubElement(labelOps, 'ticLabelSize')
        ticklabelsize.text = str(self.tickLabelSizeComboBox.get_active())
        meta = et.SubElement(labelOps, 'metaData')
        meta.text = str(self.metaDataToggle.get_active())
        legend = et.SubElement(labelOps, 'legend')
        legend.text = str(self.legendToggle.get_active())

        dataSets = et.SubElement(root, 'dataSets')
        for index, row in enumerate(self.listStoreDataSets):
            s = et.SubElement(dataSets, 'dataset')
            attribs = {'include' : str(row[4]),
                       'type' : str(row[0]),
                       'filename' : str(row[1]),
                       'linestyle' : str(row[2]),
                       'linecolor' : str(row[3])}
            s.attrib = attribs

            function = et.SubElement(s, 'functionParameters')
            attribs = {'funcString' : str(self.dataSetList[index].getFuncString())}
            function.attrib = attribs

            linear = et.SubElement(s, 'linearParameters')
            params = self.dataSetList[index].getLinParam() # [m,b,dm,db,root,droot,corr]
            attribs = {'m' : str(params[0]),
                       'b' : str(params[1]),
                       'dm' : str(params[2]),
                       'db' : str(params[3]),
                       'root' : str(params[4]),
                       'droot' : str(params[5]),
                       'corr' : str(params[6])}
            linear.attrib = attribs

            x = ",".join([str(i) for i in self.dataSetList[index].x])
            y = ",".join([str(i) for i in self.dataSetList[index].y])
            dx = ",".join([str(i) for i in self.dataSetList[index].dx])
            dy = ",".join([str(i) for i in self.dataSetList[index].dy])
            xcol = et.SubElement(s, 'xData')
            xcol.text = x
            ycol = et.SubElement(s, 'yData')
            ycol.text = y
            dxcol = et.SubElement(s, 'dxData')
            dxcol.text = dx
            dycol = et.SubElement(s, 'dyData')
            dycol.text = dy

        tree = et.ElementTree(root)
        return tree


    def loadStateXML(self, file_path):
        try:
            tree = et.parse(file_path)
            root = tree.getroot()
            self.xMinEntry.set_text('' if not root[0][0][0].text else root[0][0][0].text)
            self.xMaxEntry.set_text('' if not root[0][0][1].text else root[0][0][1].text)
            self.autoXSwitch.set_active(True if root[0][0][2].text == 'True' else False)
            self.xTicsSwitch.set_active(True if root[0][0][3].text == 'True' else False)
            self.yMinEntry.set_text('' if not root[0][1][0].text else root[0][1][0].text)
            self.yMaxEntry.set_text('' if not root[0][1][1].text else root[0][1][1].text)
            self.autoYSwitch.set_active(True if root[0][1][2].text == 'True' else False)
            self.yTicsSwitch.set_active(True if root[0][1][3].text == 'True' else False)
            self.plotGridCheckButton.set_active(True if root[0][2][0].text == 'True' else False)
            self.legendLocComboBox.set_active(True if root[0][2][1].text == 'True' else False)
            self.setFunctionSamplesSpinButton.set_value(float(root[0][2][2].text))
            self.titleEntry.set_text('' if not root[1][0].text else root[1][0].text)
            self.xLabelEntry.set_text('' if not root[1][1].text else root[1][1].text)
            self.yLabelEntry.set_text('' if not root[1][2].text else root[1][2].text)
            self.xUnitEntry.set_text('' if not root[1][3].text else root[1][3].text)
            self.yUnitEntry.set_text('' if not root[1][4].text else root[1][4].text)
            self.titleSizeComboBox.set_active(int(root[1][5].text))
            self.labelSizeComboBox.set_active(int(root[1][6].text))
            self.textSizeComboBox.set_active(int(root[1][7].text))
            self.institutionEntry.set_text('' if not root[1][8].text else root[1][8].text)
            self.authorEntry.set_text('' if not root[1][9].text else root[1][9].text)
            self.tickLabelSizeComboBox.set_active(int(root[1][10].text))
            self.metaDataToggle.set_active(True if root[1][11].text == 'True' else False)
            self.legendToggle.set_active(True if root[1][12].text == 'True' else False)
            
            self.listStoreDataSets.clear()
            self.dataSetList = []
            for item in root[2].findall('dataset'):
                dm = dataManager()
                x = [float(i) for i in item[2].text.split(',')]
                y = [float(i) for i in item[3].text.split(',')]
                dx = [float(i) for i in item[4].text.split(',')]
                dy = [float(i) for i in item[5].text.split(',')]
                dm.setData(x,y,dx,dy)
                if item.attrib['type'] == 'data' or item.attrib['type'] == 'table data':
                    self.dataSetList.append(dm)
                    self.listStoreDataSets.append([item.attrib['type'], 
                                                   item.attrib['filename'], 
                                                   item.attrib['linestyle'], 
                                                   item.attrib['linecolor'], 
                                                   bool(item.attrib['include'])])
                elif item.attrib['type'] == 'linear model':
                    dm.setLinParam(m=float(item[1].attrib['m']), 
                                   b=float(item[1].attrib['b']), 
                                   dm=float(item[1].attrib['dm']), 
                                   db=float(item[1].attrib['db']), 
                                   root=float(item[1].attrib['root']), 
                                   droot=float(item[1].attrib['droot']), 
                                   corr=float(item[1].attrib['corr']))
                    dm.setFuncString(item[0].attrib['funcString'])
                    self.dataSetList.append(dm)
                    self.listStoreDataSets.append([item.attrib['type'], 
                                                   item.attrib['filename'], 
                                                   item.attrib['linestyle'], 
                                                   item.attrib['linecolor'], 
                                                   bool(item.attrib['include'])])                    
                elif item.attrib['type'] == 'function':
                    dm.setFuncString(item[0].attrib['funcString'])
                    self.dataSetList.append(dm)
                    self.listStoreDataSets.append([item.attrib['type'], 
                                                   item.attrib['filename'], 
                                                   item.attrib['linestyle'], 
                                                   item.attrib['linecolor'], 
                                                   bool(item.attrib['include'])])
                else:
                    pass

        except Exception as e:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, "")
            dialog.format_secondary_text("Unable to load saved state.\n\nError: " + str(e))
            image = Gtk.Image.new_from_file(programInstallDirectory + '/assets/logo50x.png')
            image.show()
            dialog.set_image(image)
            dialog.run()
            dialog.destroy()

    def onLoadStateClicked(self, widget):
        file_name = self.loadSavedStateDialog(self)
        if file_name:
            self.loadStateXML(file_name)
        else:
            pass

    def loadSavedStateDialog(self, parent):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        message = "Load a previously saved state. All current settings and data sets will be erased!"
        title = "Load Saved State"
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
        fileFilter.add_pattern("*.dgr.xml")
        fileFilter.set_name("DigGRR Save")
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
        

    def onCanvasRightClick(self, widget, event):
        if event.button == 3:
            self.showCanvasMenu()

    def showCanvasMenu(self):
        self.canvasMenu.show_all()
        self.canvasMenu.popup(None, None, None, None, 3, Gtk.get_current_event_time())
        return True






    def onAboutButtonClicked(self, widget):
        about = Gtk.AboutDialog()
        about.set_authors(["Wes Kyle"])
        about.set_copyright(u'\u00a9 Wes Kyle 2016')
        about.set_comments("DigGRR was created for use in the University of Calgary's\nPhysics Junior Labs to allow linear regression and plotting\nof data collected in experiments.")
        about.set_license_type(3)
        about.set_program_name('DigGRR')
        about.set_logo(self.logoPixBuf)
        about.set_version('version 1.1.0')
        about.set_website('http://www.pjl.ucalgary.ca')
        about.set_website_label('Physics Junior Labs at the University of Calgary')
        about.set_wrap_license(True)
        with open(os.path.abspath(programInstallDirectory + '/assets/gpl.txt'), 'r') as f:
            gpl_license_txt = f.read()
        about.set_license(gpl_license_txt)
        about.show_all()
        response = about.run()
        about.hide()

        
#create main application window and start Gtk loop
mainWindow = linFitApp()
mainWindow.connect("delete-event", Gtk.main_quit)
mainWindow.show_all()

Gtk.main()
