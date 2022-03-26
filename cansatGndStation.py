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

#define global variables
global containerColor
containerColor = (130, 0, 50)
global sp1Color 
sp1Color = (255, 120, 50)
global sp2Color 
sp2Color = (0, 0, 200)
global graphBackground 
graphBackground = (255, 255, 255)
global entireBackground 
entireBackground = QColor('black')

global graphFrameLimit 
graphFrameLimit = 20

global SP1GraphsX
SP1GraphsX = [0]
global SP1AltY
SP1AltY = [0]
global SP1RotY
SP1RotY = [0]
global SP2GraphsX
SP2GraphsX = [0]
global SP2AltY
SP2AltY = [0]
global SP2RotY
SP2RotY = [0]
global contGraphsX
contGraphsX = [0]
global containerAltY
containerAltY = [0]
global containerBattY
containerBattY = "0.0"
global latitude
latitude = [34]
global longitude 
longitude = [-86]
global utcTimeY
utcTimeY = "00:00:00"
global sp1Temp 
sp1Temp = "0"
global sp2Temp
sp2Temp = "0"
global contTemp 
contTemp = "0"
global serialLine
serialLine = "blank" + "\n" + "blank" + "\n" + "blank" + "\n" + "blank"
global serialLine2
serialLine2 = "blank" + "\n" + "blank" + "\n" + "blank"
global serialLine3
serialLine3 = "blank" + "\n" + "blank" + "\n" + "blank"
global serialLine4
serialLine4 = "blank" + "\n" + "blank" + "\n" + "blank"

global simIndex 
simIndex = 0
global simIndexArray
simIndexArray = []

