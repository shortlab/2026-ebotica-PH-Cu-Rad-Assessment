#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 16:01:10 2024

@author: ebotica
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from mpl_toolkits.axes_grid1 import make_axes_locatable



############## Species related data ################

Barea=4.44288E+12 #nm2
#Barea=4.44288E+12 #nm2
charge=3
K_SRIM = 0.85
dpa_cte=(10*K_SRIM)/(charge*85*(1.602e-10)*Barea)
####################################################

# savdir='Users/ebotica/Library/CloudStorage/OneDrive-MassachusettsInstituteofTechnology/Desktop/MIT/Short Lab/Irradiations/20240221/'

read_file = pd.read_csv(r'/Users/ebotica/Library/CloudStorage/OneDrive-MassachusettsInstituteofTechnology/Desktop/MIT/Short Lab/TGS/Data/PI3/044/044_18/2024-10-03_2/044_18_2-2024-10-03-03.40um-spot00-_postprocessing.txt', sep=',', on_bad_lines='skip', header=None)
read_file2 = pd.read_excel(r'/Users/ebotica/Library/CloudStorage/OneDrive-MassachusettsInstituteofTechnology/Desktop/MIT/Short Lab/Irradiations/20241003/Irradiation_conditions.xlsx', sheet_name=1)
read_file3 = pd.read_excel(r'/Users/ebotica/Library/CloudStorage/OneDrive-MassachusettsInstituteofTechnology/Desktop/MIT/Short Lab/Irradiations/20241003/044_18_irradiation+heat.xlsx', sheet_name=0)
tgs_file=np.array(read_file)
current_file=np.array(read_file2)
temp_file=np.array(read_file3)
l=int(len(tgs_file))
c=int(len(current_file))
t=int(len(temp_file))




t0='17:45:16' #Write initial time from one of the TGS raw data files in 24h-format
t00='17:49:22' #Write initial time from TGS irradiated measurements in 24h-format
tf='19:08:43'  #Write final time from TGS irradiated measurements in 24h-format
tfff='19:18:31' #final measurement
tirr = 208  #First excel row with current different than zero
FMT = '%H:%M:%S'
t000 = datetime.strptime(t00, FMT) - datetime.strptime(t0, FMT)
tff = datetime.strptime(tf, FMT) - datetime.strptime(t0, FMT)
tir = t000.total_seconds()-tirr
tsum=np.zeros(l)
ti=np.zeros(l)
ts=0
tc=0
o=0
cum_dpa=0
# dpa_t=np.zeros((c,2))
DPA=np.zeros((l,2))
# dpa=np.zeros(c)
diff=np.zeros(l)
diff_err=np.zeros(l)
sawf=np.zeros(l)
sawf_err=np.zeros(l)
saw_speed=np.zeros(l)
current=np.zeros((l,2))
# curr=np.zeros(c)
curr=[[],[],[],[]]
temp=[[],[]]
temp_plot=[[],[],[]]
tgs_data=[[],[],[],[],[],[],[]]




for i in range(1,l):
    t1=tgs_file[i][0].split()[21]
    tinc = datetime.strptime(t1, FMT) - datetime.strptime(t0, FMT)
    ti[i]=float(tinc.total_seconds())
    ts+=tinc.total_seconds()
    tsum[i]=float(ts)
    # t0=tgs_file[i][0].split()[21]
    diff[i]=float(tgs_file[i][0].split()[5])
    diff_err[i]=float(tgs_file[i][0].split()[6])
    sawf[i]=float(tgs_file[i][0].split()[2])
    sawf_err[i]=float(tgs_file[i][0].split()[3])
    saw_speed[i]=float(tgs_file[i][0].split()[4])
    tgs_data[0].append(tgs_file[i][0].split()[21])
    tgs_data[1].append(float(tgs_file[i][0].split()[2]))
    tgs_data[2].append(float(tgs_file[i][0].split()[3]))
    tgs_data[3].append(float(tgs_file[i][0].split()[4]))
    tgs_data[4].append(float(tgs_file[i][0].split()[5]))
    tgs_data[5].append(float(tgs_file[i][0].split()[6]))
    tgs_data[6].append(float((datetime.combine(datetime.today(), datetime.strptime(tgs_file[i][0].split()[21], FMT).time()) - datetime.combine(datetime.today(), datetime.strptime(tgs_file[1][0].split()[21], FMT).time())).total_seconds()))
    
   

   
### Current extraction ###
e=datetime.strptime(t00, FMT).time() #Initial irradiation time
d=datetime.strptime(tf, FMT).time() #Final irradiation time
cum_dpa=0

for kk in range(0,len(current_file[0])-1):
    if current_file[kk,0]<=e and current_file[kk+1,0]>e:
        curr_ti=kk
    if current_file[kk,0]<=d and current_file[kk+1,0]>d:
        curr_tf=kk
for k in range(0,c):
    curr[0].append(current_file[k,0])  #time
    curr[1].append(float(current_file[k,1]))  #current
    curr[2].append(float((datetime.combine(datetime.today(), current_file[k,0]) - datetime.combine(datetime.today(), current_file[0,0])).total_seconds()))  #accumulated time
    if k == 0:
        # For first point, use a small time interval or assume initial damage is 0
        time_interval = 1.0  # 1 second default
        dpa = float(current_file[k,1]) * dpa_cte * time_interval
    else:
        # For subsequent points, calculate actual time interval
        time_interval = float((datetime.combine(datetime.today(), current_file[k,0]) - 
                             datetime.combine(datetime.today(), current_file[k-1,0])).total_seconds())
        dpa = float(current_file[k,1]) * dpa_cte * time_interval
        
    
    cum_dpa=cum_dpa+dpa
    curr[3].append(cum_dpa)
    if float((datetime.combine(datetime.today(), current_file[k,0]) - datetime.combine(datetime.today(), current_file[1,0])).total_seconds()) >= tgs_data[6][len(tgs_data[6])-1]:
        break
    
