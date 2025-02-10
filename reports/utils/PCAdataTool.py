#!/usr/bin/env python
# coding: utf-8

# In[13]:
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator
from PyPDF2 import PdfReader, PdfMerger
import os
import datetime
from datetime import timedelta
from fpdf import FPDF
import pandas as pd
import textwrap as twp
import re
# coding: utf-8
from enum import IntEnum
import subprocess

from django.conf import settings
from django.utils.text import slugify
from django.conf import settings


output_dir = '/code/imgs/' 
# Referres to root/imgs
if not os.path.exists(output_dir):
    os.makedirs(output_dir)



def get_dynamic_output_dir(instance):
    """
    Generates the dynamic output directory for a report.
    """
    # Construct the path based on instance attributes
    output_report_dir = os.path.join(
        settings.MEDIA_ROOT,  # Base media directory
        'reports_save',       # Subdirectory for reports
        str(instance.id),     # Unique report ID
    )

    # Ensure the directory exists
    if not os.path.exists(output_report_dir):
        os.makedirs(output_report_dir)

    return output_report_dir

def get_dynamic_output_file(instance):
    """
    Generates the full path for the report file, including the filename.
    """
    relative_dir = os.path.join('reports_save', str(instance.id))
    absolute_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
    if not os.path.exists(absolute_dir):
        os.makedirs(absolute_dir)
    filename = f"{slugify(instance.property_address)}_{instance.start_time.strftime('%Y%m%d%H%M%S')}.pdf"
    return os.path.join(relative_dir, filename)

output_report_dir = os.path.join(settings.MEDIA_ROOT, 'reports_save')
# Referres to root/reports_save
if not os.path.exists(output_report_dir):
    os.makedirs(output_report_dir)

# Generate and save the figure
fig, ax = plt.subplots()
# (plotting code here)
plt.savefig(os.path.join(output_dir, 'Fig1.0.png'))
plt.close()


class FontSize(IntEnum):
    CONTENT = 11
    HEADER = 14
    INDEX = 12


