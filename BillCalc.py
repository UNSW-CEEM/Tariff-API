# This function is for calculating the bill using the tariff and load profile
# load profile is half hourly net data for one year
# tariff data is a dictionary with input parameters and saved in the json file and can be retrieved
import json
import pandas as pd
import requests
from datetime import datetime
import numpy as np
#from bill_calculator import bill_calculator

# ---------- Preparing inputs -----------------
Tariff = 'T00001'  # Selected tariff : This input is coming from user . Preset to this tariff for testing. Remove later
# Also load (main_load_profile) should be estimated in other file based on the selection/information of user. Here we select
#  the average for testing
LP = requests.get('http://127.0.0.1:5000/LoadProfiles/Avg')
LP = LP.json()
df = pd.DataFrame.from_dict(LP, orient='columns')
df['TS'] = pd.to_datetime(df['TS'], unit='ms')
df = df[['TS', 'Load']]
main_load_profile = df.copy()


# ---------- Functions -----------------
# Interface to calcs with single function so the UI doesn't need to know about the different types of tariffs?
def calc(load_profile, tariff_name):
    # After user selects the tariff, the parameters of the tariff is selected from this list
    all_tariffs = requests.get('http://127.0.0.1:5000/Tariffs/AllTariffs')
    all_tariffs = all_tariffs.json()
    for i in range(len(all_tariffs)):
        if all_tariffs[i]['Tariff Code'] == Tariff:
            selected_tariff = all_tariffs[i]

    main_tariff = selected_tariff.copy()

    if main_tariff['Type'] == 'Flat_rate':
        total_bill = fr_calc(main_load_profile, main_tariff)
    elif main_tariff['Type'] == 'TOU':
        total_bill = tou_calc(main_load_profile, main_tariff)
    else:
        total_bill = 'Error'

    return total_bill


def pre_processing_load(load_profile):

    # make sure it is kwh
    # make sure it is one year
    # make sure it doesn't have missing value or changing the missing values to zero or to average
    # make sure the name is Load
    # time interval is half hour

    return load_profile
# Defining the bill calculation for each tariff


def fr_calc(load_profile, tariff):
    # idea for later: I can calculate the daily and energy values for each time
    # interval and then just multiply by them

    load_exp = load_profile['Load'].copy()
    load_exp[load_exp > 0] = 0
    load_imp = load_profile['Load'].copy()
    load_imp[load_imp < 0] = 0

    annual_kwh = load_imp.sum()
    annual_kwh_exp = load_exp.sum()

    num_of_days = len(load_profile["TS"].dt.normalize().unique())
    daily_charge = num_of_days*tariff['Parameters']['Daily']['Value']
    energy_charge = annual_kwh*tariff['Parameters']['Energy']['Value']*(1-tariff['Discount (%)']/100)
    fit_rebate = annual_kwh_exp*tariff['Parameters']['FiT']['Value']
    annual_bill = {'Annual_kWh': annual_kwh, 'Annual_kWh_Exp': annual_kwh_exp, 'Num_of_Days': num_of_days,
                   'Daily_Charge': daily_charge, 'Energy_Charge with discount': energy_charge, 'FiT_Rebate': fit_rebate,
                   'Total_Bill': energy_charge + daily_charge - fit_rebate}
    return annual_bill


def tou_calc(load_profile, tariff):
    load_exp = load_profile['Load'].copy()
    load_exp[load_exp > 0] = 0
    load_imp = load_profile['Load'].copy()
    load_imp[load_imp < 0] = 0
    load_profile['time_ind'] = 0

    annual_kwh = load_imp.sum()
    annual_kwh_exp = load_exp.sum()

    num_of_days = len(load_profile["TS"].dt.normalize().unique())
    daily_charge = num_of_days * tariff['Parameters']['Daily']['Value']
    tou_energy_charge = dict.fromkeys(tariff['Parameters']['Energy'])

    ti = 0
    all_tou_charge = 0
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
                load_profile.time_ind = np.where(((load_profile['TS'].dt.weekday < 5) &
                                                  (load_profile['TS'].dt.month.isin(this_part['Month'])) &
                                                  ((60 * load_profile['TS'].dt.hour + load_profile['TS'].dt.minute)
                                                   >= (60 * start_hour + start_min)) &
                                                  ((60 * load_profile['TS'].dt.hour + load_profile['TS'].dt.minute)
                                                   < (60 * end_hour + end_min))), ti, load_profile.time_ind)
            if this_part['Weekend']:
                load_profile.time_ind = np.where(((load_profile['TS'].dt.weekday >= 5) &
                                                  (load_profile['TS'].dt.month.isin(this_part['Month'])) &
                                                  ((60 * load_profile['TS'].dt.hour + load_profile['TS'].dt.minute)
                                                  >= (60 * start_hour + start_min)) &
                                                  ((60 * load_profile['TS'].dt.hour + load_profile['TS'].dt.minute)
                                                  < (60 * end_hour + end_min))), ti, load_profile.time_ind)

        tou_energy_charge[k] = {'kWh': load_imp[load_profile.time_ind == ti].sum(),
                                'Charge': this_part['Value']*load_imp[load_profile.time_ind == ti].sum()}
        all_tou_charge = all_tou_charge + tou_energy_charge[k]['Charge']

    all_tou_charge = all_tou_charge*(1 - tariff['Discount (%)'] / 100)
    fit_rebate = annual_kwh_exp * tariff['Parameters']['FiT']['Value']
    annual_bill = {'Annual_kWh': annual_kwh, 'Annual_kWh_Exp': annual_kwh_exp, 'Num_of_Days': num_of_days,
                   'Daily_Charge': daily_charge, 'FiT_Rebate': fit_rebate, 'Energy_Charge': tou_energy_charge,
                   'Total_Energy_Charge with discount': all_tou_charge,
                   'Total_Bill': all_tou_charge + daily_charge - fit_rebate}
    return annual_bill


# ---------- Bill calculation -----------------
bill = calc(main_load_profile, Tariff)
print(bill)