### DPA value match with data ###

dpa_int=np.interp(tgs_data[6],curr[2],curr[3])


###  Temperature extractiom  ###
for tt in range(0,t):
    temp[0].append(temp_file[tt,1])
    temp[1].append(temp_file[tt,2])

a=datetime.strptime(t0, FMT).time()
b=datetime.strptime(tfff, FMT).time()

for ttt in range(0,len(temp[0])-1):
    if temp[0][ttt]<=a and temp[0][ttt+1]>a:
        temp_ti=ttt
    if temp[0][ttt]<=b and temp[0][ttt+1]>b:
        temp_tf=ttt

for tttt in range(temp_ti,temp_tf):
    temp_plot[0].append(temp[0][tttt])
    temp_plot[1].append(temp[1][tttt])
    temp_plot[2].append(float((datetime.combine(datetime.today(), temp[0][tttt]) - datetime.combine(datetime.today(), temp[0][temp_ti])).total_seconds()))
    
deltaT=[]    
for d in range(1,len(temp_plot[1])):
    deltaT.append(temp_plot[1][d]-temp_plot[1][d-1])


##########      Plotter     ##########    Same scale figures
fig, (ax2, ax3, ax1, ax6) = plt.subplots(4,1,figsize=(12, 18), gridspec_kw={'height_ratios': [3, 3, 1.5, 1.5]})

ax1.plot(curr[2],curr[1], color='#929591')
ax1.set_xlabel('Time (s)', fontsize=24, font='serif')
ax1.set_ylabel('Current [nA]', fontsize=24, font='serif')
ax1.tick_params(axis='x', labelsize=18, labelfontfamily='serif')
ax1.tick_params(axis='y', labelsize=18, labelfontfamily='serif')
ax1.set_xlim([0, max(tgs_data[6])])
ax1.set_ylim([0, 150])

l2=ax2.errorbar(dpa_int, tgs_data[1], tgs_data[2], lw=2, marker='o', linestyle='None',elinewidth=0.8, color='tab:cyan', label='SAW frequency')
ax2.set_xlabel('DPA', fontsize=24, font='serif')
ax2.set_ylabel('SAW frequency [$\mathregular{10^{8} Hz]}$', fontsize=24, font='serif')
ax2.tick_params(axis='x', labelsize=15, labelfontfamily='serif')
ax2.tick_params(axis='y', labelsize=15, labelfontfamily='serif')
ax5 = ax2.twinx()
ax5.set_ylabel('Thermal diffusivity [$\mathregular{10^{-6} m^{2}s^{-1}]}$', fontsize=24, font='serif')
l5=ax5.errorbar(dpa_int, tgs_data[4], tgs_data[5], lw=2, marker='o', linestyle='None',elinewidth=0.8, color='#FFA500', label='Thermal diffusivity')
ax5.tick_params(axis='x', labelsize=15, labelfontfamily='serif')
ax5.tick_params(axis='y', labelsize=15, labelfontfamily='serif')
ax2.legend(handles=[l2,l5],loc='lower right', fontsize=17)
# ax2.set_ylim(5.5e+8, 5.6e+8)
# ax5.set_ylim(4.5e-6,7e-6)
ax2.set_xlim([0, 30])

l3=ax3.errorbar(tgs_data[6], tgs_data[1], tgs_data[2], lw=2, marker='o', linestyle='None',elinewidth=0.8, color='#008080', label='SAW frequency')
ax3.set_xlabel('Time (s)', fontsize=24, font='serif')
ax3.set_ylabel('SAW frequency [$\mathregular{10^{8} Hz]}$', fontsize=24, font='serif')
ax3.tick_params(axis='x', labelsize=18, labelfontfamily='serif')
ax3.tick_params(axis='y', labelsize=18, labelfontfamily='serif')
ax4 = ax3.twinx()
ax4.set_ylabel('Thermal diffusivity [$\mathregular{10^{-6} m^{2}s^{-1}]}$', fontsize=24, font='serif')
l4=ax4.errorbar(tgs_data[6], tgs_data[4], tgs_data[5], lw=2, marker='o', linestyle='None',elinewidth=0.8, color='tab:orange', label='Thermal diffusivity')
ax4.tick_params(axis='x', labelsize=18, labelfontfamily='serif')
ax4.tick_params(axis='y', labelsize=18, labelfontfamily='serif')
ax3.legend(handles=[l3,l4],loc='lower right', fontsize=17)
# ax2.set_ylim(5.5e+8, 5.6e+8)
# ax4.set_ylim(4.5e-6,7e-6)
ax3.set_xlim([0, max(tgs_data[6])])

ax6.plot(temp_plot[2],temp_plot[1], color='#929591')
ax6.set_xlabel('Time (s)', fontsize=24, font='serif')
ax6.set_ylabel('Temperature [°C]', fontsize=24, font='serif')
ax6.tick_params(axis='x', labelsize=18, labelfontfamily='serif')
ax6.tick_params(axis='y', labelsize=18, labelfontfamily='serif')
ax6.set_ylim([240, 270])
ax6.set_xlim([0, max(tgs_data[6])])



fig.tight_layout() 
#fig.suptitle('GRCop-84', fontsize=28, font='serif')
fig.savefig('/Users/ebotica/Library/CloudStorage/OneDrive-MassachusettsInstituteofTechnology/Desktop/MIT/Short Lab/Irradiations/20241003/044_18_250C.png', dpi=300)

plt.show()
plt.close()
