#########################################################################################################################################

# Created by Pietro Bortolotti
# National Renewable Energy Laboratory
# Summer 2020

#########################################################################################################################################
#########################################################################################################################################

# Processes OpenFAST Aeroacoustic output file number 4 (AAOutputFile4) which gives overall sound pressure level (OASPL) for each observer

#########################################################################################################################################

#packages

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import weio
from parse import *
import re, os
import matplotlib.colors

#########################################################################################################################################

## User inputs
R = 65.
R_hub = 2.
save_fig = True
# location for AAOutputFile1, Test18_OF2, and AA_ObserverLocations files
input_dir = '/Users/pbortolo/work/2_openfast/noise/verifyAA/OpenFAST_IEA_LB_RWT'
loc_dir = '/Users/pbortolo/work/2_openfast/noise/verifyAA/OpenFAST_IEA_LB_RWT'

# desired location for processed results
output_dir = "/Users/pbortolo/work/2_openfast/noise/verifyAA/post_process"

AAname = "AAOutputFile4.out"
OF2name = "RotorSE_FAST_IEA_landBased_RWT.outb"


AAfilename = input_dir + '/' + AAname
OF2filename = input_dir + '/' + OF2name

AA_1 = weio.FASTOutFile(AAfilename).toDataFrame()
OF2  = weio.FASTOutFile(OF2filename).toDataFrame()


with open(AAfilename, 'r') as f:
    f.readline()
    f.readline()
    f.readline()
    n_blades = int(f.readline().split()[-1])
    n_nodes  = int(f.readline().split()[-1])
    n_obs    = int(f.readline().split()[-1])
f.close()


phi = OF2['Azimuth_[deg]'] / 180. * np.pi
index = []
for i in range(1, len(phi)):
    if phi[i] < phi[i-1]:
        index.append(i)

y_b = np.linspace(R_hub, R, n_nodes)
x_b = np.zeros_like(y_b)

n_pts = index[-1] - index[-2]
x = np.zeros((n_pts,n_nodes))
y = np.zeros((n_pts,n_nodes))

for i in range(n_pts):
    x[i,:] = x_b * np.cos(-phi[i]) - y_b * np.sin(-phi[i])
    y[i,:] = x_b * np.sin(-phi[i]) + y_b * np.cos(-phi[i])

z = np.array(AA_1)[index[-2]:index[-1], 1:31]
fs = 10
fig1,ax1=plt.subplots()
ax1.set_aspect('equal')
# ax1.set_title('OSPL Contour at 2m Height')
ax1.set_xlabel('y [m]', fontsize=fs+2, fontweight='bold')
ax1.set_ylabel('z [m]', fontsize=fs+2, fontweight='bold')
tcf=ax1.tricontourf(x.flatten(),y.flatten(),z.flatten(), range(55, 72, 1))
fig1.colorbar(tcf,orientation="vertical").set_label(label = 'Overall SPL [dB]', fontsize=fs+2,weight='bold')
if save_fig == True:
    # plt.savefig('{}-contour.pdf'.format(outputfilename))
    fig_name = 'rotor_map.pdf'
    fig1.savefig(output_dir + os.sep + fig_name)
plt.show()




# # location file name
# locname = "AA_ObserverLocations_Map_Fine.dat"

# # number of revolutions (n) to calculate OASPL
# n = 1

# # save plot and/or data to output directory?
# save_fig = True
# save_data = False

# #########################################################################################################################################

# # produces full file paths
# locfilename = loc_dir + '/' + locname
# outputfilename = output_dir + '/' + outputname + "AAOutputFile1"

# # reads in file data
# location = pd.read_csv(locfilename,delimiter='\s+',skiprows=[0,1],names=['x','y','z'])

# # determine number of observers
# num_obs = AA_1.shape[1]-1

# # calculate sample time for n revolutions
# yaw = OF2[["YawPzn_[deg]"]].mean()[0] / 180. * np.pi
# time_revs = n*60/rpm
# tot_time = AA_1["Time_[s]"].max()
# if time_revs < tot_time:
#     sample_time = tot_time - time_revs
# else:
#     print("Error: Time for number of revolutions exceeds simulation time. Reduce n.")
#     raise SystemExit('')

# # slice AA dataframe for t > sample_time
# AA_1 = AA_1[AA_1["Time_[s]"] > sample_time]
# AA_1=AA_1.drop("Time_[s]",axis=1)

# # convert observer Sound Pressure Level (SPL) to Sound Pressure (P)
# AA_1 = 10**(AA_1 / 10)

# # average P for each observer
# AA_1 = AA_1.mean()

# # conver back from P to SPL
# if any(AA_1[i] == 0 for i in range(0,AA_1.size)):
#     print('Error: Log of zero encountered.')
#     raise SystemExit('')
# else:
#     AA_1 = 10*np.log10(AA_1)

# # merge location info with SPL info
# AA_1=AA_1.reset_index()
# AA_1=AA_1.drop("index",axis=1)
# AA_1=pd.merge(location,AA_1,left_index=True,right_index=True)
# AA_1=AA_1.rename(index=str,columns={0:"SPL"})

# # contour plot of SPL for each location
# if num_obs < 3:
#     print("Error: Need at least 3 observers to generate contour.")
# else:
#     x=AA_1['x'];
#     y=AA_1['y'];
#     z=AA_1['SPL'];
#     fs = 10
#     fig1,ax1=plt.subplots()
#     ax1.set_aspect('equal')
#     # ax1.set_title('OSPL Contour at 2m Height')
#     ax1.set_xlabel('x [m]', fontsize=fs+2, fontweight='bold')
#     ax1.set_ylabel('y [m]', fontsize=fs+2, fontweight='bold')
#     # ax1.set_clabel('z [m]', fontsize=fs+2, fontweight='bold')
#     tcf=ax1.tricontourf(x,y,z, range(58, 82, 1))
#     fig1.colorbar(tcf,orientation="vertical").set_label(label = 'Overall SPL [dB]', fontsize=fs+2,weight='bold')
#     # R = 65.
#     # x0 = np.array([0., 0.])
#     # y0 = np.array([-R, R])
#     # x1 = x0 * np.cos(yaw) - y0 * np.sin(yaw)
#     # y1 = x0 * np.sin(yaw) + y0 * np.cos(yaw)

#     # plt.plot(x1, y1, color = 'w', linewidth = 3)
#     # plt.plot(0, 0, marker = 'o', color = 'w', markersize = 5)
#     # ax1.tricontour(x,y,z, colors='None')
    
#     plt.show()

# # export to csv
# if save_data == True:
#     AA_1.to_csv(r'{}-data.csv'.format(outputfilename))

