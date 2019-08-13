# this file is for creating the json file based on the demog information
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import json
import scipy.io as sio
import h5py
import io


# Assign spreadsheet filename to `file`
file = 'D:/Codes/SunSPoT_V2/PythonCodes/Data/Load_Ave_2.xlsx'

# Load spreadsheet
xl = pd.ExcelFile(file)
df1 = xl.parse('Sheet1')
df1['TS'] = pd.to_datetime(df1.TS)

df1.plot(x='TS', y='LP1')
df2=df1.copy()
df3=df2.to_json(orient='records')

# to_unicode = str

with io.open('AllData_Demog.json', 'w', encoding='utf8') as outfile:
    # str_ = json.dumps(df3,
    #                   indent=4, sort_keys=True,
    #                   separators=(',', ': '), ensure_ascii=False)
       outfile.write(str(df3))

