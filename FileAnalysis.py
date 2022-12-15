from cmath import sqrt
import nidaqmx
import math
import time
from datetime import datetime
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

##GRAPHS
##OUR DATA
"""fileName = ("Results/" + str(input("File Name: ")) + "_" + str(input("Hours: ") + "-" + str(input("Minutes: ") + ".csv")))"""
fileName = "Results/CasTemp3_14-59.csv"
layout = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'MAPressureData', 'InputMFCValue', 'Height', 'Weight']
 
df = pd.read_csv(fileName, sep = ',', names=layout)
df = df[1:]

Date_Time = df["DateTime"]
Date_Time = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in df['DateTime']]
StartTime = Date_Time[0]
EndTime = Date_Time[-1]
CycleTime = (EndTime - StartTime).total_seconds()
TimeDiff = [(x - StartTime).total_seconds() for x in Date_Time]

MFCData = df["MFCData"]
MFCData = [float(x) for x in MFCData]

MAPressureData = df["MAPressureData"]
MAPressureData = [float(x) for x in MAPressureData]

HeightData = df["Height"]
HeightData = [float(x) for x in HeightData]

WeightData = df["Weight"]
WeightData = [float(x) for x in WeightData]



##BRITISH STEEL DATA
"""fileName = ("Results/" + "British Steel/" + str(input("British Steel File Name: ")) + "_" + str(input("Hours: ") + "-" + str(input("Minutes: ") + ".csv")))"""
fileNameBS = "Results/British Steel/grafana_data_export (12).csv"
layoutBS = ['Time', 'GrossWeight', 'NetWeight', 'TareWeight', 'CastingRate', 'Position']
 
dg = pd.read_csv(fileNameBS, sep = ';', names=layoutBS)
dg = dg[2:]

Date_TimeBS = dg["Time"]
Date_TimeBS = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in dg['Time']]
TimeDiffBS = [(x - StartTime).total_seconds() for x in Date_TimeBS]  

WeightDataBS = dg["NetWeight"]  ##Calculate Pressure and Height from this
WeightDataBS = [float(x) for x in WeightDataBS]

HeightDataBS = [((-5.16996+sqrt((26.72848+1.4*x)/0.7))) for x in WeightDataBS]

"""MAPressureDataBS = [x*(1000*7*9.81)/100000 for x in HeightDataBS]"""


##PLOTTING
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig, ax = plt.subplots(2, 2, figsize=(15,8))       
ax[0,0].cla(),ax[1,0].cla(),ax[0,1].cla(),ax[1,1].cla()

ax[0,0].plot(TimeDiff, MAPressureData)
ax[1,0].plot(TimeDiff, MFCData)
ax[0,1].plot(TimeDiff, WeightData)
ax[1,1].plot(TimeDiff, HeightData)

"""ax[0,0].plot(TimeDiffBS, MAPressureDataBS)"""
ax[0,1].plot(TimeDiffBS, WeightDataBS)
ax[1,1].plot(TimeDiffBS, HeightDataBS)

ax[0,0].set_xlim([0, CycleTime])
ax[1,0].set_xlim([0, CycleTime])
ax[0,1].set_xlim([0, CycleTime])
ax[1,1].set_xlim([0, CycleTime])

ax[0,0].set_xlabel('Time (s)')
ax[1,0].set_xlabel('Time (s)')
ax[0,1].set_xlabel('Time (s)')
ax[1,1].set_xlabel('Time (s)')

ax[0,0].set_ylabel('Pressure(Bar)')
ax[1,0].set_ylabel('Mass Flow (L/Min)')
ax[0,1].set_ylabel('Weight (Tonnes)')
ax[1,1].set_ylabel('Depth (m)')

"""plt.savefig("figures/" + str(input("Name of Figure: ") + ".pdf"))"""
"""plt.show()"""


#############################################################################################################################################
##TABLE
##Our Data
dh = pd.read_csv(fileName, sep = ',', names=layout)
dh = dh[((60*10)-1):]  #Change to end before last 10 minutes

MFCData1 = dh["MFCData"]
MFCData1 = [float(x) for x in MFCData]
MAPressureData1 = dh["MAPressureData"]
MAPressureData1 = [float(x) for x in MAPressureData]
HeightData1 = dh["Height"]
HeightData1 = [float(x) for x in HeightData]
WeightData1 = dh["Weight"]
WeightData1 = [float(x) for x in WeightData]


##British steel Data
##Needs to delete data pulled from outside of the dip start and dip end times
di = pd.read_csv(fileNameBS, sep = ';', names=layoutBS)
di = di[2:]

Date_TimeBS = di["Time"]
Date_TimeBS = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in di['Time']]
TimeDiffBS = [(x - StartTime).total_seconds() for x in Date_TimeBS] 

WeightDataBS1 = di["NetWeight"]  ##Calculate Pressure and Height from this
WeightDataBS1 = [float(x) for x in WeightDataBS1]
HeightDataBS1 = [((-5.16996+sqrt((26.72848+1.4*x)/0.7))) for x in WeightDataBS1]
MAPressureDataBS1 = [x*(1000*7*9.81)/100000 for x in HeightDataBS1]


##Calculate standard deviation of initial pressure
std_pressure = np.std(MAPressureData[60:120])
##Calculate standard deviation of mass flow
std_mass_flow = np.std(MFCData1)
##Calculate variance of pressure
var_pressure = np.var(MAPressureData1)
var_pressureBS = np.var(MAPressureDataBS1)
##Calculate variance of weight
var_weight = np.var(WeightData1)
var_weightBS = np.var(WeightDataBS1)
##Calculate variance of height
var_height = np.var(HeightData1)
var_heightBS = np.var(HeightDataBS1)

data = [['Property', 'Our Data', 'British Steel Data'],
['standard deviation of initial pressure', std_pressure, 'N/A'],
['standard deviation of mass flow', std_mass_flow, 'N/A'],
['variance of pressure', var_pressure, var_pressureBS],
['variance of weight', var_weight, var_weightBS],
['variance of height', var_height, var_heightBS]]

##Create the table
fig2, ax2 = plt.subplots()
table = plt.table(cellText=data, loc='center')
table.scale(1,2)
ax2.axis("off")
fig2.tight_layout()


plt.show()