#thread to grab xbee data from the serial usb port
class xbeeDataThread(QThread):
    def __init__(self):
        super().__init__()

        self.contPacketCount = 0
        self.sp1PacketCount = 0
        self.sp2PacketCount = 0
        self.xbee = QtSerialPort.QSerialPort()
        self.xbee.setPortName('COM3')
        self.xbee.setBaudRate(9600)
        self.line = ",,,,,,"

        if self.xbee.open(QtSerialPort.QSerialPort.ReadWrite) == False:
            return

        self.dataCollectionTimer = QTimer()
        self.dataCollectionTimer.moveToThread(self)
        self.dataCollectionTimer.timeout.connect(self.getData)

    def getData(self):
        global serialLine
        global serialLine2
        global serialLine3
        global serialLine4

        while(self.xbee.canReadLine()):
            newData = self.xbee.readLine()
            newData = str(newData, 'utf-8')
            self.line += newData
        
        if(self.line != ""):

            self.line = self.line.split("\r\n")
            print(self.line)

            for x in range(len(self.line)):
                print(self.line[x])

                if(len(self.line[x].split(',')) > 2):
                    if(self.line[x].split(',')[1] == "d"):
                        
                        serialLineArray = serialLine.split()
                        serialLineArray.pop(0)
                        serialLineArray.append(self.line[x])
                        serialLine = serialLineArray[0] + "\n" + serialLineArray[1] + "\n" + serialLineArray[2] + "\n" + serialLineArray[3]
                    elif(self.line[x].split(',')[3] == "SP1"):
                        #print(self.line.strip())

                        
                        serialLineArray2 = serialLine2.split()
                        serialLineArray2.pop(0)
                        serialLineArray2.append(self.line[x])
                        serialLine2 = serialLineArray2[0] + "\n" + serialLineArray2[1] + "\n" + serialLineArray2[2]
                    elif(self.line[x].split(',')[3] == "SP2"):
                        #print(self.line[x].strip())
                        
                        
                        serialLineArray3 = serialLine3.split()
                        serialLineArray3.pop(0)
                        serialLineArray3.append(self.line[x])
                        serialLine3 = serialLineArray3[0] + "\n" + serialLineArray3[1] + "\n" + serialLineArray3[2]

                    self.line[x] = self.line[x].strip()
                    self.line[x] = self.line[x].split(',')
                    if(len(self.line[x]) >= 20):
                        if(self.line[x][3] == "C"):
                        #parse through and update variable arrays 
                            self.parseContainerData(self.line[x])
                    elif(len(self.line[x]) >= 7):    

                        if(self.line[x][3] == "SP1"):
                            self.parseSP1Data(self.line[x])

                        elif(self.line[x][3] == "SP2"):
                            self.parseSP2Data(self.line[x])

                    for x in range(len(self.line[x])):
                        if(x == "PING_RECIEVED"):
                            print("WE GOT PING RECIEVED")
                    #else:
                        #print("not container data or ping received")
                
                else:
                        serialLineArray4 = serialLine4.split()
                        if(self.line[x] != ""):
                            serialLineArray4.pop(0)
                            serialLineArray4.append(self.line[x])
                        serialLine4 = serialLineArray4[0] + "\n" + serialLineArray4[1] + "\n" + serialLineArray4[2]

                        self.line[x] = ",,,,,,"

        self.line = ""

    def parseSP1Data(self, line):
        global sp1Temp

        #line = line.split(',')
        self.sp1PacketCount += 1
        if self.sp1PacketCount > graphFrameLimit:
            SP1GraphsX.pop(0)
            SP1AltY.pop(0)
            SP1RotY.pop(0)
        try:
            SP1GraphsX.append(self.sp1PacketCount)
            SP1AltY.append(float(line[4]))
            SP1RotY.append(float(line[6]))
        except:
            SP1GraphsX.pop(len(SP1GraphsX) - 1)
            SP1AltY.pop(len(SP1AltY) - 1)
            SP1RotY.pop(len(SP1RotY) - 1)
            print(len(SP1GraphsX))
            print(len(SP1RotY))
            print(len(SP1AltY))
            print("BAD SP1 DATA")
        
        sp1Temp = line[5]

        with open('Flight_2617_SP1.csv','a',newline='') as fd:
            csvData = csv.writer(fd, delimiter=",")
            csvData.writerow(line)
            
    def parseSP2Data(self, line):
        global sp2Temp

        #line = line.split(',')
        self.sp2PacketCount += 1
        if self.sp2PacketCount > graphFrameLimit:
            SP2GraphsX.pop(0)
            SP2AltY.pop(0)
            SP2RotY.pop(0)

        try:
            SP2GraphsX.append(self.sp2PacketCount)
            SP2AltY.append(float(line[4]))
            SP2RotY.append(float(line[6]))
        except:
            SP2GraphsX.pop(len(SP2GraphsX) - 1)
            SP2AltY.pop(len(SP2AltY) - 1)
            SP2RotY.pop(len(SP2RotY) - 1)
            print(len(SP2GraphsX))
            print(len(SP2RotY))
            print(len(SP2AltY))
            print("BAD SP2 DATA")
        
        sp2Temp = line[5]

        with open('Flight_2617_SP2.csv','a',newline='') as fd:
            csvData = csv.writer(fd, delimiter=",")
            csvData.writerow(line)

    def parseContainerData(self, line):
        global containerBattY #have to include global because I am redefining containerBattY every time (for the arrays, I am just appending, not redefining)
        global utcTimeY
        global contTemp

        self.contPacketCount += 1
        if self.contPacketCount > graphFrameLimit:
            contGraphsX.pop(0)
            containerAltY.pop(0)
        contGraphsX.append(self.contPacketCount)
        containerAltY.append(float(line[7]))
        containerBattY = line[9]
        utcTimeY = line[1]
        contTemp = line[8]
        try:
            if(float(line[12]) >= -95 and float(line[12]) <= -70 and float(line[11]) >= 25 and float(line[11]) <= 40) :
                latitude.append(float(line[11]))
                longitude.append(float(line[12]))
        except:
            print("lat long out of range")

        with open('Flight_2617_C.csv','a',newline='') as fd:
            csvData = csv.writer(fd, delimiter=",")
            csvData.writerow(line)
        

    def run(self):
        self.dataCollectionTimer.start(50)
        loop = QEventLoop()
        loop.exec_()

