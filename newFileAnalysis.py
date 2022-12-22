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
fileName = ("Results/" + TLMFile)
layout = ['DateTime', 'RawMFCData', 'MFCData','RawPressureData', 'PressureData', 'MAPressureData', 'InputMFCValue', 'Height', 'Weight']
df = pd.read_csv(fileName, sep = ',', names=layout)
df = df[1:]
InitialPressuredf = df      ##To do the 0 analysis of pressure

for col in range(1, 9):
    df[df.columns[col]] = pd.to_numeric(df[df.columns[col]])

##Filter out times outside of the dip
Date_Time = df["DateTime"] = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in df['DateTime']]
TrialDate = str(input("Trial Date: "))  
DipStart = str(input("Dip Start Time: "))       ##Convert to a time input
DipStart = datetime.strptime(TrialDate + ' ' + DipStart, "%Y-%m-%d %H:%M:%S.%f")
DipEnd = str(input("Dip End Time: "))       ##Convert to a time input
DipEnd = datetime.strptime(TrialDate + ' ' + DipEnd, "%Y-%m-%d %H:%M:%S.%f")
DipFilter = 5*60

df = df[(df["DateTime"] >= DipStart) & (df["DateTime"] <= DipEnd)]
Date_Time = df["DateTime"]
CycleTime = (DipEnd - DipStart).total_seconds()
TimeDiff = [(x - DipStart).total_seconds() for x in df["DateTime"]]