class RoomData:
    import pandas as pd
    @staticmethod
    def BMIIndex(x):
        if x >= 5.5:
            Index = 'Extremely High'
        elif x >= 4.5:
            Index = 'Very High'
        elif x >= 3.5:
            Index = 'High'
        elif x >= 2.5:
            Index = 'Moderate'
        elif x >= 1.5:
            Index = 'Low'
        elif x >= 0.5:
            Index = 'Very Low'
        else:
            Index = 'no impact of'
        return Index

    @staticmethod
    def impactScore(threshold, exceedThreshold, s, a, b, c, d, e, f):
        score1 = 0
        score2 = 0
        if threshold >= 80.0:
            score1 = 6.0  # scoreEH
        elif threshold >= 60.0:
            score1 = 5.0  # scoreVH
        elif threshold >= 40.0:
            score1 = 4.0  # scoreH
        elif threshold >= 20.0:
            score1 = 3.0  # scoreM
        elif threshold >= 10.0:
            score1 = 2.0  # scoreL
        elif threshold >= s:
            score1 = 1.0  # scoreVL
        else:
            score1 = 0.0  # scoreNS

        if exceedThreshold >= a:
            score2 = 6.0  # scoreEH
        elif exceedThreshold >= b:
            score2 = 5.0  # scoreVH
        elif exceedThreshold >= c:
            score2 = 4.0  # scoreH
        elif exceedThreshold >= d:
            score2 = 3.0  # scoreM
        elif exceedThreshold >= e:
            score2 = 2.0  # scoreL
        elif exceedThreshold >= f:
            score2 = 1.0  # scoreVL
        else:
            score2 = 0.0  # scoreNS
        return (score1 + score2) / 2

    @staticmethod
    def bmiScore(factor):
        score = 0
        if factor >= 5.5:
            score = 6.0  # scoreEH
        elif factor >= 4.5:
            score = 5.0  # scoreVH
        elif factor >= 3.5:
            score = 4.0  # scoreH
        elif factor >= 2.5:
            score = 3.0  # scoreM
        elif factor >= 1.5:
            score = 2.0  # scoreL
        elif factor >= 0.5:
            score = 1.0  # scoreVL
        else:
            score = 0.0  # scoreNS
        return score

    def __init__(self, datafile, index=0, start_time=None, end_time=None, problem_room=None, monitor_area=None):

        # if index == 0:
        #     self.suffix = ''
        # else:
        #     self.suffix = f'.{index}'
        self.suffix = f'.{index}'
        self.inputFile = datafile
        self.index = index

        if re.search(".xlsx$", datafile):
            print(f'Read Excel file {datafile} for analysis.')
            dataframe = pd.read_excel(datafile)
        else:
            print(f'Read csv file {datafile} for analysis.')
            dataframe = pd.read_csv(datafile)
            if 'timestamp' in dataframe.columns:
                dataframe.rename(columns={'timestamp': 'Time'}, inplace=True)
                dataframe['Time'] = pd.to_datetime(dataframe['Time'], format='%d/%m/%Y %H:%M:%S')
            # print(dataframe)
                dataframe.dropna(inplace=True)

        # Check if 'IndoorAirTemp' and 'IndoorRelativeH' exist
        if 'IndoorAirTemp' in dataframe.columns and 'IndoorRelativeH' in dataframe.columns:
            # Calculate 'IndoorDewPoint'
            a = 17.27
            b = 237.7
            alpha = (a * dataframe['IndoorAirTemp']) / (b + dataframe['IndoorAirTemp']) + np.log(dataframe['IndoorRelativeH'] / 100.0)
            dataframe['IndoorDewPoint'] = (b * alpha) / (a - alpha)
        else:
            # Handle missing columns
            print("Warning: 'IndoorAirTemp' or 'IndoorRelativeH' column is missing from the data.")
            dataframe['IndoorDewPoint'] = pd.Series([float('nan')] * len(dataframe))
        
        # print("After dropna")
        # print(dataframe)
        TI = dataframe.Time
        SN = TI.size
        self.startTime = TI[0]
        self.endTime = TI[SN - 1]

        timeDuration = self.endTime - self.startTime  # timedelta object
        print(f'From input file {self.inputFile}: startTime:{self.startTime}  endTime:{self.endTime}')
              # f'TI[0]:{TI[0]} TI[SN - 1]{TI[SN - 1]}')

        self.days = timeDuration.days
        self.hours, remainder = divmod(timeDuration.seconds, 3600)

        self.NPR = problem_room
        if problem_room == 'select room':
            self.problem_room = f'ROOM {self.index}'
        else:
            self.problem_room = str(problem_room).upper()

        print(f'Debug room data problem room {self.problem_room}')
        self.monitor_area = monitor_area
        print(f'Debug room data monitor area {self.monitor_area}')

        if start_time:
            self.STDH = str(start_time)
        else:
            self.STDH = str(self.startTime)
        if end_time:
            self.EDDH = str(end_time)
        else:
            self.EDDH = str(self.endTime)
        if start_time:
            startIndex = np.argmax(TI > start_time)
        else:
            startIndex = 0
        if end_time:
            endIndex = np.argmin(TI < end_time)
        else:
            endIndex = SN - 1
        self.TI = dataframe.Time[startIndex:endIndex]
        self.ATI = dataframe.IndoorAirTemp[startIndex:endIndex]
        self.RHI = dataframe.IndoorRelativeH[startIndex:endIndex]
        self.DPI = dataframe.IndoorDewPoint[startIndex:endIndex]
        self.STI = dataframe.SurfaceTemp[startIndex:endIndex]
        self.ATO = dataframe.OutdoorAirTemp[startIndex:endIndex]
        self.RHO = dataframe.OutdoorRelativeH[startIndex:endIndex]
        # Sat VP (To)
        self.SATO = ((self.ATO.div(self.ATO + 237.3)) * 17.2694).apply(np.exp) * 610.5

        # Vpo (Kpa)
        self.VPO = self.SATO.div(1000) * self.RHO.div(100)

        # Outdoor Air Moisture Content
        self.AMOC = 2170 * self.VPO.div(self.ATO + 273.3)

        # Sat VP (Ti)
        self.SATI = ((self.ATI.div(self.ATI + 237.3)) * 17.2694).apply(np.exp) * 610.5

        # Sat VP (Tsi)
        self.SATS = ((self.STI.div(self.STI + 237.3)) * 17.2694).apply(np.exp) * 610.5

        # VPI(KPa)
        self.VPI = self.SATI.div(1000) * self.RHI.div(100)

        # Vapour Pressure Excess(VPE)
        self.VPE = self.VPI - self.VPO

        # Indoor Air Moisture Content
        self.AMIC = 2170 * self.VPI.div(self.ATI + 273.3)

        # Air Moisture Content

        # Diff Tsi-Dp
        self.DifSTID = self.STI - self.DPI

        # Diff Ti-Dp
        self.DifATID = self.ATI - self.DPI

        # Water Activity
        self.WA = self.SATI * self.RHI.div(self.SATS * 100)

        # Temp factor
        self.TF = (self.STI - self.ATO).div(self.ATI - self.ATO)
        #    print('original size of TF', len(TF))
        self.TF = self.TF.replace(np.inf, np.nan)
        self.TF = self.TF.replace(-np.inf, np.nan)
        self.TF.dropna()
        #    print('Nan dropped size of TF', len(TF))

        self.TFF = self.TF[self.TF > 0]
        #    print('< 0 dropped size of TF1', len(TFF))
        self.TFF = self.TFF[self.TFF <= 1]
        #    print('> 1 dropped size of TF1', len(TFF))

        ###############################################
        # Prepare data for tables

        self.AveSTI = round(self.STI.mean(), 2)
        self.MinSTI = round(self.STI.min(), 2)
        self.MaxSTI = round(self.STI.max(), 2)

        # No need as saved in object global AveATI
        self.AveATI = round(self.ATI.mean(), 2)
        self.MinATI = round(self.ATI.min(), 2)
        self.MaxATI = round(self.ATI.max(), 2)
        #    StdATI = round(ATI.std(),1)

        self.AveATO = round(self.ATO.mean(), 2)
        self.MinATO = round(self.ATO.min(), 2)
        self.MaxATO = round(self.ATO.max(), 2)
        #   StdATO = round(ATO.std(),1)

        # No need as saved in object global AveRHI
        self.AveRHI = round(self.RHI.mean(), 2)
        self.MinRHI = round(self.RHI.min(), 2)
        self.MaxRHI = round(self.RHI.max(), 2)
        #  StdRHI = round(RHI.std(),1)

        self.AveRHO = round(self.RHO.mean(), 2)
        self.MinRHO = round(self.RHO.min(), 2)
        self.MaxRHO = round(self.RHO.max(), 2)
        #    StdRHO = round(RHO.std(),1)

        # No need as saved in object global AveVPE

        self.AveVPE = round(self.VPE.mean(), 2)
        self.MinVPE = round(self.VPE.min(), 2)
        self.MaxVPE = round(self.VPE.max(), 2)
        #    StdVPE = round(VPE.std(),1)

        # No need as saved in object global AveWA
        self.AveWA = round(self.WA.mean(), 2)
        self.MinWA = round(self.WA.min(), 2)
        self.MaxWA = round(self.WA.max(), 2)

        # No need as saved in ojbect global AveTF
        self.AveTF = round(self.TFF.mean(), 2)
        self.MinTF = round(self.TFF.min(), 2)
        self.MaxTF = round(self.TFF.max(), 2)

        self.AveDPI = round(self.DPI.mean(), 2)
        self.MinDPI = round(self.DPI.min(), 2)
        self.MaxDPI = round(self.DPI.max(), 2)
        #   StdDPI = round(DPI.std(),1)

        # No need as saved in object global AveDifSTID
        self.AveDifSTID = round(self.DifSTID.mean(), 2)
        self.MinDifSTID = round(self.DifSTID.min(), 2)
        self.MaxDifSTID = round(self.DifSTID.max(), 2)
        #  StdDifSTID = round(DifSTID.std(),2)

        self.AveAMIC = round(self.AMIC.mean(), 2)
        self.MinAMIC = round(self.AMIC.min(), 2)
        self.MaxAMIC = round(self.AMIC.max(), 2)
        #   StdAMIC = round(AMIC.std(),2)

        self.AveDifATID = round(self.DifATID.mean(), 2)
        self.MinDifATID = round(self.DifATID.min(), 2)
        self.MaxDifATID = round(self.DifATID.max(), 2)
        #    StdDifATID = round(DifATID.std(),2)

        self.AveVPO = round(self.VPO.mean(), 2)
        self.MinVPO = round(self.VPO.min(), 2)
        self.MaxVPO = round(self.VPO.max(), 2)
        #    StdVPO = round(VPO.std(),1)

        self.AveVPI = round(self.VPI.mean(), 2)
        self.MinVPI = round(self.VPI.min(), 2)
        self.MaxVPI = round(self.VPI.max(), 2)
        #    StdVPI = round(VPI.std(),1)

        # Average Thresholds
        dataSize = self.TI.size + 2
        #    print(dataSize)
        self.pcTholdWA = round(sum(1 for x in self.WA if round(float(x), 4) > 0.8) / dataSize * 100, 4)
        self.pcTholdTF = round(sum(1 for x in self.TFF if round(float(x), 4) <= 0.75) / dataSize * 100, 4)
        self.pcTholdRHI = round(sum(1 for x in self.RHI if round(float(x), 4) > 60) / dataSize * 100, 4)
        self.pcTholdATI = round(sum(1 for x in self.ATI if float(x) <= 15.5) / dataSize * 100, 3)
        self.pcTholdVPE = round(sum(1 for x in self.VPE if float(x) > 0.6) / dataSize * 100, 4)
        self.pcTholdSTID = round(sum(1 for x in self.DifSTID if float(x) <= 4) / dataSize * 100, 4)
        print(f'pcTholdWA:{self.pcTholdWA}, pcTholdTF:{self.pcTholdTF}, pcTholdRHI:{self.pcTholdRHI}, '
              f'pcTholdATI:{self.pcTholdATI}, pcTholdVPE:{self.pcTholdVPE}, pcTholdSTID:{self.pcTholdSTID}')
        print(f'AveTF:{self.AveTF}, MinTF:{self.MinTF}, MaxTF:{self.MaxTF}')

        self.exceedWA = round(float(self.AveWA) - 0.8, 4)
        self.exceedTF = round((0.75 - float(self.AveTF)), 4)
        self.exceedRHI = round((self.AveRHI - 60.0), 4)
        self.exceedATI = round((15.5 - self.AveATI), 4)
        self.exceedVPE = round((self.AveVPE - 0.6), 4)
        self.exceedSTID = round((4 - self.AveDifSTID), 4)

        self.impactScoreWA = self.impactScore(self.pcTholdWA, self.exceedWA, 1.0, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4)
        self.impactScoreTF = self.impactScore(self.pcTholdTF, self.exceedTF, 1.0, 0.1, 0.0, -0.05, -0.1, -0.15, -0.2)
        self.impactScoreRHI = self.impactScore(self.pcTholdRHI, self.exceedRHI, 1.0, 20.0, 10.0, 0.0, -15.0, -25.0,
                                               -30.0)
        self.impactScoreATI = self.impactScore(self.pcTholdATI, self.exceedATI, 1.0, 2.0, 0.0, -2.0, -4.0, -6.0, -8.0)
        self.impactScoreVPE = self.impactScore(self.pcTholdVPE, self.exceedVPE, 1.0, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4)
        self.impactScoreSTID = self.impactScore(self.pcTholdSTID, self.exceedSTID, 0.5, 2.0, 0.0, -2.0, -4.0, -6.0,
                                                -9.0)
        self.impactScoreMould = self.impactScoreWA
        self.impactScoreSCD = self.impactScoreSTID
        print(f"IMPACT-Score impactScoreWA={self.impactScoreWA}, impactScoreTF={self.impactScoreTF}, "
              f"impactScoreRHI={self.impactScoreRHI}, impactScoreATI={self.impactScoreATI}, "
              f"impactScoreVPE={self.impactScoreVPE}, impactScoreSTID={self.impactScoreSTID}")

        # global bmiScoreEnvelope, bmiScoreHeating, bmiScoreVentilation, bmiTotal

        self.bmiScoreEnvelope = (self.bmiScore(self.impactScoreWA) + self.bmiScore(self.impactScoreTF)) / 2
        self.bmiScoreHeating = (self.bmiScore(self.impactScoreRHI) + self.bmiScore(self.impactScoreATI)) / 2
        self.bmiScoreVentilation = (self.bmiScore(self.impactScoreWA) + self.bmiScore(self.impactScoreVPE)) / 2
        print(f'BMIScore bmiScore(impactScoreWA)={self.bmiScore(self.impactScoreWA)}, '
              f'bmiScore(impactScoreTF)={self.bmiScore(self.impactScoreTF)}, '
              f'bmiScore(impactScoreRHI)={self.bmiScore(self.impactScoreRHI)},'
              f'bmiScore(impactScoreATI)={self.bmiScore(self.impactScoreATI)}, '
              f'bmiScore(impactScoreVPE)={self.bmiScore(self.impactScoreVPE)}')

        self.bmiTotal = (self.bmiScoreEnvelope + self.bmiScoreHeating + self.bmiScoreVentilation) / 3
        print(f'bmiScoreEnvelope={self.bmiScoreEnvelope}, bmiScoreVentilation={self.bmiScoreVentilation}, '
              f'bmiScoreHeating={self.bmiScoreHeating}, bmiTotal={self.bmiTotal}')

        ## From PDF section start
        self.FRE = '30'
        self.BMIT = self.BMIIndex(self.bmiTotal)
        self.BMIE = self.BMIIndex(self.bmiScoreEnvelope)
        self.BMIH = self.BMIIndex(self.bmiScoreHeating)
        self.BMIV = self.BMIIndex(self.bmiScoreVentilation)
        if self.bmiScoreVentilation < 0.5:
            self.BMIVV = 'No'
        else:
            self.BMIVV = self.BMIV

        self.BMIATI = self.BMIIndex(self.impactScoreATI)
        self.BMIRHI = self.BMIIndex(self.impactScoreRHI)
        self.BMIVPE = self.BMIIndex(self.impactScoreVPE)

        if self.impactScoreATI >= 5.5:
            self.LIAT = 'very cold'  # Extremely High
        elif self.impactScoreATI >= 4.5:
            self.LIAT = 'cold'  # Very High
        elif self.impactScoreATI >= 3.5:
            self.LIAT = 'cold'  # High
        elif self.impactScoreATI >= 2.5:
            self.LIAT = 'moderately cool'  # Moderate
        elif self.impactScoreATI >= 1.5:
            self.LIAT = 'warm'  # Low
        elif self.impactScoreATI >= 0.5:
            self.LIAT = 'warm'  # Very Low
        else:
            self.LIAT = 'very warm'  # no impact of

        if self.impactScoreRHI >= 5.5:
            self.HIARH = 'very humid'  # Extremely High
        elif self.impactScoreRHI >= 4.5:
            self.HIARH = 'humid'  # Very High
        elif self.impactScoreRHI >= 3.5:
            self.HIARH = 'humid'  # High
        elif self.impactScoreRHI >= 2.5:
            self.HIARH = 'moderately humid'  # Moderate
        elif self.impactScoreRHI >= 1.5:
            self.HIARH = 'dry'  # Low
        elif self.impactScoreRHI >= 0.5:
            self.HIARH = 'dry'  # Very Low
        else:
            self.HIARH = 'very dry'  # no impact of

        if self.impactScoreTF > 3:
            self.FRSIE = 'problematic'  # inappropriate
        else:
            self.FRSIE = 'no problematic'  # appropriate

        # if self.impactScoreWA > 3:
        #     self.AWSUIT = 'is'
        # else:
        #     self.AWSUIT = 'is not'

        # if self.impactScoreWA > 3:
        if self.bmiScoreEnvelope > 3:
            self.AWSUIT = 'present'
        else:
            self.AWSUIT = 'do not present'

        if self.AveDifSTID < 0:
            self.AveSurT: str = '{AveDifSTID}°C below'
        else:
            self.AveSurT: str = '{AveDifSTID}°C above'
        self.AveSurT = self.AveSurT.format(AveDifSTID=str(round(self.AveDifSTID, 1)))

        self.BMITS = "{:.1f}".format(self.bmiTotal)
        self.BMIES = "{:.1f}".format(self.bmiScoreEnvelope)
        self.BMIVS = "{:.1f}".format(self.bmiScoreVentilation)
        self.BMIHS = "{:.1f}".format(self.bmiScoreHeating)

        self.figure1FileName = f'imgs/Fig1{self.suffix}.png'
        self.figure2FileName = f'imgs/Fig2{self.suffix}.png'
        self.figure3FileName = f'imgs/Fig3{self.suffix}.png'
        self.figure4FileName = f'imgs/Fig4{self.suffix}.png'
        self.figure6FileName = f'imgs/Fig6{self.suffix}.png'
        self.table1cFileName = f"imgs/Tab1{self.suffix}C.png"
        self.table2CFileName = f"imgs/Tab2{self.suffix}C.png"
        self.table1FileName = f"imgs/Tab1{self.suffix}.png"
        print(f'self.figure1FileName={self.figure1FileName},self.figure2FileName={self.figure2FileName}')
        print(f'self.figure3FileName={self.figure3FileName},self.figure4FileName={self.figure4FileName}')
        print(f'self.figure6FileName={self.figure6FileName},self.table1cFileName={self.table1cFileName}')
        print(f'self.table2CFileName={self.table2CFileName},self.table1FileName={self.table1FileName}')
        self.gen_figure1(filename=self.figure1FileName)
        self.gen_figure2(filename=self.figure2FileName)
        self.gen_figure3(filename=self.figure3FileName)
        self.gen_figure4(filename=self.figure4FileName)
        self.gen_figure6(filename=self.figure6FileName)
        self.gen_figure10(filename=self.table1cFileName)
        self.gen_table2c(filename=self.table2CFileName)
        self.gen_table1(filename=self.table1FileName)

    def gen_figure1(self, filename=None):
        fig1 = plt.figure(figsize=(10, 6), dpi=180)  # Fig. 1 Thermal Envelope Performance
        # plt.grid(True)
        ax = fig1.add_subplot(1, 1, 1)

        # Major ticks every 20, minor ticks every 5
        major_ticks = np.arange(0, 1.01, 0.2)
        minor_ticks = np.arange(0, 1.01, 0.05)

        ax.set_xticks(major_ticks)
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_yticks(major_ticks)
        ax.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
        ax.grid(which='both')

        # Or if you want different settings for the grids:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        ax.scatter(self.WA, self.TF, zorder=10)
        # ax.plot([0,1],[0.75,0.75])
        # ax.plot([0.8,0.8],[0,1])
        ax.axis([0, 1, 0, 1])
        ax.set_ylabel('T Factor (fR$_{si}$)', fontsize=14)
        ax.set_xlabel('Water Activity(a$_w$)', fontsize=14)
        plt.title(f'Figure 1{self.suffix} Thermal Envelope Performance', fontweight='bold', fontsize=14)

        ax.text(0.01, 0.58, '6-EH', fontsize=15)
        ax.text(0.01, 0.68, '5-VH', fontsize=15)
        ax.text(0.01, 0.75, '4-H', fontsize=15)
        ax.text(0.01, 0.80, '3-M', fontsize=15)
        ax.text(0.01, 0.85, '2-L', fontsize=15)
        ax.text(0.01, 0.90, '1-VL', fontsize=15)
        ax.text(0.01, 0.95, '0-NI', fontsize=15)

        ax.text(0.92, 0.01, '6-EH', fontsize=15)
        ax.text(0.82, 0.01, '5-VH', fontsize=15)
        ax.text(0.73, 0.01, '4-H', fontsize=15)
        ax.text(0.63, 0.01, '3-M', fontsize=15)
        ax.text(0.53, 0.01, '2-L', fontsize=15)
        ax.text(0.42, 0.01, '1-VL', fontsize=15)
        ax.text(0.32, 0.01, '0-NI', fontsize=15)

        ax.text(0.2, 0.8, 'No Mould', {'color': '#865229', 'fontsize': 20}, zorder=15)
        ax.text(0.7, 0.55, ' Mould', {'color': 'w', 'fontsize': 20}, zorder=15)
        ax.text(0.7, 0.45, ' Growth', {'color': 'w', 'fontsize': 20}, zorder=15)

        #     ax.arrow(0.81,0.10,0.16,0,color='#FF7272',lw=10)

        # orange color block
        # ax.plot([0,1],[0.75,0.75],'#FFB657',lw=5)
        ax.plot([0, 1], [0.575, 0.575], '#daa30a', lw=50, alpha=0.7)
        ax.plot([0, 1], [0.7, 0.7], '#daa30a', lw=33, alpha=0.6)
        ax.plot([0, 1], [0.775, 0.775], '#daa30a', lw=16.5, alpha=0.5)
        ax.plot([0, 1], [0.825, 0.825], '#daa30a', lw=16.5, alpha=0.4)
        ax.plot([0, 1], [0.875, 0.875], '#daa30a', lw=16.5, alpha=0.3)
        ax.plot([0, 1], [0.925, 0.925], '#daa30a', lw=16.5, alpha=0.2)
        ax.plot([0, 1], [0.975, 0.975], '#daa30a', lw=16.5, alpha=0.1)

        # blue Block
        # ax.plot([0.8,0.8],[0,1],'#57C6EF',lw=5)
        ax.plot([0.95, 0.95], [0, 1], '#8c97c2', lw=56, alpha=0.7)
        ax.plot([0.85, 0.85], [0, 1], '#8c97c2', lw=56, alpha=0.6)
        ax.plot([0.75, 0.75], [0, 1], '#8c97c2', lw=56, alpha=0.5)
        ax.plot([0.65, 0.65], [0, 1], '#8c97c2', lw=56, alpha=0.4)
        ax.plot([0.55, 0.55], [0, 1], '#8c97c2', lw=56, alpha=0.3)
        ax.plot([0.45, 0.45], [0, 1], '#8c97c2', lw=56, alpha=0.2)
        ax.plot([0.35, 0.35], [0, 1], '#8c97c2', lw=56, alpha=0.1)

        # plt.savefig("imgs/Fig1.png")
        if filename:
            plt.savefig(filename)
        else:
            plt.savefig("imgs/Fig1.png")

    def gen_figure2(self, filename=None):

        fig2 = plt.figure(figsize=(10, 6), dpi=180)  # Fig. 2 Ventilation
        # plt.grid(True)
        ax = fig2.add_subplot(1, 1, 1)

        # Major ticks every 20, minor ticks every 5
        major_ticks = np.arange(0, 1.01, 0.2)
        minor_ticks = np.arange(0, 1.01, 0.05)

        ax.set_xticks(major_ticks)
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_yticks(major_ticks)
        ax.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
        ax.grid(which='both')

        # Or if you want different settings for the grids:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        ax.scatter(self.VPE, self.WA, zorder=10)

        ax.axis([0, 1, 0, 1])

        ax.set_xlabel('VPE(vapour pressure excess)(kPa)', fontsize=14)
        ax.set_ylabel('Water Activity(a$_w$)', fontsize=14)
        plt.title(f'Figure 2{self.suffix} Ventilation', fontweight='bold', fontsize=14)

        ax.text(0.01, 0.92, '6-EH', fontsize=15)
        ax.text(0.01, 0.82, '5-VH', fontsize=15)
        ax.text(0.01, 0.72, '4-H', fontsize=15)
        ax.text(0.01, 0.62, '3-M', fontsize=15)
        ax.text(0.01, 0.52, '2-L', fontsize=15)
        ax.text(0.01, 0.42, '1-VL', fontsize=15)
        ax.text(0.01, 0.32, '0-NI', fontsize=15)

        ax.text(0.82, 0.01, '6-EH', fontsize=15)
        ax.text(0.62, 0.01, '5-VH', fontsize=15)
        ax.text(0.53, 0.01, '4-H', fontsize=15)
        ax.text(0.43, 0.01, '3-M', fontsize=15)
        ax.text(0.33, 0.01, '2-L', fontsize=15)
        ax.text(0.22, 0.01, '1-VL', fontsize=15)
        ax.text(0.12, 0.01, '0-NI', fontsize=15)

        ax.text(0.1, 0.3, 'No trapped moisture', {'color': '#865229', 'fontsize': 20}, zorder=15)
        ax.text(0.6, 0.7, 'Trapped moisture', {'color': '#FFFFFF', 'fontsize': 20}, zorder=15)

        # orange color block

        # ax.plot([0,1],[0.8,0.8],'#FFB657',lw=5)
        ax.plot([0, 1], [0.95, 0.95], '#8c97c2', lw=33, alpha=0.7)
        ax.plot([0, 1], [0.85, 0.85], '#8c97c2', lw=33, alpha=0.6)
        ax.plot([0, 1], [0.75, 0.75], '#8c97c2', lw=33, alpha=0.5)
        ax.plot([0, 1], [0.65, 0.65], '#8c97c2', lw=33, alpha=0.4)
        ax.plot([0, 1], [0.55, 0.55], '#8c97c2', lw=33, alpha=0.3)
        ax.plot([0, 1], [0.45, 0.45], '#8c97c2', lw=33, alpha=0.2)
        ax.plot([0, 1], [0.35, 0.35], '#8c97c2', lw=33, alpha=0.1)

        # blue Block
        # ax.plot([0.6,0.6],[0,1],'#57C6EF',lw=5)
        ax.plot([0.85, 0.85], [0, 1], '#8c97c2', lw=170, alpha=0.7)
        ax.plot([0.65, 0.65], [0, 1], '#8c97c2', lw=56, alpha=0.6)
        ax.plot([0.55, 0.55], [0, 1], '#8c97c2', lw=56, alpha=0.5)
        ax.plot([0.45, 0.45], [0, 1], '#8c97c2', lw=56, alpha=0.4)
        ax.plot([0.35, 0.35], [0, 1], '#8c97c2', lw=56, alpha=0.3)
        ax.plot([0.25, 0.25], [0, 1], '#8c97c2', lw=56, alpha=0.2)
        ax.plot([0.15, 0.15], [0, 1], '#8c97c2', lw=56, alpha=0.1)

        if filename:
            plt.savefig(filename)
        else:
            plt.savefig("imgs/Fig2.png")

    def gen_figure3(self, filename=None):

        fig3 = plt.figure(figsize=(10, 6), dpi=180)  # Fig. 3 Heat-Moisture Regime

        # plt.grid(True)
        ax = fig3.add_subplot(1, 1, 1)

        # Major ticks every 20, minor ticks every 5
        major_ticksy = np.arange(0, 101, 20)
        minor_ticksy = np.arange(0, 101, 5)
        major_ticksx = np.arange(0, 31, 5)
        minor_ticksx = np.arange(0, 31, 1)
        ax.set_xticks(major_ticksx)
        ax.set_xticks(minor_ticksx, minor=True)
        ax.set_yticks(major_ticksy)
        ax.set_yticks(minor_ticksy, minor=True)

        # And a corresponding grid
        ax.grid(which='both')

        # Or if you want different settings for the grids:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        ax.scatter(self.ATI, self.RHI, zorder=10)

        ax.axis([0, 30, 0, 100])

        ax.set_ylabel('RHi$_{air}$(indooor air relative humidity)(%)', fontsize=14)
        ax.set_xlabel('Ti$_{air}$(indoor air temperature)(°C)', fontsize=14)
        plt.title(f'Figure 3{self.suffix} Heat-Moisture Regime', fontweight='bold', fontsize=14)

        ax.text(0.3, 82, '6-EH', fontsize=15)
        ax.text(0.3, 72, '5-VH', fontsize=15)
        ax.text(0.3, 62, '4-H', fontsize=15)
        ax.text(0.3, 52, '3-M', fontsize=15)
        ax.text(0.3, 42, '2-L', fontsize=15)
        ax.text(0.3, 32, '1-VL', fontsize=15)
        ax.text(0.3, 22, '0-NI', fontsize=15)

        ax.text(10.5, 1, '6-EH', fontsize=15)
        ax.text(13.2, 1, '5-VH', fontsize=15)
        ax.text(15.8, 1, '4-H', fontsize=15)
        ax.text(18.4, 1, '3-M', fontsize=15)
        ax.text(21, 1, '2-L', fontsize=15)
        ax.text(23.5, 1, '1-VL', fontsize=15)
        # ax.text(27.5, 1, '0-NI',fontsize=20)

        ax.text(3, 25, 'Cold & Dry', {'color': '#8c97c2', 'fontsize': 20}, zorder=15)
        ax.text(20, 25, 'Warm & Dry', {'color': '#865229', 'fontsize': 20}, zorder=15)
        ax.text(3, 80, 'Cold & Humid', {'color': '#ffffff', 'fontsize': 20}, zorder=15)
        ax.text(20, 80, 'Warm & Humid', {'color': '#ffffff', 'fontsize': 20}, zorder=15)

        # ax.plot([0,30],[60,60])
        # ax.plot([17.5,17.5],[0,100])

        # orange color block
        # ax.plot([0,30],[60,60],'#FFB657',lw=5)
        ax.plot([0, 30], [95, 95], '#8c97c2', lw=33, alpha=0.7)
        ax.plot([0, 30], [85, 85], '#8c97c2', lw=33, alpha=0.6)
        ax.plot([0, 30], [75, 75], '#8c97c2', lw=33, alpha=0.5)
        ax.plot([0, 30], [65, 65], '#8c97c2', lw=33, alpha=0.4)
        ax.plot([0, 30], [55, 55], '#8c97c2', lw=33, alpha=0.3)
        ax.plot([0, 30], [45, 45], '#8c97c2', lw=33, alpha=0.2)
        ax.plot([0, 30], [35, 35], '#8c97c2', lw=33, alpha=0.1)

        # blue Block
        # ax.plot([17.5,17.5],[0,100],'#57C6EF',lw=5)
        ax.plot([11.5, 11.5], [0, 100], '#daa30a', lw=56, alpha=0.6)
        ax.plot([14.25, 14.25], [0, 100], '#daa30a', lw=48, alpha=0.5)
        ax.plot([16.75, 16.75], [0, 100], '#daa30a', lw=48, alpha=0.4)
        ax.plot([19.25, 19.25], [0, 100], '#daa30a', lw=48, alpha=0.3)
        ax.plot([21.75, 21.75], [0, 100], '#daa30a', lw=48, alpha=0.2)
        ax.plot([24.5, 24.5], [0, 100], '#daa30a', lw=56, alpha=0.1)

        if filename:
            plt.savefig(filename)
        else:
            plt.savefig("imgs/Fig3.png")

    def gen_figure4(self, filename=None):

        fig4 = plt.figure(figsize=(10, 7.5), dpi=180)  # ATI, DPI, STI and ATO for Fig. 4 Temperature & Humidity graph

        ax1 = fig4.subplots()
        color = 'tab:red'
        ax1.set_xlabel('Date', fontsize=14)
        ax1.set_ylabel('Temperature, Dew Point(°C)', fontsize=14)
        lns1 = ax1.plot(self.TI, self.ATI, '#D56716', linewidth=1.0, label='IndoorAirTemp')
        lns2 = ax1.plot(self.TI, self.DPI, 'c', linewidth=1.0, label='IndoorDewPoint')
        lns3 = ax1.plot(self.TI, self.STI, 'y', linewidth=1.0, label='SurfaceTemp')
        lns4 = ax1.plot(self.TI, self.ATO, 'r', linewidth=1.0, label='OutdoorAirTemp')
        plt.xticks(rotation=30)

        ax1.tick_params(axis='y', labelcolor=color)
        plt.ylim(-20, 80)
        # plt.axis([0, 700, -10, 50])
        # legend = plt.legend(bbox_to_anchor=(1.35,0.3),loc='right', fontsize=14)
        major_ticks = np.arange(-20, 81, 20)
        minor_ticks = np.arange(-20, 81, 5)
        dloc = DayLocator()
        hloc = HourLocator()

        ax1.set_yticks(major_ticks)
        ax1.set_yticks(minor_ticks, minor=True)
        ax1.xaxis.set_major_locator(dloc)
        # And a corresponding grid
        ax1.grid(which='both')
        ax1.grid(True)
        # Or if you want different settings for the grids:
        ax1.grid(which='minor', alpha=0.2)
        ax1.grid(which='major', alpha=0.5)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:blue'
        ax2.set_ylabel('Relative Humidity(%)', fontsize=14)  # we already handled the x-label with ax1
        lns5 = ax2.plot(self.TI, self.RHI, '#2D64E1', linewidth=1.0, label='IndoorRH')
        lns6 = ax2.plot(self.TI, self.RHO, '#14178A', linewidth=1.0, label='OutdoorRH')
        ax2.xaxis.set_major_locator(dloc)
        ax2.tick_params(axis='y', labelcolor=color)
        plt.ylim(0, 100)

        lns = lns1 + lns2 + lns3 + lns4 + lns5 + lns6
        labs = [l.get_label() for l in lns]
        plt.title(f'Figure 4{self.suffix} Temperature & Humidity', fontweight='bold', fontsize=14)

        fig4.legend(lns, labs, bbox_to_anchor=(0., 0.93, 1, .1), loc='lower center', ncol=3, mode="tight",
                    borderaxespad=0.)
        if filename:
            plt.savefig(filename)
        else:
            plt.savefig(f'imgs/Fig4{self.suffix}.png')

    def gen_figure6(self, filename=None):
        fig6 = plt.figure(figsize=(10, 6), dpi=180)  # Thermal vs moisture graph
        dloc = DayLocator()
        major_ticks = np.arange(0, 2.1, 0.1)
        minor_ticks = np.arange(0, 2.1, 0.05)
        ax1 = fig6.subplots()
        ax1.set_yticks(major_ticks)
        ax1.set_yticks(minor_ticks, minor=True)
        ax1.set_xticks(major_ticks)
        ax1.set_xticks(minor_ticks, minor=True)
        # And a corresponding grid
        ax1.grid(which='both')
        ax1.xaxis.set_major_locator(dloc)
        # Or if you want different settings for the grids:
        ax1.grid(which='minor', alpha=0.2)
        ax1.grid(which='major', alpha=0.5)
        color = 'tab:red'
        ax1.set_xlabel('Date', fontsize=14)
        ax1.set_ylabel('Vapour Pressure(kPa)', fontsize=14)
        lns1 = plt.plot(self.TI, self.VPI, 'cornflowerblue', linewidth=1.0, label='Vpi')
        lns2 = plt.plot(self.TI, self.VPO, 'navy', linewidth=1.0, label='Vpo')
        plt.ylim(0, 2)
        plt.xticks(rotation=30)

        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:blue'
        ax2.set_ylabel('Water Activity & Temperature Factor', fontsize=14)  # we already handled the x-label with ax1
        lns3 = plt.plot(self.TI, self.WA, 'b', linewidth=1.0, label='Water Activity')
        lns4 = plt.plot(self.TI, self.TF, 'fuchsia', linewidth=1.0, label='Temperature Factor')
        plt.ylim(0, 1)
        ax2.xaxis.set_major_locator(dloc)
        ax2.tick_params(axis='y', labelcolor=color)
        #
        lns = lns1 + lns2 + lns3 + lns4
        labs = [l.get_label() for l in lns]
        fig6.legend(lns, labs, bbox_to_anchor=(0., 0.92, 1, .1), loc='lower center', ncol=4, mode="tight",
                    borderaxespad=0.)
        plt.title(f'Figure 5{self.suffix}. Thermal and moisture related parameters', fontweight='bold')
        plt.subplots_adjust(left=0.1, bottom=0.15, right=0.9, top=0.85, wspace=0, hspace=0)
        # plt.savefig(f"imgs/Fig6{self.prefix}.png")
        if filename:
            plt.savefig(filename)
        else:
            plt.savefig(f"imgs/Fig6{self.suffix}.png")
        # TBC morris 26 Jul

    def gen_figure10(self, filename=None):

        fig10 = plt.figure(dpi=160, figsize=(12, 2))  # Table 2

        ax = fig10.add_subplot()

        table_data = [
            ["Conditions", "Indoor Air T(°C)", "Indoor RH(%)", "Surface T(°C)", "Outdoor Air T(°C)", "Outdoor RH(%)",
             "Dew P(°C)", "Surface T-Dew(°C)"],
            ["Average", round(self.AveATI, 1), round(self.AveRHI, 1), round(self.AveSTI, 1), round(self.AveATO, 1),
             round(self.AveRHO, 1),
             round(self.AveDPI, 1), round(self.AveDifSTID, 1)],
            ["Max", round(self.MaxATI, 1), round(self.MaxRHI, 1), round(self.MaxSTI, 1), round(self.MaxATO, 1),
             round(self.MaxRHO, 1),
             round(self.MaxDPI, 1), round(self.MaxDifSTID, 1)],
            ["Min", round(self.MinATI, 1), round(self.MinRHI, 1), round(self.MinSTI, 1), round(self.MinATO, 1),
             round(self.MinRHO, 1),
             round(self.MinDPI, 1), round(self.MinDifSTID, 1)],

        ]

        table = ax.table(cellText=table_data, rowLoc='center', colLoc='center', cellLoc='center', loc='center')
        table.scale(1.25, 2)

        ax.axis('off')
        table.auto_set_font_size(False)
        table.set_fontsize(11.5)  # original is 14
        plt.title(
            f'Table 2{self.suffix} Average environmental parameters gathered by the sensors. See Section 6 Symbols and definitions.',
            fontweight='bold')
        if filename:
            plt.savefig(filename)
        else:
            plt.savefig("imgs/Tab1C.png")

    def gen_table2c(self, filename=None):

        fig11 = plt.figure(dpi=160, figsize=(11, 2))  # Table 3

        ax = fig11.add_subplot()

        table_data = [
            ["Conditions", "Water Activity", "T Factor", "Vpi(kPa)", "Vpo(kPa)", "VPE(kPa)"],
            ["Average", '{0:.2f}'.format(self.AveWA), '{0:.2f}'.format(self.AveTF), round(self.AveVPI, 1),
             round(self.AveVPO, 1),
             round(self.AveVPE, 1)],
            ["Max", '{0:.2f}'.format(self.MaxWA), '{0:.2f}'.format(self.MaxTF), round(self.MaxVPI, 1),
             round(self.MaxVPO, 1),
             round(self.MaxVPE, 1)],
            ["Min", '{0:.2f}'.format(self.MinWA), '{0:.2f}'.format(self.MinTF), round(self.MinVPI, 1),
             round(self.MinVPO, 1),
             round(self.MinVPE, 1)],
        ]

        table = ax.table(cellText=table_data, rowLoc='center', colLoc='center', cellLoc='center', loc='center')
        table.scale(1.2, 2)

        ax.axis('off')
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        plt.title(f'Table 3{self.suffix} Average calculated parameters from raw data', fontweight='bold')
        if filename:
            plt.savefig(filename)
        else:
            plt.savefig("imgs/Tab2C.png")

    def gen_table1(self, filename=None):
        a = [["Envelope", "", "", "", "", "", "", "", ""], ["Ventilation", "", "", "", "", "", "", "", ""],
             ["Heating", "", "", "", "", "", "", "", ""], ["Total BMI Imbalance", "", "", "", "", "", "", "", ""]]
        a[0][8] = "{:.1f}".format(self.bmiScoreEnvelope)
        a[2][8] = "{:.1f}".format(self.bmiScoreHeating)
        a[1][8] = "{:.1f}".format(self.bmiScoreVentilation)
        a[3][8] = "{:.1f}".format(self.bmiTotal)

        def bmi2Level(bmiIndex):
            bmiLevel = 0
            if bmiIndex >= 5.5:
                bmiLevel = 6
            elif bmiIndex >= 4.5:
                bmiLevel = 5
            elif bmiIndex >= 3.5:
                bmiLevel = 4
            elif bmiIndex >= 2.5:
                bmiLevel = 3
            elif bmiIndex >= 1.5:
                bmiLevel = 2
            elif bmiIndex >= 0.5:
                bmiLevel = 1
            else:
                bmiLevel = 0
            return bmiLevel

        def bmiTableSet(bmiScoreEnvelope, bmiScoreVentilation, bmiScoreHeating, bmiTotal):
            levelStr = ['NI', 'VL', 'L', 'M', 'H', 'VH', 'EH']

            levelEnvelop = bmi2Level(bmiScoreEnvelope)
            levelVentilation = bmi2Level(bmiScoreVentilation)
            levelHeating = bmi2Level(bmiScoreHeating)
            levelTota = bmi2Level(bmiTotal)
            a[0][levelEnvelop + 1] = levelStr[levelEnvelop]
            a[1][levelVentilation + 1] = levelStr[levelVentilation]
            a[2][levelHeating + 1] = levelStr[levelHeating]
            a[3][levelTota + 1] = levelStr[levelTota]
            return a

        impactLevel = ['CAUSAL FACTORS', 'No Impact', 'Very Low', 'Low', 'Moderate', 'High', 'Very High', 'Extreme H',
                       'BMI']
        impactFactor = ['Envelope', 'Ventilation', 'Heating', 'Total']

        a[:][0] = impactFactor
        bmiTableSet(self.bmiScoreEnvelope, self.bmiScoreVentilation, self.bmiScoreHeating, self.bmiTotal)

        contentColors = [["w", "darkgreen", "green", "lightgreen", "darkorange", "coral", "red", "darkred", "w"],
                         ["w", "darkgreen", "green", "lightgreen", "darkorange", "coral", "red", "darkred", "w"],
                         ["w", "darkgreen", "green", "lightgreen", "darkorange", "coral", "red", "darkred", "w"],
                         ["w", "w", "w", "w", "w", "w", "w", "w", "w"]]

        fig9 = plt.figure(figsize=(12, 2.5), dpi=160)  # Table 1
        ax = fig9.add_subplot(1, 1, 1)
        table = ax.table(cellText=a, colLabels=impactLevel, cellColours=contentColors, rowLoc='center', colLoc='center',
                         cellLoc='center', loc='center')

        table.auto_set_column_width(0)

        table.scale(1.1, 2)
        ax.axis('off')
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        plt.title(f'Table 1{self.suffix} Building Moisture Index (BMI): imbalance scores')
        if filename:
            plt.savefig(filename)
        else:
            plt.savefig("imgs/Tab1.png")


