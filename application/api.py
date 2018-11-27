from flask import Flask, render_template, request, jsonify
import os
import io
import json
import pandas as pd

app = Flask(__name__)

# cwd = os.getcwd()



@app.route('/')
def base():
    return jsonify('Welcome to CEEM''s API centre! Please select an API. For example: /LoadProfiles/Avg OR /LoadProfiles/Demog/<lpnum> OR /Tariffs/AllTariffs')
    # return jsonify(cwd)


# Here you go to http://127.0.0.1:5000/LoadProfiles/Avg
# This is for returning the average load profile of all customers

@app.route('/LoadProfiles/Avg')
def avgload():
    # with open(os.path.join('application', 'AllData.json')) as data_file:
    with open(os.path.join('D:\\Codes\\Tariff-API\\application', 'AllData.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


# Here you go to http://127.0.0.1:5000/LoadProfiles/Demog/lpnum
# this is for returning the average load profile of a selected subset of users

@app.route('/LoadProfiles/Demog/<lpnum>')
def data(lpnum):
    # with open(os.path.join('application', 'AllData_Demog.json')) as data_file:
    with open(os.path.join('D:\\Codes\\Tariff-API\\application', 'AllData_Demog.json')) as data_file:

        data_loaded = json.load(data_file)
        for i in range(len(data_loaded)):
            data_loaded[i] = {k: data_loaded[i][k] for k in data_loaded[i] if (k == lpnum or k == 'TS')}
        return jsonify(data_loaded)


# Here you go to http://127.0.0.1:5000/Tariffs/AllTariffs
# this is for returning all tariffs stored in the jason file

@app.route('/Tariffs/AllTariffs')
def Alltariffs():
    # with open(os.path.join('application', 'AllTariffs.json')) as data_file:
    with open(os.path.join('D:\\Codes\\Tariff-API\\application', 'AllTariffs.json')) as data_file:

        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


