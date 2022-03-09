import serial

ser = serial.Serial('COM10', 9600)  # open serial port
dataArray = []
timeArray = []

print("Hit EntCtrl + C to Stop Data Collection")

try:
    while(1):   # grab data forever until there is a keyboard press
        if(ser.in_waiting):  # if there is data to be read on the serial port
            try: # sometimes there is a read error if the start bit of the ser.readline() isn't right, this is added to avoid code crash in that case
                line = ser.readline().decode()  # read in whats on the serial port and decode it from byte to string
                line = line.strip().split(",") # strip off trailing \r\n and split by commas
                if(line[0] == "d"):  # if we got senor data, append to appropriate arrays
                    #print(line)
                    dataArray.append(line[1])
                    timeArray.append(line[2])
                else:
                    #print("NOT DATA", line)
                    pass
            except Exception as e:
                print(e)
                
except KeyboardInterrupt:

    print(dataArray)
    print(timeArray)
    print(len(dataArray))

    # append the data captured to a csv file
    file1 = open("myfile.csv", "a")  # append mode
    file1.write("STARTING NEW CAPTURE\n")
    for x in range(len(dataArray)):
        file1.write(timeArray[x] + ", " + dataArray[x] + "\n")
    file1.close()

while(1): 
    pass