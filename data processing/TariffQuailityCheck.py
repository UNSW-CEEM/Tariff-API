import json
import io
import os
import pandas as pd
import numpy as np
from datetime import datetime as dt

with open(os.path.join('D:\\Codes\\Tariff-API\\application', 'AllTariffs_New.json')) as NewTariffs:
    NewTariffs = json.load(NewTariffs)

# Test 1: The tariff DNSP names re correct
DNSPs = []
for i in range(len(NewTariffs)):
    DNSPs.append(NewTariffs[i]['Distributor'])

DNSPs=set(DNSPs)
print(DNSPs)

# Test 2: The tariff names and ID are unique
Names = []
for i in range(len(NewTariffs)):
    Names.append(NewTariffs[i]['Name'])
print(Names)
if len(Names) > len(set(Names)):
    seen = {}
    dupes = []
    for x in Names:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1
    print([' Some names are repeated! Duplicates are: ', dupes])
else:
    print('Names are unique!')

IDs = []
for i in range(len(NewTariffs)):
    IDs.append(NewTariffs[i]['Tariff ID'])
print(IDs)
if len(IDs) > len(set(IDs)):
    print('Some Codes are repeated!')
else:
    print('Codes are unique!')


# Checking if the time of use is covered. I.e. checking all times of the year
# Should check the times on the bill calculator

Timeind = pd.DataFrame(0, index=pd.date_range('2001-01-01', '2002-01-01', freq='30T'), columns=['ind'])
Timeind = Timeind.iloc[1:]
Timeind['TS'] = pd.to_datetime(Timeind.index, unit='ms')

# Timeind = Timeind.set_index('TS')

FRR=0

for i in range(len(NewTariffs)):
    Timeind['ind']=0
    tariff = NewTariffs[i]


    if tariff['Type'] == 'Flat_rate':
        FRR += 1 # print('flat rate')
    elif tariff['Type'] == 'TOU':
        ti = 0
        for k, v in tariff['Parameters']['Energy'].items():
            this_part = tariff['Parameters']['Energy'][k].copy()
            ti += 1
            for k2, v2, in this_part['TimeIntervals'].items():
                start_hour = int(this_part['TimeIntervals'][k2][0][0:2])
                if start_hour == 24:
                    start_hour = 0
                start_min = int(this_part['TimeIntervals'][k2][0][3:5])
                end_hour = int(this_part['TimeIntervals'][k2][1][0:2])
                if end_hour == 0:
                    end_hour = 24
                end_min = int(this_part['TimeIntervals'][k2][1][3:5])
                if this_part['Weekday']:
                    if start_hour <= end_hour:
                        Timeind.ind = np.where((Timeind['TS'].dt.weekday < 5) &
                                                (Timeind['TS'].dt.month.isin(this_part['Month'])) &
                                                      (((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                       >= (60 * start_hour + start_min)) &
                                                      ((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                       < (60 * end_hour + end_min))), Timeind.ind + 1, Timeind.ind)
                    else:
                        Timeind.ind = np.where((Timeind['TS'].dt.weekday < 5) &
                                               (Timeind['TS'].dt.month.isin(this_part['Month'])) &
                                               (((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                 >= (60 * start_hour + start_min)) |
                                                ((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                 < (60 * end_hour + end_min))), Timeind.ind + 1, Timeind.ind)
                if this_part['Weekend']:
                    if start_hour <= end_hour:
                        Timeind.ind = np.where((Timeind['TS'].dt.weekday >= 5) &
                                               (Timeind['TS'].dt.month.isin(this_part['Month'])) &
                                               (((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                 >= (60 * start_hour + start_min)) &
                                                ((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                 < (60 * end_hour + end_min))), Timeind.ind + 1, Timeind.ind)
                    else:
                        Timeind.ind = np.where((Timeind['TS'].dt.weekday >= 5) &
                                               (Timeind['TS'].dt.month.isin(this_part['Month'])) &
                                               (((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                 >= (60 * start_hour + start_min)) |
                                                ((60 * Timeind['TS'].dt.hour + Timeind['TS'].dt.minute)
                                                 < (60 * end_hour + end_min))), Timeind.ind + 1, Timeind.ind)
                # if Timeind.ind[Timeind.ind > 1].sum() != 0:
                # print(k)


        if Timeind.ind[Timeind.ind < 1].sum() != 0:
            print(tariff['Tariff ID'], ': Some times not assigned')
            print(i)
        elif Timeind.ind[Timeind.ind > 1].sum() != 0:
            print(tariff['Tariff ID'], ': Some times double assigned')
            print(i)