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

#Controller for argon pneumatics system for level measurement

maxPressure = 6
prevEMA = 0.00

#Get counter
def get_counter():
    return counter

#Set counter
def set_counter(updateCount):
    global counter
    counter = counter + updateCount

#Insert data into csv file
def insert_data(f, timeNow, temp, f2, num, num2, fMA, height):
    sensorData.append(fMA)
    timeData.append(timeNow)

    temp.extend((timeNow, num2, f2, num, f, fMA, inputValue, height))

    writer.writerow(temp) # write to csv

#Insert data for condensed csv file
def insert_data_2(temp):
    writer2.writerow(temp) # write to csv

#Set data on subplots
def data_handler(temp):
    # get data
    pressureData.popleft()
    pressureData.append(temp[4])
    pressureDataMA.popleft()
    pressureDataMA.append(temp[5])
    mfcData.popleft()
    mfcData.append(temp[2])

    # clear axis
    ax[0].cla()
    ax[1].cla()

    pMax = np.max(pressureData)

    # plot
    ax[0].plot(pressureData)
    ax[0].plot(pressureDataMA)
    ax[1].plot(mfcData)
    ax[0].scatter(len(pressureData)-1, pressureData[-1])
    ax[0].text(len(pressureData)-1, pressureData[-1], "{:.3f}".format(pressureData[-1]))
    ax[0].set_ylim(0,(pMax + (pMax*0.05)))
    ax[1].scatter(len(mfcData)-1, mfcData[-1])
    ax[1].text(len(mfcData)-1, mfcData[-1], "{:.3f}".format(mfcData[-1]))
    ax[1].set_ylim(0,15)

#Moving average calculator
def calc_ma(num, ma):
    global prevEMA
    ema = (alpha*num) + ((1-alpha) * prevEMA)
    prevEMA = ema
    return ema

#Counter for switching between high and low flow
def counter_timer():
    global counter, inputValue
    if variableOn:
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
    if line and line2:
        try:
            string = line.decode().strip()  # convert the byte string to a unicode string
            string2 = line2.decode().strip()
            num = int(string) # convert the unicode string to an int
            num2 = int(string2)
            numMA = num

            #Number Formatting
            f = (num * (3.355 / 65535.0))
            f += offset
            f *= gain
            f2 = (num2 * (5 / 65535.0)) * 3
            fMA = (numMA * (3.355 / 65535.0))
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

            height = (fMA*100000)/(1000*7*9.81)
            height = "{:.3f}".format(height)

            #Data printing to terminal, saving to csv and writing to arduino
            print("Time: ", timeNow, "\t P: ", fNum, "\t PMA: ", fNumMa, "\t\t MFC", fNum2, "\t\t Input: ", (inputValue/25.5), "\t\t Depth: ", height)
            insert_data(f, timeNow, temp, f2, num, num2, fMA, height)
            writeToArd(str(inputValue))

            #Variable low flow data storing
            if get_counter() == 15:
                insert_data_2(temp)
            
            #Normal data storing
            data_handler(temp)

        except Exception as e:
            print(e)
            logFile.sendError(e)

#Write to arduino
def writeToArd(x):
    ser.write(x.encode())

#Start chart animation
def joiner(fig):
    return FuncAnimation(fig, chart_gen, interval=0)

#Define variables for continous flow mode and variable flow mode
def modePicker():
    global initialInput, inputValue, inputHigh, inputLow, continuous, variableOn
    corV = input("Run Continuous Mode or Variable?  Enter C or V: ")
    if corV == "V" or corV == "v":
        variableOn = True
        iI = input("Initial Flow: ")
        iH = input("High Flow: ")
        iL = input("Low Flow: ")
        initialInput = float(iI) * 25.5
        inputValue = initialInput
        inputHigh = float(iH) * 25.5
        inputLow = float(iL) * 25.5
        logFile.sendNotice("Variable- InitialValue: " + str(iI) + " InputHigh: " + str(iH) + " InputLow: " + str(iL))
    elif corV == "C" or corV == "c":
        continuous = input("Continuous Flow: ")
        continuous = float(continuous) * 25.5
        contFlow = continuous/25.5
        inputHigh = continuous
        inputLow = continuous
        initialInput = continuous
        inputValue = initialInput
        logFile.sendNotice("Continuous- InitialValue: " + str(contFlow) + " InputHigh: " + str(contFlow) + " InputLow: " + str(contFlow))

def pressureSafety(pressure):
    if pressure > maxPressure:
        exit(0)

#Start log file        
startTime = datetime.datetime.now()
logFile = Log(str(startTime))

#Connection to Arduino
try:
    ser = serial.Serial('COM12', 250000, timeout=1)
except Exception as e:
    print(e)
    logFile.sendError(e)


#Initial Variables
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
            start = input("Run recorder? Y/N: ")
            if start == "y" or start == "Y":
                modePicker()
                header = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'MAPressureData', 'InputMFCValue', 'Height']

                fileNameDate = str(input("Enter File Name: "))
                hour = str(startTime)[11:13]
                mins = str(startTime)[14:16]
                fileNameLong = "Results/" + fileNameDate + "_" + hour + "-" + mins + ".csv"
                fileNameShort = "ResultsCondensed/" + fileNameDate + "_" + hour + "-" + mins + ".csv"

                f = open(fileNameLong, 'x', newline='')
                r = open(fileNameShort, 'x', newline='')
                writer = csv.writer(f)
                writer2 = csv.writer(r)
                writer.writerow(header)
                writer2.writerow(header)

                counter = 0
                moving_average = 40
                alpha = (2/(moving_average + 1))
                gain = 2.404
                offset = -1.28
                argonCorrection = 1.18
                sensorData = []
                timeData = []
                temp = []

                logFile.sendNotice("MA: " + str(moving_average) + " Gain: " + str(gain) + " Offset: " + str(offset))

                # start collections with zeros
                pressureData = collections.deque(np.zeros(2000))
                pressureDataMA = collections.deque(np.zeros(2000))
                mfcData = collections.deque(np.zeros(2000))

                # define and adjust figure
                fig, ax = plt.subplots(2, figsize=(15,8))
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
                ser.close()
                exit(0)

        except Exception as e:
            print(e)
            logFile.sendError(e)
            exit(0)