def RPTGen(datafiles, surveyor, inspectiontime, company, Address,
           occupied, monitor_time, occupied_during_all_monitoring, occupant_number, Problem_rooms, Monitor_areas, moulds, Image_property, room_pictures,
           Image_indoor1, Image_indoor2, Image_indoor3, Image_indoor4,Image_logo, comment, popup=True):
    # global DATA
    import logging
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    app_logger = logging.getLogger(__name__)

    app_logger.debug(datafiles)

    # Add additional debug information as needed
    for file_path in datafiles:
        with open(file_path, 'r') as file:
            app_logger.debug(f"Contents of {file_path}: {file.read()[:500]}")  # Log a snippet of the file

    output_file_name = os.path.join(output_report_dir, "PCA_BMI_Report")

    table_of_content = []

    room_data_list = []

    if len(datafiles) != len(Problem_rooms) or len(datafiles) != len(Monitor_areas):
        print(f'ERROR: Mismatch of input data len(datafiles):{len(datafiles)}, len(Problem_rooms):{len(Problem_rooms)},'
              f'len(Monitor_areas):{len(Monitor_areas)}')
        return
    
    image_list = []

    if Image_property:
        image_list.append([Image_property, 'Outdoor Image'])
    for idx, image in enumerate([Image_indoor1, Image_indoor2, Image_indoor3, Image_indoor4]):
        if image:
            image_list.append([image, f'Indoor Image {idx + 1}'])

    # if Image_property or any([Image_indoor1, Image_indoor2, Image_indoor3, Image_indoor4]):  # Check if there is at least one image
    #     if Image_property:
    #         image_list.append([Image_property, 'Outdoor Image'])
    #     if Image_indoor1:
    #         image_list.append([Image_indoor1, 'Indoor Image'])
    #     if Image_indoor2:
    #         image_list.append([Image_indoor2, 'Indoor Image'])
    #     if Image_indoor3:
    #         image_list.append([Image_indoor3, 'Indoor Image'])
    #     if Image_indoor4:
    #         image_list.append([Image_indoor4, 'Indoor Image'])


        # # Add room images
        # for room_index, room_picture in enumerate(room_pictures):
        #     if room_picture:  # Only if the room image is provided
        #         image_list.append([room_picture, f'Room {room_index + 1} Image'], 'Indoor Image')



    # if len(datafiles) == 1:
    #     output_file_name = datafiles[0]
    #     room_data_list.append(RoomData(datafile=datafiles[0], problem_room=Problem_rooms[0],
    #                                    monitor_area=Monitor_areas[0]))
    # else:
    #     room_no = 0
    #     for datafile in datafiles:
    #         if Problem_rooms[room_no] and Monitor_areas[room_no]:
    #             room_data_list.append(
    #                 RoomData(datafile=datafile, index=room_no + 1, problem_room=Problem_rooms[room_no],
    #                          monitor_area=Monitor_areas[room_no]))
    #         else:
    #             room_data_list.append(RoomData(datafile=datafile, index=room_no))
    #         room_no = room_no + 1

    room_no = 0
    for datafile in datafiles:
        if Problem_rooms[room_no] and Monitor_areas[room_no]:
            room_data_list.append(
                RoomData(datafile=datafile, index=room_no + 1, problem_room=Problem_rooms[room_no],
                         monitor_area=Monitor_areas[room_no]))
        else:
            room_data_list.append(RoomData(datafile=datafile, index=room_no))
        room_no = room_no + 1

    class BasePDF(FPDF):
        grid_line = True

        def header(self):

            if self.grid_line:
                x = 5
                while x < 295:
                    self.dashed_line(5, x, 200, x, 2, 2)
                    x += 5
                y = 5
                while y < 205:
                    self.dashed_line(y, 5, y, 290, 1, 1)
                    y += 5

            if Image_logo != '':
                self.image(Image_logo, 170, 5, 20, 0)

            # UCL.png
            # Arial bold 15
            self.set_font('Arial', 'B', 15)
            self.set_text_color(100, 100, 250)
            self.cell(100, 5, 'Building Moisture Index (BMI)', 0, 1, 'L')
            self.set_font('Arial', 'B', 13)
            self.set_text_color(0, 0, 0)
            self.cell(100, 5, 'Environmental Diagnostic Report', 0, 1, 'L')
            self.line(20, 25, 190, 25)
            # Line break
            self.ln(10)

        def gen_para(self, texts):
            for text in texts:
                self.set_font('', text[1])
                self.write(5, text[0])
            self.write(5, '\n')

    def section4(room_data: RoomData):

        pdf.add_page()

        pdf.ln(5)
        pdf.set_font('Arial', 'B', FontSize.HEADER)

        if room_data.index == 1:
            section4_main_title = '4. RESULTS OF ENVIRONMENTAL MONITORING ASSESSMENT'
            print(f'{section4_main_title} Page no.: {pdf.page_no()}')
            table_of_content.append([section4_main_title, f'{pdf.page_no()}'])
            pdf.cell(70, 8, section4_main_title, 0, 1, 'L', True)

        pdf.ln(5)
        

        suffix = f'{room_data.suffix}'
        section4_title = f'4{suffix}. {room_data.problem_room}'
        print(f'{section4_title} Page no.: {pdf.page_no()}')
        table_of_content.append([section4_title, f'{pdf.page_no()}'])
        pdf.cell(70, 8, section4_title, 0, 1, 'L', True)
        pdf.ln(3)
        pdf.set_font('Arial', '', FontSize.CONTENT)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5,
                       f'Two weeks are considered to be the minimum period of monitoring needed in order formulate an '
                       f'accurate and reliable Building Moisture Index. A report will be created if data sets have been'
                       f' gathered for shorter periods of time, however the user should be aware that accuracy may be '
                       f'compromised when monitoring periods are less than 14 days.',
                       'J')
        # pdf.image(f'imgs/Tab1{prefix}.png', 20, 70, 170)
        # pdf.image(room_data.table1FileName, 20, 70, 170)
        if room_data.index == 1:
            table1_y_offset = 85
        else:
            table1_y_offset = 75
        pdf.image(room_data.table1FileName, 20, table1_y_offset, 170)
        pdf.ln(45)

        pdf.multi_cell(0, 5,
                       f'The analysis of the environmental data gathered from the sensors during {room_data.days} days '
                       f'{room_data.hours} hours (start from {room_data.STDH} until {room_data.EDDH}) period, every {room_data.FRE} mins, '
                       f'shows that the total Building Moisture Index (BMI) in {room_data.NPR} displays a {room_data.BMIT} '
                       f'score ({room_data.BMITS} out of 6.0 BMI-T) of a moisture imbalance environment.', 'J')

        pdf.ln(2)
        pdf.multi_cell(0, 5,
                       f'Impact of causal factors leading to risk of surface condensation and mould growth '
                       f'(Table 1{suffix}):',
                       'J')
        pdf.ln(2)
        pdf.cell(10, 5, '', 0, 0)
        pdf.multi_cell(0, 5, '* Poor Envelope Performance: ' + room_data.BMIE + ' impact ')
        pdf.cell(10, 5, '', 0, 0)
        pdf.multi_cell(0, 5, '* Inadequate Heat-Moisture Regime: ' + room_data.BMIH + ' impact ')
        pdf.cell(15, 5, '', 0, 0)
        pdf.multi_cell(0, 5,
                       '  Low Indoor Air Temperature: ' + room_data.BMIATI + ' impact ' + ' (i.e. ' + room_data.LIAT + ' air)')
        pdf.cell(15, 5, '', 0, 0)
        pdf.multi_cell(0, 5,
                       '  High Indoor Air Relative Humidity: ' + room_data.BMIRHI + ' impact ' + ' (i.e. ' + room_data.HIARH + ' air)')
        pdf.cell(10, 5, '', 0, 0)
        pdf.multi_cell(0, 5, '* Insufficient / Inefficient Ventilation: ' + room_data.BMIVV + ' impact ')
        pdf.ln(4)

        pdf.set_font('Arial', '', FontSize.CONTENT)

        # FRSIE & AWSUIT
        # if self.impactScoreTF > 3:
        #     self.FRSIE = 'problematic'  # inappropriate
        # else:
        #     self.FRSIE = 'no problematic'  # appropriate
        #
        # if self.bmiScoreEnvelope > 3:
        #     self.AWSUIT = 'present'
        # else:
        #     self.AWSUIT = 'do not present'
        if (room_data.impactScoreTF > 3 and room_data.bmiScoreEnvelope <= 3) or \
                (room_data.impactScoreTF <= 3 and room_data.bmiScoreEnvelope > 3):
            # "problematic and do not present" or "no problematic and present "
            # case 2
            mismatch_FRSIE_AWSUIT = True
        else:
            # case 1
            mismatch_FRSIE_AWSUIT = False

        access_4 = f"Table 2{suffix} and Table 3{suffix} show average values of raw and calculated environmental" \
                   f" parameters. The thermal envelope performance graph (Figure 1{suffix}) shows that " \
                   f"most data fall into an area where the temperature factor (T Factor) values ({room_data.AveTF:.2f} average), " \
                   f"can be considered {room_data.FRSIE}. {'However this' if mismatch_FRSIE_AWSUIT else 'This'}, " \
                   f"together with most water activity (aw, surface RH) values " \
                   f"obtained during the recorded period ({room_data.AveWA:.2f} average), {room_data.AWSUIT} a high risk for " \
                   f"condensation and mould growth."
        # access_4 = access_4.format(AveTF=AveTF, FRSIE=FRSIE, AWSUIT=AWSUIT, AveWA=str(AveWA))
        print(f"{'However this' if mismatch_FRSIE_AWSUIT else 'This'} {room_data.FRSIE} {room_data.AWSUIT}")
        pdf.multi_cell(0, 5, access_4, 'J')
        pdf.ln(3)

        access_5 = f'The likelihood of surface condensation occurring is also related to surface temperature ' \
                   f'(Surface T) and dew point (Dew P) temperature differentials (Surface T- Dew P (°C)). ' \
                   f'During the monitoring period, average Surface T is {room_data.AveSurT} Dew P temperature to give rise to ' \
                   f'condensation (Figure 4{suffix} and Table 2{suffix}). The lower this difference the higher ' \
                   f'the risk of surface condensation occurring, which happens when Surface T reaches ' \
                   f'and goes below Dew P temperature.'
        # access_5 = access_5.format(AveSurT=AveSurT)
        pdf.multi_cell(0, 5, access_5, 'J')
        pdf.ln(3)
        # Before 31 Jan 2022 Issue
        # if impactScoreVPE > 3:
        #     VPESEEM = 'seems to be a problem'
        # else:
        #     VPESEEM = 'does not seem to be a problem'
        # 31 Jan 2022 Issue
        if room_data.bmiScoreVentilation >= 3.5:
            VPESEEM = 'seems to be a problem'
        else:
            VPESEEM = 'does not seem to be a problem'

        pdf.multi_cell(0, 5,
                       f'The ventilation, i.e. removal of the moisture produced in this dwelling, {VPESEEM}, with most '
                       f'vapour pressure excess (VPE) and water activity (aw) data (Figure 2{suffix}) showing {room_data.BMIV} '
                       f'score ({room_data.AveVPE} kPa and {room_data.AveWA} average, respectively), in a {room_data.LIAT} ({round(room_data.AveATI, 1)}°C '
                       f'average) and {room_data.HIARH} ({round(room_data.AveRHI, 1)}% average RH) environment (Figure 3{suffix}). '
                       , 'J')

        print(f'pdf start 4{suffix} 2nd page')

        pdf.add_page()
        pdf.ln(1)
        pdf.set_font('Arial', 'B', FontSize.CONTENT)
        pdf.cell(160, 8, ' BMI causal factors graphs', 0, 1, 'C', True)
        pdf.image(room_data.figure1FileName, 37, 40, 130)
        pdf.image(room_data.figure2FileName, 37, 120, 130)
        pdf.image(room_data.figure3FileName, 37, 200, 130)

        # pdf.image(f'imgs/Fig1{prefix}.png', 37, 40, 130)
        # pdf.image(f'imgs/Fig2{prefix}.png', 37, 120, 130)
        # pdf.image(f'imgs/Fig3{prefix}.png', 37, 200, 130)

        print(f'pdf start 4{suffix} 3rd page')

        pdf.add_page()
        pdf.set_font('Arial', 'B', FontSize.CONTENT)
        pdf.cell(160, 8, 'Raw and calculated parameters graphs', 0, 1, 'C', True)

        pdf.image(room_data.figure4FileName, 30, 40, 140)
        pdf.image(room_data.table1cFileName, 25, 148, 150)
        pdf.image(room_data.figure6FileName, 30, 170, 140)
        pdf.image(room_data.table2CFileName, 25, 255, 150)

        # pdf.image(f'imgs/Fig4{prefix}.png', 30, 40, 140)
        # pdf.image(f'imgs/Tab1C{prefix}.png', 25, 148, 150)
        # pdf.image(f'imgs/Fig6{prefix}.png', 30, 170, 140)
        # pdf.image(f'imgs/Tab2C{prefix}.png', 25, 255, 150)

    class PDF(BasePDF):

        # def header(self):
        #     # Logo
        #     # self.image('PCA.png', 140, 8, 12)#zuoshangjiaoyuandian
        #     # self.image('PCA.png', 140, 8, 20)
        #     if Image_logo != '':
        #         self.image(Image_logo, 170, 5, 20, 0)
        #
        #     # UCL.png
        #     # Arial bold 15
        #     self.set_font('Arial', 'B', 15)
        #     # Move to the right
        #     # self.cell(80)
        #     # Title
        #     self.cell(100, 5, 'Building Moisture Index (BMI)', 0, 1, 'L')
        #     self.set_font('Arial', 'B', 13)
        #     self.set_text_color(100, 100, 250)
        #     # self.cell(100, 5, 'Preliminary Results', 0, 1, 'C')
        #     # self.set_font('Times', 'B', 10)
        #     self.cell(100, 5, 'Environmental Diagnostic Report', 0, 1, 'L')
        #     self.line(20, 25, 190, 25)
        #     # Line break
        #     self.ln(10)

        # Page footer
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            self.line(20, 280, 190, 280)
            self.set_font('Arial', 'B', 8)
            self.ln(4)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Page number
            self.cell(0, 5, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
            self.image('imgs/Footer-Logos.png', 150, 282, 40)

    def gen_cover(cover_pdf_file_name):
        cover_pdf = BasePDF()
        cover_pdf.grid_line = False
        cover_pdf.set_left_margin(20)
        cover_pdf.set_right_margin(20)
        print('CoverPage')
        cover_pdf.add_page()
        cover_pdf.image('imgs/Cover_Title-Logo-Label.jpg', 20, 0, 175)
        cover_pdf.ln(140)

        # Line drawing
        cover_pdf.set_fill_color(100, 100, 250)
        line_base_post = 170
        line_offset = 6
        line_no = 0
        while line_no < 5:
            cover_pdf.rect(20, line_base_post + line_offset * line_no, 55, 0.3, style='F')
            line_no += 1

        # Building Professional
        cover_pdf.set_font('Arial', '', FontSize.HEADER)
        cover_pdf.cell(60, 6, 'Building Professional:', 0, 0, 'L')
        cover_pdf.set_font('Arial', '', FontSize.CONTENT)
        cover_pdf.cell(100, 6, surveyor, 0, 1, 'L')
        # Company Name
        cover_pdf.set_font('Arial', '', FontSize.HEADER)
        cover_pdf.cell(60, 6, 'Company Name:', 0, 0, 'L')
        cover_pdf.set_font('Arial', '', FontSize.CONTENT)
        cover_pdf.cell(100, 6, company, 0, 1, 'L')
        # Property Address
        cover_pdf.set_font('Arial', '', FontSize.HEADER)
        cover_pdf.cell(60, 6, 'Property Address:', 0, 0, 'L')
        cover_pdf.set_font('Arial', '', FontSize.CONTENT)
        cover_pdf.cell(100, 6, Address, 0, 1, 'L')
        # Date Of Inspection
        cover_pdf.set_font('Arial', '', FontSize.HEADER)
        cover_pdf.cell(60, 6, 'Date of Inspection:', 0, 0, 'L')
        cover_pdf.set_font('Arial', '', FontSize.CONTENT)
        formatted_inspectiontime = inspectiontime.strftime('%-d %B %Y')
        # formatted_inspectiontime = inspectiontime.strftime('%-d %B %Y %H:%M:%S')
        cover_pdf.cell(60, 6, str(formatted_inspectiontime), 0, 1, 'L')
        # cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=0, link=''):
        # cover_pdf.add_page()
        # cover_pdf.image('imgs/Contents-Page-Index-Image.jpg', 20, 70, 170)
        cover_pdf.add_page()
        cover_pdf.ln(15)
        cover_pdf.set_font('Arial', 'B', FontSize.HEADER)
        cover_pdf.multi_cell(0, 8, 'CONTENTS', 0, 'C')
        cover_pdf.ln(15)
        for item in table_of_content:
            print(f"Table of content: {','.join(item)}")
            cover_pdf.set_font('Arial', '', FontSize.CONTENT)
            cover_pdf.cell(160, 6, f'{item[0]}', 0, 0, 'L')
            cover_pdf.set_font('Arial', '', FontSize.CONTENT)
            cover_pdf.cell(20, 6, f'{item[1]}', 0, 1, 'L')
            cover_pdf.ln(10)
        cover_pdf.output(cover_pdf_file_name, 'F')

    # Debug
    # cover_filename = datafile + "_c_" + dt_string + '.pdf'
    # os.startfile(cover_filename)
    # print('CoverPage End')
    # return

    # Instantiation of inherited class
    pdf = PDF()
    pdf.grid_line = False
    pdf.alias_nb_pages()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    pdf.add_page()
    print(f'1. INTRODUCTION Page no.: {pdf.page_no()}')
    table_of_content.append([f'1. INTRODUCTION', f'{pdf.page_no()}'])
    # class color:
    #     PURPLE = '\033[95m'
    #     CYAN = '\033[96m'
    #     DARKCYAN = '\033[36m'
    #     BLUE = '\033[94m'
    #     GREEN = '\033[92m'
    #     YELLOW = '\033[93m'
    #     RED = '\033[91m'
    #     BOLD = '\033[1m'
    #     UNDERLINE = '\033[4m'
    #     END = '\033[0m'
    #
    # print("The output is:" + color.BOLD + 'Python Programming !' + color.BLUE)

    pdf.set_font('Arial', 'B', FontSize.HEADER)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(170, 8, '1. INTRODUCTION', 0, 1, 'L', True)
    pdf.ln(3)
    pdf.set_font('Arial', '', FontSize.CONTENT)
    pdf.multi_cell(0, 5,
                   'Maple R&D Ltd is a research and development PCA subsidiary company offering innovative diagnostic systems to analyse moisture-related problems in buildings.',
                   'J')
    # intro_2 = [['The ', ''],
    #              ['Building Moisture Index (BMI) diagnostic system ', 'BI'],
    #              ['has been developed by The Property Care association (PCA) and University College London (UCL). It is based on years of research collaboration, is internationally peer-reviewed and has been tested and validated by monitoring numerous private and social properties (including Local authorities, Housing Associations).',
    #                  '']]
    # pdf.gen_para(intro_2)
    pdf.ln(3)

    pdf.multi_cell(0, 5,
                   'The Building Moisture Index (BMI) diagnostic system has been developed by The Property Care association (PCA) and University College London (UCL). It is based on years of research collaboration, is internationally peer-reviewed and has been tested and validated by monitoring numerous private and social properties (including Local authorities, Housing Associations).',
                   'J')
    pdf.image('imgs/Intro_pic.png', 20, 105, 62)
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'The BMI system produces diagnostic reports on indoor air and surface moisture in buildings by processing environmental data. A protocol to install data loggers (environmental sensors) in properties and a novel method integrated in a computer program enables the system to generate autonomous diagnostic reports.',
                   'J')
    pdf.ln(3)
    pdf.set_left_margin(83)

    # intro_4 = [['This technical report consists of several sections which include a description of the BMI method, photos and plans together with details and comments about the property (provided by the surveyor). A summary of results on the moisture diagnostic assessment includes the BMI scores indicating the severity of ', ''],
    #             ['moisture imbalance ', 'BI'],
    #             ['and the ', ''],
    #             ['causal factors ', 'BI'],
    #             ['leading to ', ''],
    #             ['condensation and mould', 'BI'],
    #             ['. This is complemented with tables and graphs showing the representation of all data and averaged values gathered by the loggers.',
    #                  '']]
    # pdf.gen_para(intro_4)
    pdf.multi_cell(0, 5,
                   'This technical report consists of several sections which include a description of the BMI method, photos and plans together with details and comments about the property (provided by the surveyor). A summary of results on the moisture diagnostic assessment includes the BMI scores indicating the severity of moisture imbalance and the causal factors leading to condensation and mould. This is complemented with tables and graphs showing the representation of all data and averaged values gathered by the loggers.',
                   'J')
    pdf.ln(3)

    # intro_5 = [['A user manual is provided for the installation of the data loggers in the property. These sensors gather environmental data every 30 minutes (ambient air-atmospheric relative humidity (', ''],
    #             ['RH', 'I'],
    #             [') and temperature (', ''],
    #             ['T', 'I'],
    #             ['), plus surface ', ''],
    #             ['T', 'I'],
    #             [') in the identified problem room and area of the property, during a minimum period of two weeks. Raw data collected by the sensors is then processed by establishing links through other computed environmental parameters that relate to the root causal factors leading to surface condensation and mould growth.','']
    #         ]
    # pdf.gen_para(intro_5)
    pdf.multi_cell(0, 5,
                   'A user manual is provided for the installation of the data loggers in the property. These sensors gather environmental data every 30 minutes (ambient air-atmospheric relative humidity (RH) and temperature (T), plus surface T) in the identified problem room and area of the property, during a minimum period of two weeks. Raw data collected by the sensors is then processed by establishing links through other computed environmental parameters that relate to the root causal factors leading to surface condensation and mould growth.',
                   'J')
    pdf.set_left_margin(20)
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'The BMI system identifies the severity of the problem based on the objective quantification of atmospheric and surface moisture levels. It analyses the data (critical thresholds and weighted values) to establish the severity and likelihood of moisture imbalance leading to condensation and mould. Provided that the BMI protocol to install the data loggers in the monitored property has been accurately followed, the BMI method provides a quick, accurate and impartial assessment to identify and quantify the root cause of the problem.',
                   'J')
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'Please, note that this report is not a building survey; it complements property inspections. This report is based solely on the data processed from the environmental sensors placed in the dwelling and on the understanding they have not been moved or manipulated.',
                   'J')

    print('pdstartpage1')
    pdf.add_page()
    print(f'2. ENVIRONMENTAL MONITORING AND ASSESSMENT PROCEDURE Page no.: {pdf.page_no()}')
    table_of_content.append([f'2. ENVIRONMENTAL MONITORING AND ASSESSMENT PROCEDURE', f'{pdf.page_no()}'])
    #########################################################################
    # page 1
    pdf.set_font('Arial', 'B', FontSize.HEADER)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(170, 8, '2. ENVIRONMENTAL MONITORING AND ASSESSMENT PROCEDURE', 0, 1, 'L', True)
    pdf.ln(3)
    pdf.set_font('Arial', '', FontSize.CONTENT)
    pdf.multi_cell(0, 5,
                   'Indoor water vapour from day-to-day activities can give rise to condensation on wall or ceiling areas in buildings. A high level of moisture production is a trigger factor which may lead to surface condensation and mould growth resulting in a moisture imbalance environment.',
                   'J')
    pdf.ln(3)
    # pro_2 = [['The environmental sensors (data loggers) gather data which can be used to assess moisture imbalance leading to condensation and mould in dwellings. A minimum set of three data loggers has been installed in the property. A surface ', ''],
    #             ['T ', 'I'],
    #             ['sensor has been located on the area showing the main damp/mould issue or potential problem spot. An ambient ', ''],
    #             ['T-RH ', 'I'],
    #             ['sensor has been installed in the same room while an external sensor has been placed outdoors (inside an open-air protective case) to register the weather conditions during the monitoring period.', '']
    #         ]
    # pdf.gen_para(pro_2)
    pdf.multi_cell(0, 5,
                   'The environmental sensors (data loggers) gather data which can be used to assess moisture imbalance leading to condensation and mould in dwellings. A minimum set of three data loggers has been installed in the property. A surface T sensor has been located on the area showing the main damp/mould issue or potential problem spot. An ambient T-RH sensor has been installed in the same room while an external sensor has been placed outdoors (inside an open-air protective case) to register the weather conditions during the monitoring period.',
                   'J')
    pdf.ln(3)
    # pro_3 = [['Moisture imbalance ', 'BI'],
    #             ['may occur from ', ''],
    #             ['high moisture ', 'BI'],
    #             ['levels and the following ', ''],
    #             ['causal factors', 'BI'],
    #             [':', '']
    #         ]
    # pdf.gen_para(pro_3)
    pdf.multi_cell(0, 5,
                   'Moisture imbalance may occur from high moisture levels and the following causal factors:',
                   'J')
    pdf.set_left_margin(25)
    pdf.ln(3)
    # pro_4 = [['- Poor Building Thermal Envelope Performance ', 'B'],
    #             ['as a whole and/or related to the presence of thermal bridges (cold spots with low surface ', ''],
    #             ['T', 'I'],
    #             [', e.g. concrete lintels, etc.). This involves environmental parameters such as low ', ''],
    #             ['T factors', 'I'],
    #             [' (poor thermal behaviour) and high ', ''],
    #             ['water activity ', 'I'],
    #             ['values (high ', ''],
    #             ['surface RH', 'I'],
    #             [').', '']
    #         ]
    # pdf.gen_para(pro_4)
    pdf.multi_cell(0, 5,
                   '- Poor Building Thermal Envelope Performance as a whole and/or related to the presence of thermal bridges (cold spots with low surface T, e.g. concrete lintels, etc.). This involves environmental parameters such as low T factors (poor thermal behaviour) and high water activity values (high surface RH).',
                   'J')
    pdf.ln(3)
    # pro_5 = [['- Inadequate Heat-Moisture Regime ', 'B'],
    #             ['caused by insufficient or irregular heating, heat loss and/or infiltrations, such as cold air entry through gaps and around thermal bridges. This relates to low ', ''],
    #             ['indoor air T ', 'I'],
    #             ['and high ', ''],
    #             ['indoor air RH ', 'I'],
    #             ['levels.', '']
    #         ]
    # pdf.gen_para(pro_5)
    pdf.multi_cell(0, 5,
                   '- Inadequate Heat-Moisture Regime caused by insufficient or irregular heating, heat loss and/or infiltrations, such as cold air entry through gaps and around thermal bridges. This relates to low indoor air T and high indoor air RH levels.',
                   'J')

    pdf.ln(3)
    # pro_6 = [['- Insufficient Ventilation ', 'B'],
    #             ['related to high indoor vapour pressure excess (', ''],
    #             ['VPE', 'I'],
    #             ['), from internal and external vapour pressure differentials, and high ', ''],
    #             ['surface RH.', 'I']
    #         ]
    # pdf.gen_para(pro_6)
    pdf.multi_cell(0, 5,
                   '- Insufficient Ventilation related to high indoor vapour pressure excess (VPE), from internal and external vapour pressure differentials, and high surface RH.',
                   'J')

    pdf.set_left_margin(20)
    pdf.ln(3)
    # pro_7 = [['Analysis of the data gathered by the sensors helps to identify which (if any) factors, or combination of factors, are the most likely cause/s of any condensation or mould issues. The extent of the ', ''],
    #             ['Impact of each individual causal factor leading to moisture imbalance, condensation and mould ', 'IB'],
    #             [' has been expressed by a numerical moisture impact indicator (', ''],
    #             ['BMI score', 'B'],
    #             ['). The higher the impact the larger the score and the severity of the moisture problem:', '']
    #         ]
    # pdf.gen_para(pro_7)
    pdf.multi_cell(0, 5,
                   'Analysis of the data gathered by the sensors helps to identify which (if any) factors, or combination of factors, are the most likely cause/s of any condensation or mould issues. The extent of the Impact of each individual causal factor leading to moisture imbalance, condensation and mould has been expressed by a numerical moisture impact indicator (BMI score). The higher the impact the larger the score and the severity of the moisture problem:',
                   'J')
    pdf.ln(3)
    pdf.write(5,
              ' -0- No Impact (NI); \n -1- Very Low (VL); \n -2- Low (L); \n -3- Moderate (M); \n -4- High (H); \n -5- Very High (VH);  \n -6- Extremely High (EH)')
    pdf.ln(8)
    # pro_9 = [['The individual impact of each causal factor leading to moisture imbalance is shown in Section 4 ', ''],
    #              ['Results of Environmental Assessment', 'BI'],
    #              [', in the BMI graphs and in Table 1. This Table also shows the combined impact of the various causal factors involved in the assessment (', ''],
    #              ['Total BMI', 'B'],
    #              ['). Table 2 and Table 3 show the average, maximum and minimum values obtained for each environmental parameter considered in the BMI assessment during the recording period.', '']
    #         ]
    # pdf.gen_para(pro_9)
    pdf.multi_cell(0, 5,
                   'The individual impact of each causal factor leading to moisture imbalance is shown in Section 4 Results of Environmental Assessment, in the BMI graphs and in Table 1. This Table also shows the combined impact of the various causal factors involved in the assessment (Total BMI). Table 2 and Table 3 show the average, maximum and minimum values obtained for each environmental parameter considered in the BMI assessment during the recording period.',
                   'J')

    pdf.ln(3)
    # pro_10 = [['Finally, advice on different rectification strategies (based on the results) is provided in Section 5 ', ''],
    #              ['Recommendations', 'BI'],
    #              ['. Definitions and benchmarks for each parameter and causal factor involved in the BMI assessment are explained in Section 6 ', ''],
    #              ['Symbols and Definitions.', 'BI']
    #            ]
    # pdf.gen_para(pro_10)
    pdf.multi_cell(0, 5,
                   'Finally, advice on different rectification strategies (based on the results) is provided in Section 5 Recommendations. Definitions and benchmarks for each parameter and causal factor involved in the BMI assessment are explained in Section 6 Symbols and Definitions.',
                   'J')

    # now = datetime.datetime.now()
    # dt_string = now.strftime("%d%m%Y_%H%M%S")
    # pdf.output(datafile + dt_string + '.pdf', 'F')
    # filename = datafile + dt_string + '.pdf'
    # os.startfile(filename)
    # return

    ################################################################################
    # page 2
    pdf.add_page()
    section3_title = '3. PROPERTY AND SURVEYOR: MOISTURE OBSERVATIONS'
    print(f'{section3_title} Page no.: {pdf.page_no()}')
    table_of_content.append([section3_title, f'{pdf.page_no()}'])
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font('Arial', 'B', FontSize.HEADER)
    pdf.cell(70, 8, section3_title, 0, 1, 'L', True)
    pdf.ln(3)

    def q_and_a(title, answer, label_size):
        pdf.set_font('Arial', 'B', FontSize.CONTENT)
        pdf.cell(label_size, 6, title, 0, 0, 'L')
        pdf.set_font('Arial', '', FontSize.CONTENT)
        pdf.cell(100, 6, answer, 0, 1, 'L')

    def fix_q_and_a(title, answer):
        q_and_a(title, answer, 50)

    # Convert monitor_time if it's a float representing seconds
    if isinstance(monitor_time, float):
        monitor_time = timedelta(seconds=monitor_time)

    days = monitor_time.days
    # hours, remainder = divmod(monitor_time.seconds, 3600)
    # minutes, seconds = divmod(remainder, 60)

    print(f"occupied type: {type(occupied)}")
    print(f"monitor_time type: {type(monitor_time)}")
    print(f"occupant_number type: {type(occupant_number)}")

    fix_q_and_a('Building professional:', surveyor)
    fix_q_and_a('Company Name:', company)

    
    formatted_inspectiontime = inspectiontime.strftime('%-d %B %Y')
    fix_q_and_a('Date of inspection:', formatted_inspectiontime)
    # fix_q_and_a('Date of inspection:', str(inspectiontime))
    fix_q_and_a('Property Address:', Address)
    pdf.ln(10)
    q_and_a('Occupied or empty?:', 'Occupied' if occupied else 'Empty', 70)
    q_and_a('During all monitoring period?:', 'Yes' if occupied_during_all_monitoring else 'No', 70)
    formatted_monitor_time = f"{days} days"
    # formatted_monitor_time = f"{days} days {hours:02} hours {minutes:02} minutes"
    q_and_a('Monitoring period:', str(formatted_monitor_time), 70)
    q_and_a('If occupied, how many occupants?:', str(occupant_number), 70)
    pdf.ln(10)
    fix_q_and_a('Monitored Problem room:', ', '.join(Problem_rooms))
    fix_q_and_a('Monitored Problem area:', ', '.join(Monitor_areas))
    formatted_moulds = ['Yes' if mould == True else 'No' for mould in moulds]
    fix_q_and_a('Is there visible mould?:', ', '.join(formatted_moulds))
    # fix_q_and_a('Is there visible mould?:', ', '.join(map(str, moulds)))

    pdf.set_font('Arial', 'B', FontSize.CONTENT)
    pdf.ln(10)
    pdf.cell(100, 6, 'Comments and additional relevant observations:', 0, 1, 'L')
    pdf.set_font('Arial', '', FontSize.CONTENT)
    pdf.multi_cell(0, 6, comment, 'J')

    print("Full image_list:", image_list)

    if Image_property or any(image_list):  # Check if there is at least one image
        print("Full image_list:", image_list)

        pdf.set_font('Arial', '', FontSize.CONTENT)
        IMAGE_WIDTH = 80
        IMAGE_HEIGHT = 0  # Unspecified, dynamically set based on image aspect ratio
        pdf.add_page()
        image_count = 0
        no_of_image_page = 1

        for image in image_list:
            image_tile = image[1]
            image_file = image[0]
            image_count += 1
            print(f"List of image({image_count}): {','.join(image)}")
            quotient, remainder = divmod(image_count, 4)

            if quotient == no_of_image_page and remainder == 1:
                pdf.add_page()
                no_of_image_page += 1

            if remainder == 1:  # upper left
                pdf.cell(90, 10, image_tile, 0, 0, 'L')
                pdf.image(image_file, 20, 40, IMAGE_WIDTH, IMAGE_HEIGHT)
            elif remainder == 2:  # upper right
                pdf.cell(90, 10, image_tile, 0, 1, 'L')
                pdf.image(image_file, 110, 40, IMAGE_WIDTH, IMAGE_HEIGHT)
            elif remainder == 3:  # lower left
                pdf.ln(110)
                pdf.cell(90, 10, image_tile, 0, 0, 'L')
                pdf.image(image_file, 20, 160, IMAGE_WIDTH, IMAGE_HEIGHT)
            elif remainder == 0:  # lower right
                pdf.cell(90, 10, image_tile, 0, 1, 'L')
                pdf.image(image_file, 110, 160, IMAGE_WIDTH, IMAGE_HEIGHT)
    else:
        pdf.add_page()
        pdf.ln(10)
        pdf.cell(50, 6, 'Some images, drawings, maps or plans could be added to the report in this section', 0, 0, 'L')

        pdf.set_font('Arial', '', FontSize.CONTENT)
        

     # Process each room's data and images
    # for room_index, room_data in enumerate(room_data_list):
    #     # Extract images for the current room
    #     current_room_pictures = room_pictures[room_index] if room_index < len(room_pictures) else []

        # Pass the images to the section4 function to handle them
    for room_data in room_data_list:
        section4(room_data)

    def gen_cause_recommendation_summary(data: RoomData):
        cause_recommendation = None
        c1 = c2 = c3 = c4 = False
        monitor_room = data.problem_room
        recommendation = []
        # moisture_imbalance = data.BMIT.lower()

        # C1 - impactScoreTF
        #
        # C2 - bmiScoreVentilation
        #
        # C3 - impactScoreATI
        #
        # C4 - impactScoreRHI

        if (data.bmiTotal >= 3.5) and \
                (data.impactScoreTF > 3 or data.bmiScoreVentilation > 3 or data.impactScoreATI > 3 or
                 data.impactScoreRHI > 3):  # 'Extremely High'/'Very High'/'High'
            # Case 5
            mould_risk = moisture_imbalance = data.BMIT.lower()
            if data.impactScoreTF > 3:
                c1 = True
                recommendation.append('C1')
            if data.bmiScoreVentilation > 3:
                c2 = True
                recommendation.append('C2')
            if data.impactScoreATI > 3:
                c3 = True
                recommendation.append('C3')
            if data.impactScoreRHI > 3:
                c4 = True
                recommendation.append('C4')

            cause_recommendation = ",".join(recommendation)
        elif data.bmiTotal >= 2.5:  # 'Moderate'
            if (data.impactScoreTF > 3 or data.bmiScoreVentilation > 3 or data.impactScoreATI > 3
                    or data.impactScoreRHI > 3):  # 'Extremely High'/'Very High'/'High'
                # Case 4
                mould_risk = moisture_imbalance = data.BMIT.lower()
                if data.impactScoreTF > 3:
                    c1 = True
                    recommendation.append('C1')
                if data.bmiScoreVentilation > 3:
                    c2 = True
                    recommendation.append('C2')
                if data.impactScoreATI > 3:
                    c3 = True
                    recommendation.append('C3')
                if data.impactScoreRHI > 3:
                    c4 = True
                    recommendation.append('C4')
                cause_recommendation = "Not applicable. Nevertheless, at some point the risk could increase because: " + \
                                       ",".join(recommendation)
            else:
                # Case 3
                mould_risk = moisture_imbalance = data.BMIT.lower()
                cause_recommendation = "Not applicable."

        else:
            moisture_imbalance = "No imbalance"
            if data.bmiTotal < 0.5:
                # total_BMI_store = 'No impact' ==> 'Low'
                mould_risk = "Low"
            else:
                # total_BMI_store = 'Low' or 'Very Low'
                mould_risk = data.BMIT.lower()
            if (data.impactScoreTF > 3 or data.bmiScoreVentilation > 3 or data.impactScoreATI > 3
                    or data.impactScoreRHI > 3):  # 'Extremely High'/'Very High'/'High'
                # Case 2
                if data.impactScoreTF > 3:
                    c1 = True
                    recommendation.append('C1')
                if data.bmiScoreVentilation > 3:
                    c2 = True
                    recommendation.append('C2')
                if data.impactScoreATI > 3:
                    c3 = True
                    recommendation.append('C3')
                if data.impactScoreRHI > 3:
                    c4 = True
                    recommendation.append('C4')
                cause_recommendation = "Not applicable. Nevertheless, at some point the risk could increase because: " + \
                                       ",".join(recommendation)
            else:
                # Case 1
                cause_recommendation = "Not applicable"

        return monitor_room, moisture_imbalance, mould_risk, cause_recommendation, c1, c2, c3, c4

    pdf.add_page()
    section5_title = '5. RECOMMENDATIONS AND LIMITATIONS'
    print(f'{section5_title} Page no.: {pdf.page_no()}')
    table_of_content.append([section5_title, f'{pdf.page_no()}'])

    pdf.ln(5)
    pdf.set_font('Arial', 'B', FontSize.HEADER)
    pdf.cell(70, 8, section5_title, 0, 1, 'L', True)
    pdf.set_font('Arial', '', FontSize.CONTENT)
    # Analysis regarding to the graph

    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'The results presented here have been obtained under the recorded external weather and indoor environmental conditions. The causal factors of moisture imbalance (poor envelope performance, inadequate heating, insufficient ventilation) are dynamic and interrelated. Any significant changes in the living conditions (e.g. increasing moisture production, reducing heating, not opening windows or using extraction fans, increasing occupancy, changing building usage, etc.) can upset the balance increasing the BMI score to higher levels. This could increase surface condensation or mould risk on thermal bridges.',
                   'J')
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'The following recommendations are drawn from the environmental assessment undertaken after monitoring the building. Please refer to Section 4 Results, and Section 6 Symbols and Definitions and review all figures and comments on the data obtained.',
                   'J')

    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'The table below shows the moisture imbalance, risk of surface condensation and mould growth, causes and recommendations on remediation actions for each monitored room.',
                   'J')

    MONITOR_ROOM_WIDTH = 35
    MOSITURE_IMBALANCE_WIDTH = 40
    MOULD_RISK_WIDTH = 30
    NORMAL_HEIGHT = 5
    ONE_HALF_LINE_HEIGHT = 10
    TWO_LINE_HEIGHT = 15
    THREE_LINE_HEIGHT = 20

    def draw_summary_table(monitor_room, moisture_imbalance, mould_risk, cause_recommendation, offset=0):
        if cause_recommendation.find("Not applicable. Nevertheless") != -1:
            # Multi line cell
            height = TWO_LINE_HEIGHT
        else:
            height = NORMAL_HEIGHT
        pdf.cell(MONITOR_ROOM_WIDTH, height, monitor_room, 1, 0, 'L')
        pdf.cell(MOSITURE_IMBALANCE_WIDTH, height, moisture_imbalance, 1, 0, 'L')
        pdf.cell(MOULD_RISK_WIDTH, height, mould_risk, 1, 0, 'L')
        if height != NORMAL_HEIGHT:
            multi_height = NORMAL_HEIGHT
        else:
            multi_height = NORMAL_HEIGHT
        print(f"draw_summary_table height: {height} multi_height: {multi_height}")
        pdf.multi_cell(0, multi_height, cause_recommendation, 1, 'L')
        # pdf.set_font('Arial', '', FontSize.CONTENT)

    monitor_room_list = []
    moisture_imbalance_list = []
    mould_risk_list = []
    cause_recommendation_list = []
    display_c1 = display_c2 = display_c3 = display_c4 = False
    summary = []
    pdf.ln(3)
    pdf.set_font('Arial', 'B', FontSize.CONTENT)
    draw_summary_table("Monitored room", "Moisture Imbalance", "Mould Risk", "Cause and Recommendation")
    pdf.set_font('Arial', '', FontSize.CONTENT)
    for room_data in room_data_list:
        # pdf.set_font('Arial', 'B', FontSize.CONTENT)
        # pdf.cell(160, 8, room_data.problem_room, 0, 1, 'C', True)
        # pdf.set_font('Arial', '', FontSize.CONTENT)
        monitor_room, moisture_imbalance_result, mould_risk_result, cause_recommendation_result, c1_result, \
        c2_result, c3_result, c4_result = gen_cause_recommendation_summary(room_data)
        display_c1 = display_c1 or c1_result
        display_c2 = display_c2 or c2_result
        display_c3 = display_c3 or c3_result
        display_c4 = display_c4 or c4_result
        monitor_room_list.append(monitor_room)
        moisture_imbalance_list.append(moisture_imbalance_result)
        mould_risk_list.append(mould_risk_result)
        cause_recommendation_list.append(cause_recommendation_result)
        summary.append([monitor_room, moisture_imbalance_result, mould_risk_result,
                        '\n'.join(twp.wrap(cause_recommendation_result, 35))])
        draw_summary_table(monitor_room, moisture_imbalance_result, mould_risk_result, cause_recommendation_result)

    pdf.ln(6)

    SHORT_COL_WIDTH = 15
    if display_c1 or display_c2 or display_c3 or display_c4:
        pdf.set_font('Arial', 'B', FontSize.CONTENT)
        pdf.multi_cell(0, NORMAL_HEIGHT, 'Possible causes and recommendations for rectification measures', 1, 'L')
        pdf.set_font('Arial', '', FontSize.CONTENT)
        if display_c1:
            pdf.cell(SHORT_COL_WIDTH, TWO_LINE_HEIGHT, 'C1', 1, 0, 'L')
            pdf.multi_cell(0, NORMAL_HEIGHT,
                           'The temperature factor results indicate that the building envelope performance in the measured area is poor. An investigation of the thermal performance of the walls in this area and surroundings is strongly recommended. ',
                           1, 'L')
        if display_c2:
            pdf.cell(SHORT_COL_WIDTH, TWO_LINE_HEIGHT, 'C2', 1, 0, 'L')
            pdf.multi_cell(0, NORMAL_HEIGHT,
                           'The vapour pressure excess and water activity results indicate that wet air is not being allowed to escape adequately. The existing provision for air exchange and ventilation should be inspected.',
                           1, 'L')
        if display_c3:
            pdf.cell(SHORT_COL_WIDTH, ONE_HALF_LINE_HEIGHT, 'C3', 1, 0, 'L')
            pdf.multi_cell(0, NORMAL_HEIGHT,
                           'The provision for heating is inadequate. This should be checked and improved to ensure the room is warm and adequately heated.',
                           1, 'L')
        if display_c4:
            pdf.cell(SHORT_COL_WIDTH, THREE_LINE_HEIGHT, 'C4', 1, 0, 'L')
            pdf.multi_cell(0, NORMAL_HEIGHT,
                           'The level of moisture in the air is high because of moisture generated from within the building. Steps should be taken to reduce the release of water vapour into the atmosphere. Measures to reduce moisture production may involve simple lifestyle changes which may be also supplemented by improvements of ventilation and heating.',
                           1, 'L')

    pdf.add_page()
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'To maintain a moisture balanced environment, it is essential to ensure that the performance of the thermal envelope, the provision of ventilation and the heating regimes within the dwelling are always adequate.',
                   'J')
    pdf.ln(3)

    pdf.multi_cell(0, 5,
                   "It must be fully appreciated that the areas examined may not fully reflect other areas in the property that were not measured. To confirm the 'whole-house' performance of the thermal envelope, ventilation and heating systems, further inspections would be required.",
                   'J')
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'Please note, this environmental assessment should be used together with a building condition survey. The diagnostic analysis informs and quantifies if condensation is present and may lead to mould growth. Typically, these problems are commonest during winter months (heating season) when cooler outdoor temperatures lead to cold wall surfaces and natural ventilation is less frequent. ',
                   'J')
    pdf.ln(3)
    pdf.multi_cell(0, 5,
                   'Useful tips to reduce condensation and mould risk may involve simple lifestyle changes like modification of the occupants\' activities. Some examples for this could be cooking with pan lids on, opening windows and closing bathroom doors, for drying laundry, or during and after showers, until surfaces get dry, using warm heating sources, allowing space for the air to circulate in and around furniture, etc. Information, education, and long-term collaboration may also prove beneficial.',
                   'J')
    pdf.ln(3)

    pdf.add_page()
    section6_title = '6. SYMBOLS AND DEFINITIONS'
    print(f'{section6_title} Page no.: {pdf.page_no()}')
    table_of_content.append([section6_title, f'{pdf.page_no()}'])
    pdf.image('imgs/symbols.jpg', 0, 0, 200)

    now = datetime.datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M%S")
    cover_pdf_file_name = output_file_name + "_c_" + dt_string + '.pdf'
    gen_cover(cover_pdf_file_name)

    now = datetime.datetime.now()
    #     pdf.output('PCA_Report_V2.0.pdf', 'F')
    dt_string = now.strftime("%d%m%Y_%H%M%S")
    # pdf_name = datafile + '_t_' + dt_string + '.pdf'
    pdf_name = output_file_name + '_t_' + dt_string + '.pdf'
    pdf.output(pdf_name, 'F')
    filename = None  # Initialize to ensure it's always defined

    try:
        print("file1:" + cover_pdf_file_name)
        print("file2:" + pdf_name)

        with open(cover_pdf_file_name, 'rb') as file1, open(pdf_name, 'rb') as file2:
            reader1 = PdfReader(file1)
            reader2 = PdfReader(file2)
            merger = PdfMerger()
            merger.append(reader1)
            merger.append(reader2)

            filename = output_file_name + dt_string + '.pdf'
            with open(filename, 'wb') as output_file:
                merger.write(output_file)
                
         

        # Clean up temporary files
        os.remove(cover_pdf_file_name)
        os.remove(pdf_name)
        print(f"DEBUGGING REPORT PATH IN PCADataTool, filename is: {filename}")
        return filename

    except Exception as e:
        print("Error encountered during pdf merge and deletion: " + str(e))
        filename = None  # Ensure filename is set to None if an error occurs

    # Cross-platform way to open the file
    if filename and os.path.exists(filename):
        print(f"{filename} generation is completed.")
    else:
        print('Failed to generate the report. Please check the logs for more details.')

# RPTGen('SensorsData.xlsx','Surveyor Paula','06/20/2020 16:20:58 ','6 Gower street,WC1E,6BT','2/19/2018  4:00:00 PM', 2,\
# '3/5/2018  3:00:00 PM',500, pd.to_timedelta('1 days 06:05:01.00003'),'Bedroom A','floor',1,'imgs/Property.jpg','imgs/mould.jpeg','imgs/mould.jpeg','imgs/mould.jpeg',\
# 'imgs/Property.jpg','Comments given by the accessor,(200 words)')