##############################################################################################################################################
##organise load cell data
LCFile = str(input("Load Cell File Name: "))
fileNameBS = ("Results/" + "British Steel/" + LCFile)
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
with PdfPages('figures/' + TLMFile + 'figures_and_tables.pdf') as pdf:


    # First figure: Pressure against Mass Flow
    fig1, ax1 = plt.subplots()
    # Pressure formatting
    ax1.text(0.5, 1.2, "CasTemp Sensor Analysis", transform=ax1.transAxes, fontsize=20, fontweight='bold', ha = 'center')
    ax1.text(0.5, 1.1, "TLM Data: " + TLMFile + ' & ' + "Load Cell Data: " + LCFile, transform=ax1.transAxes, fontsize=14, ha = 'center')
    ax1.set_title("\nPressure Vs Flow Comparison", fontsize=16, fontweight='bold', ha = 'center')

    ax1.plot(TimeDiff, PressureData, 'b', label = 'Pressure')
    ax1.set_ylabel('Pressure (Bar)', color='b')
    # Mass Flow formatting
    ax2 = ax1.twinx()
    ax2.plot(TimeDiff, MFCData, 'r-', label = 'Mass Flow')
    ax2.set_ylabel('Mass Flow(L/min)', color='r')
    # Graph formatting
    ax1.set_xlim([(CycleTime/2)-10, (CycleTime/2)+10])
    ax1.set_ylim([np.min(PressureData[int((CycleTime/2)-10):int((CycleTime/2)+10)])*0.95, np.max(PressureData[int((CycleTime/2)-10):int((CycleTime/2)+10)])*1.05])
    ax2.set_ylim([np.min(MFCData[int((CycleTime/2)-10):int((CycleTime/2)+10)])*0.95, np.max(MFCData[int((CycleTime/2)-10):int((CycleTime/2)+10)])*1.05])
    ax1.grid(which='both', visible=False)
    ax2.grid(which='both', visible=False)
    ax1.set_xlabel('Time(s)')
    ax1.legend(loc='upper left')
    ax2.legend()
    # Save the figure to the PDF file
    pdf.savefig(fig1)
    plt.close(fig1)
    

    # Second figure: Weight Plotting
    fig2, ax2 = plt.subplots()
    WeightData = [float(x) + 23.4 for x in df["Weight"]]            ##Remove Offset
    WeightDataBS = [float(x) for x in dg["NetWeight"]]
    # Formatting
    ax2.set_ylim([25, 40])
    ax2.set_xlabel('Time(s)')
    ax2.set_ylabel('Weight (Tonnes)')
    # Plot
    ax2.plot(TimeDiff, WeightData, label = 'TLM')
    ax2.plot(TimeDiffBS, WeightDataBS, label = 'Load Cell')
    ax2.legend()
    ax2.set_title("Weight Comparison", fontsize=16, fontweight='bold')
    # Save the figure to the PDF file
    pdf.savefig(fig2)
    plt.close(fig2)


    # Third figure: Height Plotting
    fig3, ax3 = plt.subplots()

    HeightData = [float(x) + 0.52 for x in df["Height"]]      ##Height Offset
    a = 0.20675966114731492
    b = 5.089351257804871
    HeightDataBS = [(-b+sqrt((b*b)+(4*a*x)))/(2*7*a) for x in WeightDataBS]

    # Formatting
    ax3.set_xlabel('Time(s)')
    ax3.set_ylabel('Height (m)')
    ax3.plot(TimeDiff, HeightData, label = 'TLM')
    ax3.plot(TimeDiffBS, HeightDataBS, label = 'Load Cell')
    ax3.legend()
    ax3.set_title("Height Comparison", fontsize=16, fontweight='bold')

    # Save the figure to the PDF file
    pdf.savefig(fig3)
    plt.close(fig3)


    # Fourth figure: Mass Flow table
    fig4, ax4 = plt.subplots()

    MFCData = [float(x) for x in df["MFCData"]]
    MFCData1 = MFCData[DipFilter:int(CycleTime)]
    
    data = [['Property', 'Our Data'],
    ["Mean", "{:.3f}".format(np.mean(MFCData1))],
    ["Variance", "{:.3f}".format(np.var(MFCData1))],
    ["Standard Deviation", "{:.3f}".format(np.std(MFCData1))],
    ["Minimum", "{:.3f}".format(np.min(MFCData1))],
    ["Maximum", "{:.3f}".format(np.max(MFCData1))]]

    MassFlowTable = ax4.table(cellText=data, loc='center')
    ax4.set_title("Mass Flow Statistics", fontsize=16, fontweight='bold')
    ax4.axis("off")

    # Save the figure to the PDF file
    pdf.savefig(fig4)
    plt.close(fig4)


    # Fifth figure: Pressure table
    fig5, ax5 = plt.subplots()

    MAPressureData = [float(x) for x in df["MAPressureData"]]
    MAPressureData1 = MAPressureData[DipFilter:int(CycleTime)]
    PressureData = [float(x) for x in df["PressureData"]]
    PressureData1 = PressureData[DipFilter:int(CycleTime)]
    InitialData = [float(x) for x in InitialPressuredf["MAPressureData"]]
    InitialData1 = InitialData[200:400]

    # Calculate statistical values
    means = ['Mean', "{:.3f}".format(np.mean(InitialData1)),"{:.3f}".format(np.mean(MAPressureData1)), "{:.3f}".format(np.mean(PressureData1))]
    variances = ['Variance', "{:.3f}".format(np.var(InitialData1)), "{:.3f}".format(np.var(MAPressureData1)), "{:.3f}".format(np.var(PressureData1))]
    stddevs = ['Standard Deviation', "{:.3f}".format(np.std(InitialData1)), "{:.3f}".format(np.std(MAPressureData1)), "{:.3f}".format(np.std(PressureData1))]
    mins = ['Minimum', "{:.3f}".format(np.min(InitialData1)), "{:.3f}".format(np.min(MAPressureData1)), "{:.3f}".format(np.min(PressureData1))]
    maxs = ['Maximum', "{:.3f}".format(np.max(InitialData1)), "{:.3f}".format(np.max(MAPressureData1)), "{:.3f}".format(np.max(PressureData1))]

    # Create rows for table
    rows = [means, variances, stddevs, mins, maxs]

    # Create and display table
    table = ax5.table(cellText=rows, colLabels=[" ", "Initial Pressure", "MA Pressure", "Pressure"], loc='center')
    ax5.set_title("Pressure Statistics", fontsize=16, fontweight='bold')
    ax5.axis("off")

    # Save the figure to the PDF file
    pdf.savefig(fig5)
    plt.close(fig5)






