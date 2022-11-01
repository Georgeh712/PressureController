import os, shutil
import math
import serial
import time
import datetime
import matplotlib.pyplot as plt
import csv
import numpy as np
import collections
from matplotlib.animation import FuncAnimation
from multiprocessing import Process
from Logs import Log
plt.style.use('ggplot')
#Controller for argon pneumatics system for level measurement

#---------------------------------------------------------------------------------------------------
##Control Panel
#Controller for argon pneumatics system for level measurement

def startMenu():
    while(True):
        choice = int(input(
                    "1: Run recorder\n"
                    "2: Exit\n"
                    "9: Delete all logs and saved files\n"))
        if choice == 1:
            return 'Y'
        elif choice == 2:
            print("User Exit")
            return 'N'
        elif choice == 9:
            deleteRecords()
        else:
            print("Invalid Input - Try Again")
            startMenu()

def deleteRecords():
    confirm = input('Are you sure you wish to delete all records?\n')
    if confirm == 'Y' or confirm == 'y':
        folders = ['Logs/', 'Results/', 'ResultsCondensed/']
        for folder in folders:
            f = folder
            for filename in os.listdir(f):
                file_path = os.path.join(f, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logFile.sendError(e)
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        print("No Files Deleted")

def startSerialConnection():
    try:
        ser = serial.Serial('COM14', 9600, timeout=1)
        return ser
    except Exception as e:
        print(e)
        logFile.sendError(e)

#Write to arduino
def writeToArd(x):
    ser.write(x.encode())

#Insert data into csv file
def insert_data(f, timeNow, temp, f2, num, num2, fMA, height, weight):
    sensorData.append(fMA)
    timeData.append(timeNow)

    temp.extend((timeNow, num2, f2, num, f, fMA, inputValue, height, weight))

    writer.writerow(temp) # write to csv

#Set data on subplots
def data_handler(temp):
    # get data
    pressureData.popleft()
    pressureData.append(temp[4])
    pressureDataMA.popleft()
    pressureDataMA.append(temp[5])
    mfcData.popleft()
    mfcData.append(temp[2])
    heightData.popleft()
    heightData.append(temp[7])
    weightData.popleft()
    weightData.append(temp[8])

    # clear axis
    ax[0,0].cla()
    ax[1,0].cla()
    ax[0,1].cla()
    ax[1,1].cla()

    pMax = np.max(pressureData)
    pMin = np.min(pressureData)

    # plot
    ax[0,0].plot(pressureData, label="Pressure (Bar)")
    ax[0,0].plot(pressureDataMA, label="Pressure (Bar) Filtered")
    ax[1,0].plot(mfcData, label="Flow (L/min)")
    ax[0,1].plot(weightData, label="Weight (Tonnes)")

    #Pressure chart
    ax[0,0].scatter(len(pressureData)-1, pressureData[-1])
    ax[0,0].text(len(pressureDataMA)-1, pressureDataMA[-1], "{:.3f}".format(pressureDataMA[-1]))
    ax[0,0].set_ylim((pMin*1.05),(pMax*1.05))

    #Flow chart
    ax[1,0].scatter(len(mfcData)-1, mfcData[-1])
    ax[1,0].text(len(mfcData)-1, mfcData[-1], "{:.3f}".format(mfcData[-1]))
    ax[1,0].set_ylim(0,12)
    
    #Weight chart
    ax[0,1].scatter(len(weightData)-1, weightData[-1])
    ax[0,1].text(len(weightData)-1, weightData[-1], "{:.3f}".format(weightData[-1]))
    ax[0,1].set_ylabel('Weight (Tonnes)')
    ax[0,1].set_ylim(0,40)

    #Depth chart
    ax[1,1].bar('Depth', heightData)
    ax[1,1].text(0, heightData[0]+0.05, "{:.3f}".format(heightData[0]))
    ax[1,1].set_ylabel('Depth (m)')
    ax[1,1].set_ylim(0,1)

    ax[0,0].legend()
    ax[1,0].legend()
    ax[0,1].legend()

#Start chart animation
def joiner(fig):
    return FuncAnimation(fig, chart_gen, interval=10)

def chart_gen(i):
    timeNow = datetime.datetime.now()
    line = ser.readline()   # read a byte string
    line2 = ser.readline() # read mfc
    temp = []

    #Chart loop
    if line and line2:
        try:
            string = line.decode().strip()  # convert the byte string to a unicode string
            string2 = line2.decode().strip()
            num = int(string) # convert the unicode string to an int
            num2 = int(string2)
            numMA = num

            maxV = 3.271 #Maximum voltage for pins on board (INPUT USED, SHOULD IT BE OUTPUT?)
            bitNum = 4096 #Number of bits for analog input
            flowMultiplier = maxFlow/maxV
            bitRatio = maxV/bitNum

            #Number Formatting
            f = (num * (bitRatio))
            f += offset
            f *= gain
            f2 = (num2 * (bitRatio)) * flowMultiplier
            fMA = (numMA * (bitRatio))
            fMA += offset
            fMA *= gain

            #Moving Average
            dLength = len(sensorData)
            if dLength > moving_average:
                fMA = calc_ma(fMA, moving_average)
            
            pressureSafety(f)

            fNum = "{:.3f}".format(f)
            fNum2 = "{:.3f}".format(f2)
            fNumMa = "{:.3f}".format(fMA)

            height = float((fMA*100000)/(1000*7*9.81))
            fheight = "{:.3f}".format(height)
            
            weight = weightCalc(height)
            
            fInputValue = "{:.3f}".format(inputValue/bitConversion)

            #Data printing to terminal, saving to csv and writing to arduino
            print("Time: ", timeNow, "\t P: ", fNum, "\t PMA: ", fNumMa, "\t\t MFC", fNum2, "\t\t Input: ", fInputValue, "\t\t Depth: ", fheight, "\t\t Weight: ", weight)
            insert_data(f, timeNow, temp, f2, num, num2, fMA, height, weight)
            writeToArd(str(inputValue))
            
            #Normal data storing
            data_handler(temp)

        except Exception as e:
            print(e)
            logFile.sendError(e)

#Define variables for continous flow mode and variable flow mode
def modePicker():
    global initialInput, inputValue, inputHigh, inputLow, continuous, variableOn    
    continuous = input("Continuous Flow: ")
    continuous = float(continuous) * bitConversion
    contFlow = continuous/bitConversion
    inputHigh = continuous
    inputLow = continuous
    initialInput = continuous
    inputValue = initialInput
    logFile.sendNotice("Continuous- InitialValue: " + str(contFlow) + " InputHigh: " + str(contFlow) + " InputLow: " + str(contFlow))

  #Moving average calculator
def calc_ma(num, ma):
    global prevEMA
    ema = (alpha*num) + ((1-alpha) * prevEMA)
    prevEMA = ema
    return ema

#Calculates weight based on rough dimension of tundish (output is only an estimate)
def weightCalc(height):
    areaTriangles = (height*(math.sin(0.203854)/math.sin(1.57-0.203854)))*height
    area = ((1*(math.sin(0.349)/math.sin(1.57-0.349)))*1)+(0.34*1)
    volume = ((areaTriangles+((0.508-0.05)*height))*(9.625-0.05))+(area*height)
    return (volume*7000)/1000

def pressureSafety(pressure):
    if pressure > maxPressure:
        exit(0)

#Start log file        
startTime = datetime.datetime.now()
logFile = Log(str(startTime))

#Initial Variables
maxPressure = 3.3 - 1.81 #DO NOT CHANGE (max - offset)
prevEMA = 0.00
maxFlow = 9.813 #maximum flow rate 
bitConversion = 255 / maxFlow
variableOn = False
continuous = 255
initialInput = continuous
switchHigh = 20
switchLow = 30
inputValue = initialInput
inputHigh = continuous
inputLow = continuous
counter = 0

#Main Loop
if __name__ == "__main__":
    while (True):
        print("\nProgram Started...\n")
        try:
            start = startMenu()
            if start == "y" or start == "Y":
                modePicker()
                header = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'MAPressureData', 'InputMFCValue', 'Height', 'Weight']

                fileNameDate = str(input("Enter File Name: "))
                hour = str(startTime)[11:13]
                mins = str(startTime)[14:16]
                fileNameLong = "Results/" + fileNameDate + "_" + hour + "-" + mins + ".csv"

                f = open(fileNameLong, 'x', newline='')
                writer = csv.writer(f)
                writer.writerow(header)

                counter = 0
                moving_average = 30
                alpha = (2/(moving_average + 1))
                offset = -1.76                    # 1.81V is the output of the sensor at 1 atm - the pressure measures absolute 0-5bar so max is 4 bar gauge
                gain = 1.254                        # How do we properly calculate this value?
                argonCorrection = 1.18
                sensorData = []
                timeData = []
                temp = []

                logFile.sendNotice("MA: " + str(moving_average) + " Gain: " + str(gain) + " Offset: " + str(offset))

                # start collections with zeros
                pressureData = collections.deque(np.zeros(2000))
                pressureDataMA = collections.deque(np.zeros(2000))
                mfcData = collections.deque(np.zeros(2000))
                heightData = collections.deque(np.zeros(1))
                weightData = collections.deque(np.zeros(5000))

                # define and adjust figure
                fig, ax = plt.subplots(2, 2, figsize=(15,8))
                ax[0,0].set_facecolor('#DEDEDE')
                ax[1,0].set_facecolor('#DEDEDE')
                ax[1,1].set_facecolor('#DEDEDE')

                #Start connection with Arduino
                ser = startSerialConnection()

                #Declare animation, show plot
                ani = joiner(fig)
                plt.show()

                #Close serial connection to arduino
                ser.close()

                # close csv file
                f.close()

            if start == "n" or start == "N":
                print("Session Ended")
                ser.close()
                exit(0)

        except Exception as e:
            print(e)
            logFile.sendError(e)
            exit(0)
