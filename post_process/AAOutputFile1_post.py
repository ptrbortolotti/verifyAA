#########################################################################################################################################

# Created by Matt Phillips
# National Renewable Energy Laboratory
# Summer 2019

#########################################################################################################################################
#########################################################################################################################################

# Processes OpenFAST Aeroacoustic output file number 1 (AAOutputFile1) which gives overall sound pressure level (OASPL) for each observer

#########################################################################################################################################

#packages

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import weio
from parse import *
import re
import matplotlib.colors

#########################################################################################################################################

## User inputs

# location for AAOutputFile1, Test18_OF2, and AA_ObserverLocations files
input_dir = '/Users/pbortolo/work/2_openfast/noise/verifyAA/OpenFAST_IEA_LB_RWT/'
loc_dir = '/Users/pbortolo/work/2_openfast/noise/verifyAA/OpenFAST_IEA_LB_RWT/'

# desired location for processed results
output_dir = "/Users/pbortolo/Dropbox/Writing/NoiseTechReport"

# appended name for AAOutputFile1: (i.e. yaw10deg_AAOutputFile1.out => outputname = "yaw10deg_". Leave outputname = "" if no modification
outputname = ""
AAname = outputname + "AAOutputFile1.out"
OF2name = outputname + "RotorSE_FAST_IEA_landBased_RWT.outb"

# location file name
locname = "AA_ObserverLocations_Map.dat"

# number of revolutions (n) to calculate OASPL
n = 1

# save plot and/or data to output directory?
save_fig = False
save_data = False

#########################################################################################################################################

# produces full file paths
AAfilename = input_dir + '/' + AAname
OF2filename = input_dir + '/' + OF2name
locfilename = loc_dir + '/' + locname
outputfilename = output_dir + '/' + outputname + "AAOutputFile1"

# reads in file data
AA_1 = weio.FASTOutFile(AAfilename).toDataFrame()
OF2 = weio.FASTOutFile(OF2filename).toDataFrame()
location = pd.read_csv(locfilename,delimiter='\s+',skiprows=[0],names=['x','y','z'])

# determine number of observers
num_obs = AA_1.shape[1]-1

# calculate sample time for n revolutions
rpm = OF2[["RotSpeed_[rpm]"]].mean()[0]
yaw = OF2[["YawPzn_[deg]"]].mean()[0] / 180. * np.pi
time_revs = n*60/rpm
tot_time = AA_1["Time_[s]"].max()
if time_revs < tot_time:
    sample_time = tot_time - time_revs
else:
    print("Error: Time for number of revolutions exceeds simulation time. Reduce n.")
    raise SystemExit('')

# slice AA dataframe for t > sample_time
AA_1 = AA_1[AA_1["Time_[s]"] > sample_time]
AA_1=AA_1.drop("Time_[s]",axis=1)

# convert observer Sound Pressure Level (SPL) to Sound Pressure (P)
AA_1 = 10**(AA_1 / 10)

# average P for each observer
AA_1 = AA_1.mean()

# conver back from P to SPL
if any(AA_1[i] == 0 for i in range(0,AA_1.size)):
    print('Error: Log of zero encountered.')
    raise SystemExit('')
else:
    AA_1 = 10*np.log10(AA_1)

# merge location info with SPL info
AA_1=AA_1.reset_index()
AA_1=AA_1.drop("index",axis=1)
AA_1=pd.merge(location,AA_1,left_index=True,right_index=True)
AA_1=AA_1.rename(index=str,columns={0:"SPL"})

# contour plot of SPL for each location
if num_obs < 3:
    print("Error: Need at least 3 observers to generate contour.")
else:
    x=AA_1['x'];
    y=AA_1['y'];
    z=AA_1['SPL'];
    fs = 10
    fig1,ax1=plt.subplots()
    ax1.set_aspect('equal')
    # ax1.set_title('OSPL Contour at 2m Height')
    ax1.set_xlabel('x [m]', fontsize=fs+2, fontweight='bold')
    ax1.set_ylabel('y [m]', fontsize=fs+2, fontweight='bold')
    # ax1.set_clabel('z [m]', fontsize=fs+2, fontweight='bold')
    tcf=ax1.tricontourf(x,y,z,)
    fig1.colorbar(tcf,orientation="vertical").set_label(label = 'Overall SPL [dB]', fontsize=fs+2,weight='bold')
    R = 65.
    x0 = np.array([0., 0.])
    y0 = np.array([-R, R])
    x1 = x0 * np.cos(yaw) - y0 * np.sin(yaw)
    y1 = x0 * np.sin(yaw) + y0 * np.cos(yaw)

    plt.plot(x1, y1, color = 'w', linewidth = 3)
    plt.plot(0, 0, marker = 'o', color = 'w', markersize = 5)
    ax1.tricontour(x,y,z, colors='None')
    if save_fig == True:
        # plt.savefig('{}-contour.pdf'.format(outputfilename))
        folder2 = '/Users/pbortolo/Dropbox/Writing/NoiseTechReport/'
        fig_name = 'temp.pdf'
        fig1.savefig(folder2 + fig_name)
    plt.show()

# export to csv
if save_data == True:
    AA_1.to_csv(r'{}-data.csv'.format(outputfilename))

