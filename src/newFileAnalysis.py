import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from cmath import sqrt
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from pyparsing import nums
plt.style.use('ggplot')

##############################################################################################################################################
#organise TLM data
TLMFile = str(input("TLM File Name: "))
"""TLMFile = "Castemp4Trial_10-39"""
fileName = ("Results/" + TLMFile + '.csv')
layout = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'MAPressureData', 'InputMFCValue', 'Height', 'Weight']
df = pd.read_csv(fileName, sep = ',', names=layout)
df = df[1:]
InitialPressuredf = df      ##To do the 0 analysis of pressure

for col in range(1, 9):
    df[df.columns[col]] = pd.to_numeric(df[df.columns[col]])

##Filter out times outside of the dip
Date_Time = df["DateTime"] = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in df['DateTime']]
TrialDate = str(input("Trial Date (YYYY-MM-DD): "))  
"""TrialDate = "2022-12-06"""
DipStart = str(input("Dip Start Time (HH:MM): ")) + ':00.0'     
"""DipStart = "11:00:00.0"""
DipStart = datetime.strptime(TrialDate + ' ' + DipStart, "%Y-%m-%d %H:%M:%S.%f")
DipEnd = str(input("Dip End Time (HH:MM): ")) + ':00.0'      
"""DipEnd = "13:30:00.0"""
DipEnd = datetime.strptime(TrialDate + ' ' + DipEnd, "%Y-%m-%d %H:%M:%S.%f")
DipFilter = 5*60

df = df[(df["DateTime"] >= DipStart) & (df["DateTime"] <= DipEnd)]
Date_Time = df["DateTime"]
CycleTime = (DipEnd - DipStart).total_seconds()
TimeDiff = [(x - DipStart).total_seconds() for x in df["DateTime"]]


##############################################################################################################################################
##organise load cell data
LCFile = str(input("Load Cell File Name: "))
fileNameBS = ("Results/" + "British Steel/" + LCFile + '.csv')
layoutBS = ['Time', 'GrossWeight', 'NetWeight', 'TareWeight', 'CastingRate', 'Position']
 
dg = pd.read_csv(fileNameBS, sep = ';', names=layoutBS)
dg = dg[2:]
dg[dg.columns[1:]] = dg[dg.columns[1:]].apply(lambda x: x.astype(float))
dg["Time"] = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in dg['Time']]
dg = dg[(dg["Time"] >= DipStart) & (dg["Time"] <= DipEnd)]
Date_TimeBS = dg["Time"]
TimeDiffBS = [(x - DipStart).total_seconds() for x in Date_TimeBS]

##############################################################################################################################################
# Data Processing
##Mass Flow Analysis
MFCData = [float(x) for x in df["MFCData"]]
MFCData1 = MFCData[DipFilter:-DipFilter]
##Pressure Analysis
MAPressureData = [float(x) for x in df["MAPressureData"]]
MAPressureData1 = MAPressureData[DipFilter:-DipFilter]
PressureData = [float(x) for x in df["PressureData"]]
PressureData1 = PressureData[DipFilter:-DipFilter]
InitialData = [float(x) for x in InitialPressuredf["MAPressureData"]]
InitialData1 = InitialData[200:400]
##Weight Plotting
WeightData = [float(x) + 23.4 for x in df["Weight"]]            ##Remove Offset
WeightDataBS = [float(x) for x in dg["NetWeight"]]
##Height Plotting
HeightData = [float(x) + 0.52 for x in df["Height"]]      ##Height Offset
a = 0.20675966114731492
b = 5.089351257804871
HeightDataBS = [(-b+sqrt((b*b)+(4*a*x)))/(2*7*a) for x in WeightDataBS]

