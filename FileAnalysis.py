from this import d
from xmlrpc.client import DateTime
import nidaqmx
import math
import time
import datetime
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
import numbers
import collections
from matplotlib.animation import FuncAnimation
from multiprocessing import Process
from pyparsing import nums
plt.style.use('ggplot')

##OUR DATA
"""fileName = ("Results/" + str(input("File Name: ")) + "_" + str(input("Hours: ") + "-" + str(input("Minutes: ") + ".csv")))"""
fileName = "Results/3_15-06.csv"
layout = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'MAPressureData', 'InputMFCValue', 'Height', 'Weight']
 
df = pd.read_csv(fileName, sep = ',', names=layout)
df = df[1:]

Time = df["DateTime"]
Time = [float(x) for x in Time]

MFCData = df["MFCData"]
MFCData = [float(x) for x in MFCData]

MAPressureData = df["MAPressureData"]
MAPressureData = [float(x) for x in MAPressureData]

HeightData = df["Height"]
HeightData = [float(x) for x in HeightData]

WeightData = df["Weight"]
WeightData = [float(x) for x in WeightData]

##BRITISH STEEL DATA
##OUR DATA
"""fileName = ("Results/" + "British Steel/" + str(input("British Steel File Name: ")) + "_" + str(input("Hours: ") + "-" + str(input("Minutes: ") + ".csv")))"""
fileNameBS = "Results/British Steel/grafana_data_export (9).csv"
layoutBS = ['Series', 'Time', 'Value']
 
dff = pd.read_csv(fileNameBS, sep = ';', names=layoutBS)
dff =  dff[dff.Series == "NetWeight"] 

TimeBS = dff["Time"] ##Need to take start time from our file and delete all rows before that, end time and after too
##Then convert time into a time differential float the same as our data
##To do either, our csv must be adapted to output both datetime and timediff
"""TimeBS = [float(x) for x in TimeBS]"""
print(TimeBS)

WeightDataBS = dff["Value"]  ##Calculate Pressure and Height from this
WeightDataBS = [float(x) for x in WeightDataBS]


##PLOTTING
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig, ax = plt.subplots(2, 2, figsize=(15,8))       
ax[0,0].cla(),ax[1,0].cla(),ax[0,1].cla(),ax[1,1].cla()

ax[0,0].plot(Time, MAPressureData)
ax[1,0].plot(Time, MFCData)
ax[0,1].plot(Time, WeightData)
ax[1,1].plot(Time, HeightData)

plt.show()

