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

maxPressure = 6 #DO NOT CHANGE
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
    pMin = np.min(pressureData)

    # plot
    ax[0].plot(pressureData, label="Pressure (Bar)")
    ax[0].plot(pressureDataMA, label="Pressure (Bar) Filtered")
    ax[1].plot(mfcData, label="Flow (L/min)")
    ax[0].scatter(len(pressureData)-1, pressureData[-1])
    ax[0].text(len(pressureData)-1, pressureData[-1], "{:.3f}".format(pressureData[-1]))
    ax[0].set_ylim((pMin*1.05),(pMax*1.05))
    ax[1].scatter(len(mfcData)-1, mfcData[-1])
    ax[1].text(len(mfcData)-1, mfcData[-1], "{:.3f}".format(mfcData[-1]))
    ax[1].set_ylim(0,15)
    ax[0].legend()
    ax[1].legend()

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

            maxV = 3.1 #Maximum voltage for pins on board
            bitNum = 65535 #Number of bits for analog input
            maxP = 5 #Max Pressure
            bitRatio = maxV/bitNum

            #Number Formatting
            f = (num * (bitRatio))
            f += offset
            f *= gain
            f2 = (num2 * (bitRatio)) * maxP/(maxV/2)
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

            height = (fMA*100000)/(1000*7*9.81)
            height = "{:.3f}".format(height)

            #Data printing to terminal, saving to csv and writing to arduino
            print("Time: ", timeNow, "\t P: ", fNum, "\t PMA: ", fNumMa, "\t\t MFC", fNum2, "\t\t Input: ", (inputValue/bitConversion), "\t\t Depth: ", height)
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
        initialInput = float(iI) * bitConversion
        inputValue = initialInput
        inputHigh = float(iH) * bitConversion
        inputLow = float(iL) * bitConversion
        logFile.sendNotice("Variable- InitialValue: " + str(iI) + " InputHigh: " + str(iH) + " InputLow: " + str(iL))
    elif corV == "C" or corV == "c":
        continuous = input("Continuous Flow: ")
        continuous = float(continuous) * bitConversion
        contFlow = continuous/bitConversion
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
maxFlow = 9.399
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
                moving_average = 60
                alpha = (2/(moving_average + 1))
                offset = -1.177
                gain = 1.95
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