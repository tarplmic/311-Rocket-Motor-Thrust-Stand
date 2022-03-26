import sys
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5 import QtSerialPort
import pyqtgraph as pg
from random import uniform, randint
import serial
import csv
from datetime import datetime

global graphBackground 
graphBackground = (255, 255, 255)
global entireBackground 
entireBackground = QColor('black')
global graphFrameLimit 
graphFrameLimit = 20
serialLine = "blank" + "\n" + "blank" + "\n" + "blank" + "\n" + "blank"
global forceColor
forceColor = (130, 0, 50)

global xArray
xArray = [0]
global forceArray
forceArray = [0]

class arduinoDataThread(QThread):
    def __init__(self):
        super().__init__()

        self.packetCount = 0
        self.arduino = QtSerialPort.QSerialPort()
        self.arduino.setPortName('COM3')
        self.arduino.setBaudRate(9600)
        self.line = ",,,,,,"

        if self.arduino.open(QtSerialPort.QSerialPort.ReadWrite) == False:
            print('false')
            return

        self.dataCollectionTimer = QTimer()
        self.dataCollectionTimer.moveToThread(self)
        self.dataCollectionTimer.timeout.connect(self.getData)

    def getData(self):
        global serialLine

        while(self.arduino.canReadLine()):
            newData = self.arduino.readLine()
            newData = str(newData, 'utf-8')
            self.line += newData
        
        if(self.line != ""):

            self.line = self.line.split("\r\n")

            for x in range(len(self.line)):
                #print(self.line[x])

                if(len(self.line[x].split(',')) > 2):
                    #print(self.line[x])
                    if(self.line[x].split(',')[0] == "d"):
                        #print(self.line[x])

                        self.parseData(self.line[x])
                        
                        serialLineArray = serialLine.split()
                        serialLineArray.pop(0)
                        serialLineArray.append(self.line[x])
                        serialLine = serialLineArray[0] + "\n" + serialLineArray[1] + "\n" + serialLineArray[2] + "\n" + serialLineArray[3]
                    
        self.line = ""

    def parseData(self, line):

        line = line.split(',')
        print(line)
        self.packetCount += 1
        if self.packetCount > graphFrameLimit:
            xArray.pop(0)
            forceArray.pop(0)
        try:
            print('in try')
            xArray.append(self.packetCount)
            forceArray.append(float(line[1]))
        except:
            xArray.pop(len(xArray) - 1)
            forceArray.pop(len(forceArray) - 1)
            print(len(xArray))
            print(len(forceArray))
            print("BAD SP1 DATA")
        
        with open('ThrustData.csv','a',newline='') as fd:
            csvData = csv.writer(fd, delimiter=",")
            csvData.writerow(line)

    def run(self):
        self.dataCollectionTimer.start(50)
        loop = QEventLoop()
        loop.exec_()


class Display(QWidget):
    def __init__(self):
        super().__init__()

        p = self.palette()
        p.setColor(self.backgroundRole(), entireBackground)
        self.setPalette(p)
        #self.createSP1AirTempGraph()
        self.createForceGraph()
        self.createTitle()
        self.changeGraphics()

        self.dataCollectionThread = arduinoDataThread()
        self.dataCollectionThread.start()

        self.updateGraphsThread = updateGraphs(self.updateAllGraphs)
        self.updateGraphsThread.start()

    #creates title for the app
    def createTitle(self):
        self.title = QLabel('Spinister : CanSat Ground Station 2021')
        self.title.setStyleSheet("color: white")
        self.title.setFont(QFont('Arial', 15))
    
    def updateAllGraphs(self):
        if(len(xArray) > len(forceArray)):
            print("contGraphsX greater than containeralt")
            print("contgraphsx: " + str(len(xArray)))
            print("conat alt y: " + str(len(forceArray)))
            xArray.pop(len(xArray) - 1)
            print("contgraphsx: " + str(len(xArray)))
            print("conat alt y: " + str(len(forceArray)))

        elif(len(xArray) < len(forceArray)):
            print("contGraphsX less than containeralt")
            print("contgraphsx: " + str(len(xArray)))
            print("conat alt y: " + str(len(forceArray)))
            xArray.append(xArray[len(xArray) - 1] + 1)
            print("contgraphsx: " + str(len(xArray)))
            print("conat alt y: " + str(len(forceArray)))
        
        self.forcePlot.setData(xArray, forceArray)

    #adds all of the graphs/buttons to the layout
    def changeGraphics(self):
        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setContentsMargins(40, 40, 40, 40)
        grid.addWidget(self.title, 0, 0, 1, 6, Qt.AlignCenter)
        grid.addWidget(self.forceGraph, 1, 0, 1, 2)  
        #grid.addWidget(self.simButt, 3, 3, 1, 1, Qt.AlignCenter)
        self.setLayout(grid)

    #create the altitude real time graph
    def createForceGraph(self):
        self.forceGraph = pg.PlotWidget()
        self.forceGraph.clear()
        self.forceGraph.setRange(yRange=[-10000, 10000])
        self.forceGraph.setTitle('Container Altitude', **{'color': '#000', 'size': '14pt'})
        self.forceGraph.setLabels(left='Force (g)', bottom='Packet Count')
        pen = pg.mkPen(color=forceColor)
        self.forceGraph.setBackground(graphBackground)
        self.forceGraph.getAxis('bottom').setPen('k')
        self.forceGraph.getAxis('left').setPen('k')
        self.forcePlot = self.forceGraph.plot(xArray, forceArray, pen=pen, name='Container')
        app.processEvents()
    
#thread to update the graphs
class updateGraphs(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.updateGraphsTimer = QTimer()
        self.updateGraphsTimer.moveToThread(self)
        self.updateGraphsTimer.timeout.connect(self.func)

    def run(self):
        self.updateGraphsTimer.start(50)
        loop = QEventLoop()
        loop.exec_()
        

#start the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    display = Display()
    display.show()
    
    sys.exit(app.exec_())