##############################################################################################################################################
# Create a PDF file
with PdfPages('figures/' + str(input("PDF Name: ")) + '.pdf') as pdf:


    # First figure: Pressure against Mass Flow
    fig1, ax1 = plt.subplots()
    # Pressure formatting
    ax1.set_title("CASTEMP DATA ANALYSIS\n" + "TLM: " + TLMFile + " & " + "Load Cell: " + LCFile + '\n' + "Instrumentation Performance Analysis I", fontsize=10, ha = 'center')
    ax1.plot(TimeDiff, PressureData, 'b', label = 'Pressure')
    ax1.set_ylabel('Pressure (Bar)', color='b')
    # Mass Flow formatting
    ax2 = ax1.twinx()
    ax2.plot(TimeDiff, MFCData, 'r-', label = 'Mass Flow')
    ax2.set_ylabel('Mass Flow(L/min)', color='r')
    # Graph formatting
    List = TimeDiff[int((CycleTime/2)-10):int((CycleTime/2)+10)]
    ax1.set_xlim(List[0], List[-1]) 
    ax1.set_ylim([0.99*np.min(PressureData[int((CycleTime/2)-10):int((CycleTime/2)+10)]), 1.01*np.max(PressureData[int((CycleTime/2)-10):int((CycleTime/2)+10)])])
    ax2.set_ylim([0.99*np.min(MFCData[int((CycleTime/2)-10):int((CycleTime/2)+10)]), 1.01*np.max(MFCData[int((CycleTime/2)-10):int((CycleTime/2)+10)])])
    ax1.grid(which='both', visible=False)
    ax2.grid(which='both', visible=False)
    ax1.set_xlabel('Time(s)')
    ax1.legend(loc='upper left')
    ax2.legend()
    # Save the figure to the PDF file
    pdf.savefig(fig1)
    plt.close(fig1)
    

    # Fourth figure: Mass Flow table
    fig2, ax3 = plt.subplots()

    MFCData = [float(x) for x in df["MFCData"]]
    MFCData1 = MFCData[DipFilter:int(CycleTime)]
    MAPressureData = [float(x) for x in df["MAPressureData"]]
    MAPressureData1 = MAPressureData[DipFilter:int(CycleTime)]
    PressureData = [float(x) for x in df["PressureData"]]
    PressureData1 = PressureData[DipFilter:int(CycleTime)]
    InitialData = [float(x) for x in InitialPressuredf["MAPressureData"]]
    InitialData1 = InitialData[200:400]

    # Calculate statistical values
    means = ['Mean', "{:.3f}".format(np.mean(MFCData1)), "{:.3f}".format(np.mean(InitialData1)),"{:.3f}".format(np.mean(MAPressureData1)), "{:.3f}".format(np.mean(PressureData1))]
    variances = ['Variance', "{:.3f}".format(np.var(MFCData1)), "{:.3f}".format(np.var(InitialData1)), "{:.3f}".format(np.var(MAPressureData1)), "{:.3f}".format(np.var(PressureData1))]
    stddevs = ['Standard Deviation', "{:.3f}".format(np.std(MFCData1)), "{:.3f}".format(np.std(InitialData1)), "{:.3f}".format(np.std(MAPressureData1)), "{:.3f}".format(np.std(PressureData1))]
    mins = ['Minimum', "{:.3f}".format(np.min(MFCData1)), "{:.3f}".format(np.min(InitialData1)), "{:.3f}".format(np.min(MAPressureData1)), "{:.3f}".format(np.min(PressureData1))]
    maxs = ['Maximum', "{:.3f}".format(np.max(MFCData1)), "{:.3f}".format(np.max(InitialData1)), "{:.3f}".format(np.max(MAPressureData1)), "{:.3f}".format(np.max(PressureData1))]

    # Create rows for table
    rows = [means, variances, stddevs, mins, maxs]

    # Create and display table
    table = ax3.table(cellText=rows, colLabels=[" ", "Mass Flow", "Initial Pressure", "MA Pressure", "Pressure"], loc='center')
    ax3.axis("off")
    ax3.set_title("Instrumentation Performance Analysis II", fontsize=10, ha = 'center')


    # Save the figure to the PDF file
    pdf.savefig(fig2)
    plt.close(fig2)


    # Second figure: Weight Plotting
    fig3, ax4 = plt.subplots()
    WeightData = [float(x) + 23.4 for x in df["Weight"]]            ##Remove Offset
    WeightDataBS = [float(x) for x in dg["NetWeight"]]
    # Formatting
    ax4.set_ylim([25, 40])
    ax4.set_xlabel('Time(s)')
    ax4.set_ylabel('Weight (Tonnes)')
    # Plot
    ax4.plot(TimeDiff, WeightData, label = 'TLM')
    ax4.plot(TimeDiffBS, WeightDataBS, label = 'Load Cell')
    ax4.legend()
    ax4.set_title("Weight Comparison", fontsize=10, ha = 'center')
    # Save the figure to the PDF file
    pdf.savefig(fig3)
    plt.close(fig3)


    # Third figure: Height Plotting
    fig4, ax5 = plt.subplots()

    HeightData = [float(x) + 0.52 for x in df["Height"]]      ##Height Offset
    a = 0.20675966114731492
    b = 5.089351257804871
    HeightDataBS = [(-b+sqrt((b*b)+(4*a*x)))/(2*7*a) for x in WeightDataBS]

    # Formatting
    ax5.set_xlabel('Time(s)')
    ax5.set_ylabel('Height (m)')
    ax5.plot(TimeDiff, HeightData, label = 'TLM')
    ax5.plot(TimeDiffBS, HeightDataBS, label = 'Load Cell')
    ax5.legend()
    ax5.set_title("Height Comparison", fontsize=10, ha = 'center')

    # Save the figure to the PDF file
    pdf.savefig(fig4)
    plt.close(fig4)


    