#main class that display the ground station
class Display(QWidget):
    def __init__(self):
        super().__init__()

        p = self.palette()
        p.setColor(self.backgroundRole(), entireBackground)
        self.setPalette(p)
        #self.createSP1AirTempGraph()
        self.createContAltGraph()
        self.createGPSGraph()
        self.createRightButtons()
        self.createLegend()
        self.createBottomBoxes()
        self.createTitle()
        self.createSerialBox()
        self.createSP1RotationGraph()
        self.createSP2RotationGraph()
        self.createSP1AltGraph()
        self.createSP2AltGraph()
        self.createSimButton()
        self.changeGraphics()

        self.dataCollectionThread = xbeeDataThread()
        self.dataCollectionThread.start()

        self.updateGraphsThread = updateGraphs(self.updateAllGraphs)
        self.updateGraphsThread.start()

    #adds all of the graphs/buttons to the layout
    def changeGraphics(self):
        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setContentsMargins(40, 40, 40, 40)
        grid.addWidget(self.title, 0, 0, 1, 6, Qt.AlignCenter)
        grid.addWidget(self.altitudeGraph, 1, 0, 1, 2)  
        grid.addWidget(self.SP1rotationGraph, 2, 0, 1, 2)
        grid.addWidget(self.SP2rotationGraph, 2, 2, 1, 2)
        #grid.addWidget(self.legendWid, 1, 2, Qt.AlignCenter)
        grid.addWidget(self.SP2AltitudeGraph, 1, 4, 1, 2)
        grid.addWidget(self.SP1AltitudeGraph, 1, 2, 1, 2)
        grid.addWidget(self.commandWid, 2, 4)
        grid.addWidget(self.utcBox, 5, 3, Qt.AlignCenter)
        grid.addWidget(self.battBox, 3, 3, Qt.AlignCenter)
        grid.addWidget(self.sp1TempBox, 3, 1, Qt.AlignCenter)
        grid.addWidget(self.sp2TempBox, 3, 2, Qt.AlignCenter)
        grid.addWidget(self.contTempBox, 3, 0, Qt.AlignCenter)
        grid.addWidget(self.mqttSimWid, 3, 4, Qt.AlignCenter)
        grid.addWidget(self.serialBox, 5, 0, 1, 3, Qt.AlignCenter)
        grid.addWidget(self.serialBox2, 5, 4, 1, 1, Qt.AlignCenter)
        grid.addWidget(self.serialBox3, 6, 4, 1, 1, Qt.AlignCenter)
        grid.addWidget(self.serialBox4, 6, 0, 1, 3, Qt.AlignCenter)
        #grid.addWidget(self.simButt, 3, 3, 1, 1, Qt.AlignCenter)
        self.setLayout(grid)

    #create the altitude real time graph
    def createContAltGraph(self):
        self.altitudeGraph = pg.PlotWidget()
        self.altitudeGraph.clear()
        self.altitudeGraph.setRange(yRange=[0, 200])
        self.altitudeGraph.setTitle('Container Altitude', **{'color': '#000', 'size': '14pt'})
        self.altitudeGraph.setLabels(left='Altitude (m)', bottom='Packet Count')
        pen = pg.mkPen(color=containerColor)
        self.altitudeGraph.setBackground(graphBackground)
        self.altitudeGraph.getAxis('bottom').setPen('k')
        self.altitudeGraph.getAxis('left').setPen('k')
        self.contAltitudePlot = self.altitudeGraph.plot(contGraphsX, containerAltY, pen=pen, name='Container')
        app.processEvents()
    
    def createSP1AltGraph(self):
        self.SP1AltitudeGraph = pg.PlotWidget()
        self.SP1AltitudeGraph.clear()
        self.SP1AltitudeGraph.setRange(yRange=[0, 200])
        self.SP1AltitudeGraph.setTitle('SP1 Altitude', **{'color': '#000', 'size': '14pt'})
        self.SP1AltitudeGraph.setLabels(left='Altitude (m)', bottom='Packet Count')
        pen = pg.mkPen(color=sp1Color)
        self.SP1AltitudeGraph.setBackground(graphBackground)
        self.SP1AltitudeGraph.getAxis('bottom').setPen('k')
        self.SP1AltitudeGraph.getAxis('left').setPen('k')
        self.SP1AltitudePlot = self.SP1AltitudeGraph.plot(SP1GraphsX, SP1AltY, pen=pen, name='SP1')
        app.processEvents()

    def createSP2AltGraph(self):
        self.SP2AltitudeGraph = pg.PlotWidget()
        self.SP2AltitudeGraph.clear()
        self.SP2AltitudeGraph.setRange(yRange=[0, 200])
        self.SP2AltitudeGraph.setTitle('SP2 Altitude', **{'color': '#000', 'size': '14pt'})
        self.SP2AltitudeGraph.setLabels(left='Altitude (m)', bottom='Packet Count')
        pen = pg.mkPen(color=sp2Color)
        self.SP2AltitudeGraph.setBackground(graphBackground)
        self.SP2AltitudeGraph.getAxis('bottom').setPen('k')
        self.SP2AltitudeGraph.getAxis('left').setPen('k')
        self.SP2AltitudePlot = self.SP2AltitudeGraph.plot(SP2GraphsX, SP2AltY, pen=pen, name='SP2')
        app.processEvents()

    def createGPSGraph(self):
        self.gpsGraph = pg.PlotWidget()
        self.gpsGraph.clear()
        self.gpsGraph.setRange(yRange=[-85, -87])
        self.gpsGraph.setTitle('GPS', **{'color': '#000', 'size': '14pt'})
        self.gpsGraph.setLabels(left='Longitude (°)', bottom='Latitude (°)')
        self.gpsGraph.setBackground(graphBackground)
        pen = pg.mkPen(color=containerColor)
        self.gpsGraph.getAxis('bottom').setPen('w')
        self.gpsGraph.getAxis('left').setPen('w')
        self.gpsGraphPlot = self.gpsGraph.plot(latitude, longitude, pen=pen, name='GPS', symbol='o')

    #creates the other (currently) non-real time graphs
    def createSP1RotationGraph(self):

        self.SP1rotationGraph = pg.PlotWidget()
        self.SP1rotationGraph.clear()
        self.SP1rotationGraph.setRange(yRange=[0, 1500])
        self.SP1rotationGraph.setTitle('SP1 Rotation', **{'color': '#000', 'size': '14pt'})
        self.SP1rotationGraph.setLabels(left='Rotation (rot/min)', bottom='Packet Count')
        pen = pg.mkPen(color=sp1Color)
        self.SP1rotationGraph.setBackground(graphBackground)
        self.SP1rotationGraph.getAxis('bottom').setPen('k')
        self.SP1rotationGraph.getAxis('left').setPen('k')
        self.SP1rotationPlot = self.SP1rotationGraph.plot(SP1GraphsX, SP1RotY, pen=pen, name='SP2')
        app.processEvents()
    
    def createSP2RotationGraph(self):

        self.SP2rotationGraph = pg.PlotWidget()
        self.SP2rotationGraph.clear()
        self.SP2rotationGraph.setRange(yRange=[0, 1500])
        self.SP2rotationGraph.setTitle('SP2 Rotation', **{'color': '#000', 'size': '14pt'})
        self.SP2rotationGraph.setLabels(left='Rotation (rot/min)', bottom='Packet Count')
        pen = pg.mkPen(color=sp2Color)
        self.SP2rotationGraph.setBackground(graphBackground)
        self.SP2rotationGraph.getAxis('bottom').setPen('k')
        self.SP2rotationGraph.getAxis('left').setPen('k')
        self.SP2rotationPlot = self.SP2rotationGraph.plot(SP2GraphsX, SP2RotY, pen=pen, name='SP2')
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
        commandBox.addItems(["SET_TIME","CX_ON", "CX_OFF", "CX_PING", "SP1_ON", "SP1_OFF", "SP2_ON", "SP2_OFF", "MANUAL_RELEASE", "CLEAR_FLASH", "SIM_ENABLE", "SIM_ACTIVATE", "SIM_DISABLE", "STOP_BUZZER", "START_BUZZER"])
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

        self.altCorrectInput = QLineEdit()
        self.altCorrectInput.returnPressed.connect(self.altCorrectEntered)
        commandLayout.addWidget(self.altCorrectInput)

        commandLayout.setAlignment(Qt.AlignCenter)
        self.commandWid.setLayout(commandLayout)
    
    def altCorrectEntered(self):
        dat = "<CMD,2617,CX,SETALTCORRECTION," + self.altCorrectInput.text() + ">"
        print(dat)
        self.dataCollectionThread.xbee.write(dat.encode())

    #does things when the mqtt button is clicked
    def mqttClicked(self):
        if self.mqttButt.isChecked():
            self.mqttButt.setStyleSheet('background-color:grey; color:white; border:3px solid; border-color:grey') 
            self.mqttButt.setText("MQTT: Enabled")
        else:
            self.mqttButt.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey') 
            self.mqttButt.setText("MQTT: Disabled")
    
    #creates the legend to the right
    def createLegend(self):
        self.legendWid = QWidget()
        legendLayout = QVBoxLayout()
        legendLabel = QLabel("Legend")
        legendLabel.setFont(QFont('Airal', 9))
        legendLabel.setStyleSheet("color: white")
        legendLabel.setAlignment(Qt.AlignCenter)
        legendLayout.addWidget(legendLabel)
        legend = QLabel(self)
        pixmap = QPixmap('image.png')
        legend.setPixmap(pixmap)
        legendLayout.addWidget(legend)
        self.legendWid.setLayout(legendLayout)

    #creates the utc and battery boxes
    def createBottomBoxes(self):
        self.utcBox = QWidget()
        utcLayout = QVBoxLayout()
        utcLabel = QLabel("UTC Time")
        utcLabel.setFont(QFont('Airal', 10))
        utcLabel.setAlignment(Qt.AlignCenter)
        utcLabel.setStyleSheet("color: white")
        utcLayout.addWidget(utcLabel)
        utcText = QLineEdit()
        utcText.setText("00:13:45")
        utcText.setAlignment(Qt.AlignCenter)
        utcText.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey') 
        utcLayout.addWidget(utcText)
        self.utcBox.setLayout(utcLayout)

        self.battBox = QWidget()
        battLayout = QVBoxLayout()
        battLabel = QLabel("Battery Voltage (V)")
        battLabel.setFont(QFont('Arial', 10))
        battLabel.setAlignment(Qt.AlignCenter)
        battLabel.setStyleSheet("color: white")
        battLayout.addWidget(battLabel)
        battText = QLineEdit()
        battText.setText("5.0") 
        battText.setAlignment(Qt.AlignCenter)
        battText.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey')
        battLayout.addWidget(battText)
        self.battBox.setLayout(battLayout)

        self.contTempBox = QWidget()
        contTempLayout = QVBoxLayout()
        contTempLabel = QLabel("Container Temp (C)")
        contTempLabel.setFont(QFont('Arial', 10))
        contTempLabel.setAlignment(Qt.AlignCenter)
        contTempLabel.setStyleSheet("color: white")
        contTempLayout.addWidget(contTempLabel)
        contTempText = QLineEdit()
        contTempText.setText("5.0") 
        contTempText.setAlignment(Qt.AlignCenter)
        contTempText.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey')
        contTempLayout.addWidget(contTempText)
        self.contTempBox.setLayout(contTempLayout)

        self.sp1TempBox = QWidget()
        sp1TempLayout = QVBoxLayout()
        sp1TempLabel = QLabel("SP1 Temp (C)")
        sp1TempLabel.setFont(QFont('Arial', 10))
        sp1TempLabel.setAlignment(Qt.AlignCenter)
        sp1TempLabel.setStyleSheet("color: white")
        sp1TempLayout.addWidget(sp1TempLabel)
        contTempText = QLineEdit()
        contTempText.setText("5.0") 
        contTempText.setAlignment(Qt.AlignCenter)
        contTempText.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey')
        sp1TempLayout.addWidget(contTempText)
        self.sp1TempBox.setLayout(sp1TempLayout)

        self.sp2TempBox = QWidget()
        sp2TempLayout = QVBoxLayout()
        sp2TempLabel = QLabel("SP2 Temp (C)")
        sp2TempLabel.setFont(QFont('Arial', 10))
        sp2TempLabel.setAlignment(Qt.AlignCenter)
        sp2TempLabel.setStyleSheet("color: white")
        sp2TempLayout.addWidget(sp2TempLabel)
        contTempText = QLineEdit()
        contTempText.setText("5.0") 
        contTempText.setAlignment(Qt.AlignCenter)
        contTempText.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey')
        sp2TempLayout.addWidget(contTempText)
        self.sp2TempBox.setLayout(sp2TempLayout)

    def createSerialBox(self):
        self.serialBox = QWidget()
        serialBoxLayout = QVBoxLayout()
        serialBoxLabel = QLabel("Container Telemetry:")
        serialBoxLabel.setFont(QFont('Arial', 10))
        serialBoxLabel.setAlignment(Qt.AlignCenter)
        serialBoxLabel.setStyleSheet("color: white")
        serialBoxLayout.addWidget(serialBoxLabel)
        serialBoxText = QTextEdit()
        serialBoxText.setAlignment(Qt.AlignCenter)
        serialBoxText.setStyleSheet('background-color:white; color:black; border:3px solid; border-color:grey')
        serialBoxText.setFixedSize(900,80)
        serialBoxLayout.addWidget(serialBoxText)
        #serialBoxLayout.addStretch()
        self.serialBox.setLayout(serialBoxLayout)

        self.serialBox2 = QWidget()
        serialBox2Layout = QVBoxLayout()
        serialBox2Label = QLabel("Payload 1 Telemetry:")
        serialBox2Label.setFont(QFont('Arial', 10))
        serialBox2Label.setAlignment(Qt.AlignCenter)
        serialBox2Label.setStyleSheet("color: white")
        serialBox2Layout.addWidget(serialBox2Label)
        serialBox2Text = QTextEdit()
        serialBox2Text.setAlignment(Qt.AlignCenter)
        serialBox2Text.setStyleSheet('background-color:white; color:black; border:3px solid; border-color:grey')
        serialBox2Text.setFixedSize(400,60)
        serialBox2Layout.addWidget(serialBox2Text)
        #serialBox2Layout.addStretch()
        self.serialBox2.setLayout(serialBox2Layout)

        self.serialBox3 = QWidget()
        serialBox3Layout = QVBoxLayout()
        serialBox3Label = QLabel("Payload 2 Telemetry:")
        serialBox3Label.setFont(QFont('Arial', 10))
        serialBox3Label.setAlignment(Qt.AlignCenter)
        serialBox3Label.setStyleSheet("color: white")
        serialBox3Layout.addWidget(serialBox3Label)
        serialBox3Text = QTextEdit()
        serialBox3Text.setAlignment(Qt.AlignCenter)
        serialBox3Text.setStyleSheet('background-color:white; color:black; border:3px solid; border-color:grey')
        serialBox3Text.setFixedSize(400,60)
        serialBox3Layout.addWidget(serialBox3Text)
        #serialBox3Layout.addStretch()
        self.serialBox3.setLayout(serialBox3Layout)

        self.serialBox4 = QWidget()
        serialBox4Layout = QVBoxLayout()
        serialBox4Label = QLabel("Extra Telemetry:")
        serialBox4Label.setFont(QFont('Arial', 10))
        serialBox4Label.setAlignment(Qt.AlignCenter)
        serialBox4Label.setStyleSheet("color: white")
        serialBox4Layout.addWidget(serialBox4Label)
        serialBox4Text = QTextEdit()
        serialBox4Text.setAlignment(Qt.AlignCenter)
        serialBox4Text.setStyleSheet('background-color:white; color:black; border:3px solid; border-color:grey')
        serialBox4Text.setFixedSize(900,60)
        serialBox4Layout.addWidget(serialBox4Text)
        #serialBox4Layout.addStretch()
        self.serialBox4.setLayout(serialBox4Layout)

    def createSimButton(self):
        self.mqttSimWid = QWidget()
        mqttSimLayout = QHBoxLayout()

        self.mqttButt = QPushButton("MQTT: Disabled")
        self.mqttButt.setFixedSize(100, 50)
        self.mqttButt.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey') 
        self.mqttButt.setCheckable(True)
        self.mqttButt.toggle()
        self.mqttButt.clicked.connect(self.mqttClicked)
        mqttSimLayout.addWidget(self.mqttButt)

        self.simButt = QPushButton("Not sending SIMP")
        self.simButt.setFixedSize(150, 50)
        self.simButt.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey') 
        self.simButt.setCheckable(True)
        self.simButt.toggle()
        self.simButt.clicked.connect(self.simButtonClicked)
        mqttSimLayout.addWidget(self.simButt)

        mqttSimLayout.setAlignment(Qt.AlignCenter)
        self.mqttSimWid.setLayout(mqttSimLayout)

    def simButtonClicked(self):
        global simIndex
        if self.simButt.isChecked():
            simIndex = 0
            self.simButt.setStyleSheet('background-color:grey; color:white; border:3px solid; border-color:grey') 
            self.simButt.setText("Am sending SIMP")

            # with open('simData.txt','r') as fd:
            #     for line in fd:
            #         line = line.replace('$', '2617')
            #         line = line.replace('\n', '')
            #         line = "<" + line + ">"
            #         simIndexArray.append(line)
            
            with open('Cansat_2021_sim_file_B.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if (len(row) >= 3):
                        if(row[0] == 'CMD'):
                            row[1] = "2617"
                            #print("<" + row[0] + "," + row[1] + "," + row[2] + "," + row[3] + ">")
                            simIndexArray.append("<" + row[0] + "," + row[1] + "," + row[2] + "," + row[3] + ">")

            self.sendSimDataThread = sendSimData(self.sendSimDataFun)
            self.sendSimDataThread.start()

        else:
            self.sendSimDataThread.quit()
            self.simButt.setStyleSheet('background-color:black; color:white; border:3px solid; border-color:grey') 
            self.simButt.setText("Not sending SIMP")
            simIndex = 0
    
    def sendSimDataFun(self):
        global simIndex

        if(simIndex >= len(simIndexArray)):
            cmdToSend = simIndexArray[len(simIndexArray) - 1]
        else:
            cmdToSend = simIndexArray[simIndex]
        
        self.dataCollectionThread.xbee.write(cmdToSend.encode())

        print(simIndex)
        simIndex += 1



    #creates title for the app
    def createTitle(self):
        self.title = QLabel('Spinister : CanSat Ground Station 2021')
        self.title.setStyleSheet("color: white")
        self.title.setFont(QFont('Arial', 15))

    #updates all of the graphs with data coming from xbee
    def updateAllGraphs(self):
        if(len(contGraphsX) > len(containerAltY)):
            print("contGraphsX greater than containeralt")
            print("contgraphsx: " + str(len(contGraphsX)))
            print("conat alt y: " + str(len(containerAltY)))
            contGraphsX.pop(len(contGraphsX) - 1)
            print("contgraphsx: " + str(len(contGraphsX)))
            print("conat alt y: " + str(len(containerAltY)))

        elif(len(contGraphsX) < len(containerAltY)):
            print("contGraphsX less than containeralt")
            print("contgraphsx: " + str(len(contGraphsX)))
            print("conat alt y: " + str(len(containerAltY)))
            contGraphsX.append(contGraphsX[len(contGraphsX) - 1] + 1)
            print("contgraphsx: " + str(len(contGraphsX)))
            print("conat alt y: " + str(len(containerAltY)))

        if(len(SP1GraphsX) > len(SP1AltY) or len(SP1GraphsX) > len(SP1RotY)):
            print("sp1GraphsX more than SP1AltY")
            print("SP1GraphsX: " + str(len(SP1GraphsX)))
            print("SP1AltY: " + str(len(SP1AltY)))
            print("SP1RotY: " + str(len(SP1RotY)))
            SP1GraphsX.pop(len(SP1GraphsX) - 1)
            print("SP1GraphsX: " + str(len(SP1GraphsX)))
            print("SP1AltY: " + str(len(SP1AltY)))
            print("SP1rot: " + str(len(SP1RotY)))

            if(len(SP1AltY) > len(SP1RotY)):
                print("SP1RotY: " + str(len(SP1RotY)))
                print("SP1AltY: " + str(len(SP1AltY)))
                SP1AltY.pop(len(SP1AltY) - 1)
                print("SP1RotY: " + str(len(SP1RotY)))
                print("SP1AltY: " + str(len(SP1AltY)))

            elif(len(SP1AltY) < len(SP1RotY)):
                print("SP1RotY: " + str(len(SP1RotY)))
                print("SP1AltY: " + str(len(SP1AltY)))
                SP1RotY.pop(len(SP1RotY) - 1)
                print("SP1RotY: " + str(len(SP1RotY)))
                print("SP1AltY: " + str(len(SP1AltY)))
        
        if(len(SP1GraphsX) < len(SP1AltY) or len(SP1GraphsX) < len(SP1RotY)):
            print("sp1GraphsX less than SP1AltY")
            print("SP1GraphsX: " + str(len(SP1GraphsX)))
            print("SP1AltY: " + str(len(SP1AltY)))
            print("SP1RotY: " + str(len(SP1RotY)))
            SP1GraphsX.append(SP1GraphsX[len(SP1GraphsX) - 1] + 1)
            print("SP1GraphsX: " + str(len(SP1GraphsX)))
            print("SP1AltY: " + str(len(SP1AltY)))
            print("SP1RotY: " + str(len(SP1RotY)))

            if(len(SP1AltY) > len(SP1RotY)):
                print("SP1AltY: " + str(len(SP1AltY)))
                print("SP1RotY: " + str(len(SP1RotY)))
                SP1RotY.append(0)
                print("SP1AltY: " + str(len(SP1AltY)))
                print("SP1RotY: " + str(len(SP1RotY)))

            elif(len(SP1AltY) < len(SP1RotY)):
                print("SP1AltY: " + str(len(SP1AltY)))
                print("SP1RotY: " + str(len(SP1RotY)))
                SP1RotY.append(0)
                print("SP1AltY: " + str(len(SP1AltY)))
                print("SP1RotY: " + str(len(SP1RotY)))

        if(len(SP2GraphsX) < len(SP2AltY) or len(SP2GraphsX) < len(SP2RotY)):
            print("sp2GraphsX less than SP2AltY")
            print("SP2GraphsX: " + str(len(SP2GraphsX)))
            print("SP2AltY: " + str(len(SP2AltY)))
            print("SP2RotY: " + str(len(SP2RotY)))
            SP2GraphsX.append(SP2GraphsX[len(SP2GraphsX) - 1] + 1)
            print("SP2GraphsX: " + str(len(SP2GraphsX)))
            print("SP2AltY: " + str(len(SP2AltY)))
            print("SP2RotY: " + str(len(SP2RotY)))

            if(len(SP2AltY) > len(SP2RotY)):
                print("SP2AltY: " + str(len(SP2AltY)))
                print("SP2RotY: " + str(len(SP2RotY)))
                SP2RotY.append(0)
                print("SP2AltY: " + str(len(SP2AltY)))
                print("SP2RotY: " + str(len(SP2RotY)))

            elif(len(SP2AltY) < len(SP2RotY)):
                print("SP2AltY: " + str(len(SP2AltY)))
                print("SP2RotY: " + str(len(SP2RotY)))
                SP2RotY.append(0)
                print("SP2AltY: " + str(len(SP2AltY)))
                print("SP2RotY: " + str(len(SP2RotY)))

        if(len(SP2GraphsX) > len(SP2AltY) or len(SP2GraphsX) > len(SP2RotY)):
            print("SP2GraphsX more than SP2AltY")
            print("SP2GraphsX: " + str(len(SP2GraphsX)))
            print("SP2AltY: " + str(len(SP2AltY)))
            print("SP2RotY: " + str(len(SP2RotY)))
            SP2GraphsX.pop(len(SP2GraphsX) - 1)
            print("SP2GraphsX: " + str(len(SP2GraphsX)))
            print("SP2AltY: " + str(len(SP2AltY)))
            print("SP2rot: " + str(len(SP2RotY)))

            if(len(SP2AltY) > len(SP2RotY)):
                print("SP2RotY: " + str(len(SP2RotY)))
                print("SP2AltY: " + str(len(SP2AltY)))
                SP2AltY.pop(len(SP2AltY) - 1)
                print("SP2RotY: " + str(len(SP2RotY)))
                print("SP2AltY: " + str(len(SP2AltY)))

            elif(len(SP2AltY) < len(SP2RotY)):
                print("SP2RotY: " + str(len(SP2RotY)))
                print("SP2AltY: " + str(len(SP2AltY)))
                SP2RotY.pop(len(SP2RotY) - 1)
                print("SP2RotY: " + str(len(SP2RotY)))
                print("SP2AltY: " + str(len(SP2AltY)))

        self.contAltitudePlot.setData(contGraphsX, containerAltY)
        self.SP1AltitudePlot.setData(SP1GraphsX, SP1AltY)
        self.SP2AltitudePlot.setData(SP2GraphsX, SP2AltY)
        self.SP1rotationPlot.setData(SP1GraphsX, SP1RotY)
        self.SP2rotationPlot.setData(SP2GraphsX, SP2RotY)

        self.battBox.children()[0].itemAt(1).widget().setText(containerBattY) #path to the battery voltage box
        self.gpsGraphPlot.setData(latitude, longitude)
        #print(self.utcBox.children()[0].itemAt(1).widget())
        self.utcBox.children()[0].itemAt(1).widget().setText(utcTimeY)
        self.contTempBox.children()[0].itemAt(1).widget().setText(contTemp)
        self.sp1TempBox.children()[0].itemAt(1).widget().setText(sp1Temp)
        self.sp2TempBox.children()[0].itemAt(1).widget().setText(sp2Temp)
        self.serialBox.children()[0].itemAt(1).widget().setText(serialLine)
        self.serialBox2.children()[0].itemAt(1).widget().setText(serialLine2)
        self.serialBox3.children()[0].itemAt(1).widget().setText(serialLine3)
        self.serialBox4.children()[0].itemAt(1).widget().setText(serialLine4)


    def sendCommand(self):
        #print(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText()) #path to the command selected
        if(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "CX_PING"):
            print('About to send ping command')
            dat = "<CMD,2617,CX,PING>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "MANUAL_RELEASE"):
            print('About to send release command')
            dat = "<CMD,2617,CX,RELEASE>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SET_TIME"):
            print('About to send st command')
            rightnow = datetime.utcnow()
            rightnow = str(rightnow).split(" ")[1][0:8]
            dat = "<CMD,2617,ST," + rightnow + ">"
            self.dataCollectionThread.xbee.write(dat.encode())

        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "CLEAR_FLASH"):
            print('About to send clear flash command')
            dat = "<CMD,2617,CX,CLEARFLASH>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "CX_ON"):
            print('About to send cxon')
            dat = "<CMD,2617,CX,ON>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "CX_OFF"):
            print('About to send cxoff')
            dat = "<CMD,2617,CX,OFF>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SIM_ENABLE"):
            print('About to send sim enable')
            dat = "<CMD,2617,SIM,ENABLE>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SIM_ACTIVATE"):
            print('About to send sim activate')
            dat = "<CMD,2617,SIM,ACTIVATE>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SIM_DISABLE"):
            print('About to send sim disable')
            dat = "<CMD,2617,SIM,DISABLE>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SP1_ON"):
            print('About to send SP1_on')
            dat = "<CMD,2617,SP1X,ON>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SP1_OFF"):
            print('About to send sp1_off')
            dat = "<CMD,2617,SP1X,OFF>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SP2_ON"):
            print('About to send SP2_on')
            dat = "<CMD,2617,SP2X,ON>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "SP2_OFF"):
            print('About to send sp2_off')
            dat = "<CMD,2617,SP2X,OFF>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "STOP_BUZZER"):
            print('About to send stop buzzer')
            dat = "<CMD,2617,CX,STOP_BUZZER>"
            self.dataCollectionThread.xbee.write(dat.encode())
        elif(self.commandWid.children()[0].itemAt(1).widget().children()[1].currentText() == "START_BUZZER"):
            print('About to send start buzzer')
            dat = "<CMD,2617,CX,START_BUZZER>"
            self.dataCollectionThread.xbee.write(dat.encode())

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

class sendSimData(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.sendSimDataTimer = QTimer()
        self.sendSimDataTimer.moveToThread(self)
        self.sendSimDataTimer.timeout.connect(self.func)

    def run(self):
        self.sendSimDataTimer.start(1000)
        loop = QEventLoop()
        loop.exec_()

#start the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    display = Display()
    display.show()
    
    sys.exit(app.exec_())