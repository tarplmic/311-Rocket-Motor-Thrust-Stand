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
from scipy import integrate

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
xArray = []
global forceArray
forceArray = []

global currentImpulse
currentImpulse = "Waiting..."

global impulseXArray
impulseXArray = []
global impulseYArray
impulseYArray = []

with open('ThrustData.csv','a',newline='') as fd:
    csvData = csv.writer(fd, delimiter=",")
    csvData.writerow(['STARTING NEW RUN'])

class arduinoDataThread(QThread):
    def __init__(self):
        super().__init__()

        self.packetCount = 0
        self.arduino = QtSerialPort.QSerialPort()
        self.arduino.setPortName('COM4')
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
            
            print(self.line)
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
        #print(line)
        self.packetCount += 1
        if self.packetCount > graphFrameLimit:
            xArray.pop(0)
            forceArray.pop(0)
        try:
            #print('in try')
            xArray.append(float(line[2]))
            forceArray.append(float(line[1]))

            impulseXArray.append(float(line[2]))
            impulseYArray.append(float(line[1]))
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
        self.createImpulseGraph()
        self.createTitle()
        self.createRightButtons()
        self.createBottomBoxes()
        self.changeGraphics()

        self.dataCollectionThread = arduinoDataThread()
        self.dataCollectionThread.start()

        self.updateGraphsThread = updateGraphs(self.updateAllGraphs)
        self.updateGraphsThread.start()

    #creates title for the app
    def createTitle(self):
        self.title = QLabel('311 Project: Thrust from Model Rocket Motors 2022')
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
        self.impulseBox.children()[0].itemAt(1).widget().setText(currentImpulse)
        self.impulsePlot.setData(impulseXArray, impulseYArray)

    #adds all of the graphs/buttons to the layout
    def changeGraphics(self):
        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setContentsMargins(40, 40, 40, 40)
        grid.addWidget(self.title, 0, 0, 1, 6, Qt.AlignCenter)
        grid.addWidget(self.forceGraph, 1, 0, 1, 2) 
        grid.addWidget(self.impulseGraph, 1, 3, 1, 2) 
        grid.addWidget(self.commandWid, 2, 4)
        grid.addWidget(self.impulseBox, 2, 0, Qt.AlignCenter)
        #grid.addWidget(self.simButt, 3, 3, 1, 1, Qt.AlignCenter)
        self.setLayout(grid)

    #create the altitude real time graph
    def createForceGraph(self):
        self.forceGraph = pg.PlotWidget()
        self.forceGraph.clear()
        self.forceGraph.setRange(yRange=[-1000, 1000])
        self.forceGraph.setTitle('Force Real Time', **{'color': '#000', 'size': '14pt'})
        self.forceGraph.setLabels(left='Force [g]', bottom='Time [ms]')
        pen = pg.mkPen(color=forceColor)
        self.forceGraph.setBackground(graphBackground)
        self.forceGraph.getAxis('bottom').setPen('k')
        self.forceGraph.getAxis('left').setPen('k')
        self.forcePlot = self.forceGraph.plot(xArray, forceArray, pen=pen, name='Container')
        app.processEvents()
    
    def createImpulseGraph(self):
        self.impulseGraph = pg.PlotWidget()
        self.impulseGraph.clear()
        self.impulseGraph.setRange(yRange=[-1000, 1000])
        self.impulseGraph.setTitle('Force Total', **{'color': '#000', 'size': '14pt'})
        self.impulseGraph.setLabels(left='Force [g]', bottom='Time [ms]')
        pen = pg.mkPen(color=forceColor)
        self.impulseGraph.setBackground(graphBackground)
        self.impulseGraph.getAxis('bottom').setPen('k')
        self.impulseGraph.getAxis('left').setPen('k')
        self.impulsePlot = self.impulseGraph.plot(impulseXArray, impulseYArray, pen=pen, name='SP1')
        app.processEvents()

    #creates the mqtt and command buttons
    def createRightButtons(self):
        self.commandWid = QWidget()
        commandLayout = QVBoxLayout()

        commandLabel = QLabel('Commands')
        commandLabel.setAlignment(Qt.AlignCenter)
        commandLabel.setFont(QFont('Airal', 9))
        commandLabel.setStyleSheet('background-color:black; color:white')
        commandLayout.addWidget(commandLabel)
        
        commandBoxes = QWidget()
        commandBoxesLayout = QHBoxLayout()
        commandBox = QComboBox(self)
        commandBox.setFixedSize(150, 50)
        commandBox.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey')
        #commandBox.addItems(["CX_ON", "CX_PING", "SP1_ON", "SP2_ON", "SIM_ENABLE", "SIM_ACTIVATE", "MANUAL_RELEASE"])
        commandBox.addItems(["GETDATA", "STOPDATA"])
        commandBox.setEditable(True)
        line_edit = commandBox.lineEdit()
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setReadOnly(True) 
        commandBoxesLayout.addWidget(commandBox)
        sendButt = QPushButton('Send Command')
        sendButt.setFixedSize(100,80)
        sendButt.clicked.connect(self.sendCommand)
        sendButt.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey') 
        commandBoxesLayout.addWidget(sendButt)
        commandBoxes.setLayout(commandBoxesLayout)
        commandLayout.addWidget(commandBoxes)

        commandLayout.setAlignment(Qt.AlignCenter)
        self.commandWid.setLayout(commandLayout)
    
    def createBottomBoxes(self):
        self.impulseBox = QWidget()
        impulseBoxLayout = QVBoxLayout()
        impulseBoxLabel = QLabel("Total Impulse")
        impulseBoxLabel.setFont(QFont('Arial', 10))
        impulseBoxLabel.setAlignment(Qt.AlignCenter)
        impulseBoxLabel.setStyleSheet("color: white")
        impulseBoxLayout.addWidget(impulseBoxLabel)
        impulseText = QLineEdit()
        impulseText.setText(str(currentImpulse)) 
        impulseText.setAlignment(Qt.AlignCenter)
        impulseText.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey')
        impulseBoxLayout.addWidget(impulseText)
        self.impulseBox.setLayout(impulseBoxLayout)
    
    def sendCommand(self):
        global impulseXArray
        global impulseYArray

        #print(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText()) #path to the command selected
        if(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "GETDATA"):
            print('About to send GETDATA')

            dat = "<CMD,GETDATA>"
            self.dataCollectionThread.arduino.write(dat.encode())
            impulseXArray = [0]
            impulseYArray = [0]

        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "STOPDATA"):
            print('About to send STOPDATA')

            dat = "<CMD,STOPDATA>"
            self.dataCollectionThread.arduino.write(dat.encode())

            self.updateImpulse(impulseXArray, impulseYArray)

            #impulseXArray = [0]
            #impulseYArray = [0]
    
    def updateImpulse(self, xArray, yArray):
        global currentImpulse
        print('in updateImpulse')

        y_int = integrate.trapz(yArray[11::], xArray[11::]) #units g*ms
        currentImpulse = str(round(y_int / 1000 / 1000 * 9.81, 2)) #convert to kg*sec, and then N*sec

        #currentImpulse = "Calculated"

        with open('Impulses.csv','a',newline='') as fd:
            csvData = csv.writer(fd, delimiter=",")
            csvData.writerow([currentImpulse])
    
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