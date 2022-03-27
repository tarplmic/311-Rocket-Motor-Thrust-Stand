import numpy as np
import csv
from scipy import integrate
import matplotlib.pyplot as plt

dataFile = "C:/UAH_Classes/311/311-Rocket-Motor-Thrust-Stand/Test_Data/myfile2.csv"

with open(dataFile) as file_name:
    file_read = csv.reader(file_name)
    array = list(file_read)
 
xArray = []
yArray = []

for x in array:
    print(x)
    xArray.append(float(x[0]))
    yArray.append(float(x[1]))

#print(len(xArray))
#print(len(yArray))
y_int = integrate.trapz(yArray[521:661], xArray[521:661]) #units g*ms
y_int = y_int / 1000 / 1000 * 9.81 #convert to kg*sec, and then N*sec
print(y_int)