import serial
import time
import datetime
import matplotlib.pyplot as plt
import csv
import numpy as np
from matplotlib.animation import FuncAnimation
import psutil
import collections
from multiprocessing import Process
from Logs import Log

#Controller for argon pneumatics system for level measurement
def get_counter():
    return counter

def set_counter(updateCount):
    global counter
    counter = counter + updateCount

def insert_data(f, timeNow, temp, f2, num, num2):
    sensorData.append(f)
    timeData.append(timeNow)
    temp.append(timeNow)
    temp.append(num2)
    temp.append(f2)
    temp.append(num)
    temp.append(f)
    temp.append(inputValue)
    writer.writerow(temp) # write to csv

def insert_data_2(temp):
    writer2.writerow(temp) # write to csv

def data_handler(temp):
    # get data
    pressureData.popleft()
    pressureData.append(temp[4])
    mfcData.popleft()
    mfcData.append(temp[2])
    # clear axis
    ax[0].cla()
    ax[1].cla()
    # plot
    ax[0].plot(pressureData)
    ax[1].plot(mfcData)
    ax[0].scatter(len(pressureData)-1, pressureData[-1])
    ax[0].text(len(pressureData)-1, pressureData[-1], "{:.2f}".format(pressureData[-1]))
    ax[0].set_ylim(0,3)
    ax[1].scatter(len(mfcData)-1, mfcData[-1])
    ax[1].text(len(mfcData)-1, mfcData[-1], "{:.2f}".format(mfcData[-1]))
    ax[1].set_ylim(0,15)

def calc_ma(num, ma):
    dLength = len(sensorData)-1
    for n in range(ma-1):
        num += sensorData[dLength-(n+1)]
    numMa = num/ma
    return numMa

def counter_timer():
    global counter
    global inputValue
    if counter == switchHigh:
        inputValue = inputHigh
        logFile.sendNotice("Switched High")
    if counter == switchLow:
        counter = 0
        inputValue = inputLow
        logFile.sendNotice("Switched Low")

#Charting loop - loops when recording and displaying results
def chart_gen(i):
    timeNow = datetime.datetime.now()
    line = ser.readline()   # read a byte string
    line2 = ser.readline() # read mfc
    temp = []

    #Prime Counter
    set_counter(1)
    counter_timer()

    #Chart loop
    if line:
        try:
            string = line.decode().strip()  # convert the byte string to a unicode string
            string2 = line2.decode().strip()
            num = int(string) # convert the unicode string to an int
            num2 = int(string2)

            #Moving Average
            dLength = len(sensorData)
            if dLength > moving_average:
                num = calc_ma(num, moving_average)

            #Number Formatting
            f = (num * (5.0 / 1023.0))
            f += offset
            f *= gain
            f2 = (num2 * (5.0 / 1023.0)) * 3
            fNum = "{:.2f}".format(f)
            fNum2 = "{:.2f}".format(f2)

            #Data printing to terminal, saving to csv and writing to arduino
            print("Time: ", timeNow, "\t Pressure_Data: ", fNum, "\t\t MFC_Data", fNum2, "\t\t Input_Value: ", (inputValue/17))
            insert_data(f, timeNow, temp, f2, num, num2)
            writeToArd(str(inputValue))

            #Variable low flow data storing
            if get_counter() == 15:
                insert_data_2(temp)
            
            #Normal data storing
            data_handler(temp)

        except Exception as e:
            print(e)
            logFile.sendError(e)

def writeToArd(x):
    ser.write(x.encode())

def joiner(fig):
    return FuncAnimation(fig, chart_gen, interval=0)

def modePicker():
    global initialInput, inputValue, inputHigh, inputLow, continuous
    corV = input("Run Continuous Mode or Variable?  Enter C or V: ")
    if corV == "V":
        iI = input("Initial Flow: ")
        iH = input("High Flow: ")
        iL = input("Low Flow: ")
        initialInput = float(iI) * 17
        inputValue = initialInput
        inputHigh = float(iH) * 17
        inputLow = float(iL) * 17
        logFile.sendNotice("Variable- InitialValue: " + str(iI) + " InputHigh: " + str(iH) + " InputLow: " + str(iL))
    elif corV == "C":
        continuous = input("Continuous Flow: ")
        continuous = float(continuous) * 17
        inputHigh = continuous
        inputLow = continuous
        initialInput = continuous
        inputValue = initialInput
        logFile.sendNotice("Continuous- InitialValue: " + str(continuous) + " InputHigh: " + str(continuous) + " InputLow: " + str(continuous))

#Start log file        
startTime = datetime.datetime.now()
logFile = Log(str(startTime))

#Connection to Arduino
try:
    ser = serial.Serial('COM5', 9600, timeout=1)
except Exception as e:
    print(e)
    logFile.sendError(e)

continuous = 255
#Initial Variables
initialInput = continuous
switchHigh = 20
switchLow = 40
inputValue = initialInput
inputHigh = continuous
inputLow = continuous
counter = 0

#Main Loop
if __name__ == "__main__":
    while (True):
        print("\nProgram Started...\n")
        try:
            start = input("Run recorder? Y/N: ")
            if start == "y" or start == "Y":
                modePicker()
                header = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'InputMFCValue']

                fileNameDate = str(startTime)[0:10]
                hour = str(startTime)[11:13]
                mins = str(startTime)[14:16]
                fileNameLong = "Results/Results" + fileNameDate + hour + mins + ".csv"
                fileNameShort = "Results/ResultsCondensed" + fileNameDate + hour + mins + ".csv"

                f = open(fileNameLong, 'x', newline='')
                r = open(fileNameShort, 'x', newline='')
                writer = csv.writer(f)
                writer2 = csv.writer(r)
                writer.writerow(header)
                writer2.writerow(header)

                counter = 0
                moving_average = 1
                gain = 1.5576
                offset = -1.79
                argonCorrection = 1.18
                sensorData = []
                timeData = []
                temp = []

                logFile.sendNotice("MA: " + str(moving_average) + " Gain: " + str(gain) + " Offset: " + str(offset))

                # start collections with zeros
                pressureData = collections.deque(np.zeros(500))
                mfcData = collections.deque(np.zeros(500))

                # define and adjust figure
                fig, ax = plt.subplots(2, figsize=(15,5))
                ax[0].set_facecolor('#DEDEDE')
                ax[1].set_facecolor('#DEDEDE')

                #Declare animation, show plot
                ani = joiner(fig)
                plt.show()
                
                #Close serial connection to arduino
                ser.close()

                # close csv file
                f.close()
                r.close()
            if start == "n" or start == "N":
                exit(0)

        except Exception as e:
            print(e)
            logFile.sendError(e)
            exit(0)