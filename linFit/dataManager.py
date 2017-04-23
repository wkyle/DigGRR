#!/usr/bin/env python3

import csv
from itertools import zip_longest


class dataManager():

    """
    numberColumns: the number of columns held in storage
    columnData: the columns of stored data
    shortestLength: the number of values in the shortest column

    Currently needs csv, itertools.zip_longest, numpy
    """
    
    def __init__(self):
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

    def setFilename(self, filename):
        self.filename = filename
        self.hasFilename = True

    def setData(self, *data):
        if data:
            self.numCols = len(data)
            self.data = []
            for item in data:
                self.data.append(item)
            self.shortColumn = len(min(data, key=len))
            self.longColumn = len(max(data, key=len))
            self.hasData = True
        else:
            pass

    def setDelimiter(self, value):
        try:
            self.delimiter = self.delimDict[value]
        except:
            self.delimiter = self.delimDict[0]

    def setLineColor(self, hexColor):
        self.lineColor = str(hexColor)

    def setLineMarker(self, marker):
        self.lineMarker = str(marker)


    def saveData(self, filename):
        self.filename = filename
        self.hasFilename = True
        if self.hasData:
            with open(self.filename, "w", newline='') as f:
                if self.isTruncated: 
                    writer = csv.writer(f, delimiter=self.delimiter)
                    self.data = list(map(list, zip(*self.data)))
                    writer.writerows(self.data)
                else:
                    writer = csv.writer(f, delimiter=self.delimiter)
                    writer.writerows(zip_longest(*self.data, fillvalue=''))
            f.close()
        else:
            pass

    def fitLine(self):
        if self.canFitLine:
            pass
        else:
            pass


    def getFilename(self):
        return self.filename

    def getData(self):
        return self.data

    def doTruncateData(self):
        for columns in self.data:
            del columns[self.shortColumn]

    def getCanFitLine(self):
        self._canFit()
        return self.canFitLine
        print('vis func')


    def _canFit(self):
        if (self.numCols >= 2):
            self.canFitLine = True
            print('invis func')



x = [.1, 4, 5, .7, 4, 11, -3, -.9, 3, 7, 21]
y = [.3, .4, 5.7, .2, -4, -1, 3, 9]
z = [1,2,3,4,5,6,7,8,9]
c = [1,2,4,3,4,.3,5,6,7,-9,8,9]

d = dataManager()

d.setData(x, y, z, c)
print("data set\n", d.getData())
print("number of columns=  ", d.numCols)
print("filename=  ", d.getFilename())
print("has filename?  ", d.hasFilename)
print("has data?  ", d.hasData)
print("shortest=  ", d.shortColumn)
print("longest=  ", d.longColumn)
print("truncated?  ", d.isTruncated)

d.setFilename("datatest.dat")
d.isTruncated = True

print("has filename?   ", d.hasFilename)
print("filename=   ", d.getFilename())
print("what's the delimiter?__", d.delimiter, "__")
d.saveData("datatest.dat")

print("can fit line?  ", d.getCanFitLine())
