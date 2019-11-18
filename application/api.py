from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import json
import pandas as pd
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
# cwd = os.getcwd()

# refer to Tariff-API-data-prep for preparing the backend data

@app.route('/')
def base():
    return jsonify('Welcome to CEEM''s API centre! Please select an API. For example: api.ceem.org.au/elec-tariffs/network')
    # return jsonify(cwd)


# Here you go to http://127.0.0.1:5000/LoadProfiles/Avg
# This is for returning the average load profile of all customers

@app.route('/LoadProfiles/Avg')
def avgload():
    with open(os.path.join('application','AllData.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


# Here you go to http://127.0.0.1:5000/LoadProfiles/Demog/lpnum
# this is for returning the average load profile of a selected subset of users

@app.route('/LoadProfiles/Demog/<lpnum>')
def data(lpnum):
    with open(os.path.join('application','AllData_Demog.json')) as data_file:
        data_loaded = json.load(data_file)
        for i in range(len(data_loaded)):
            data_loaded[i] = {k: data_loaded[i][k] for k in data_loaded[i] if (k == lpnum or k == 'TS')}

    return jsonify(data_loaded)


# Here you go to http://127.0.0.1:5000/Tariffs/AllTariffs
# this is for returning all tariffs stored in the jason file

@app.route('/Tariffs/AllTariffs')
def Alltariffs():
    with open(os.path.join('application', 'AllTariffs_Retail.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)

# # This part is for previous versions of retail tariffs
# @app.route('/elec-tariffs/retail-previous-version/<version>')
# def retail_tariff(version):
#     with open(os.path.join('application', 'AllTariffs_Retail_{}.json'.format(version))) as data_file:
#         data_loaded = json.load(data_file)
#         return jsonify(data_loaded)
#
# #  Track the versions and dates
# @app.route('/elec-tariffs/retail-previous-version-list')
# def retail_tariff(version):
#     with open(os.path.join('application', 'AllTariffs_Retail_Version_Track.json')) as data_file:
#         data_loaded = json.load(data_file)
#         return jsonify(data_loaded)
#
# # Most up to date version
# @app.route('/elec-tariffs/retail')
# def retail_tariff():
#     with open(os.path.join('application', 'AllTariffs_Retail.json')) as data_file:
#         data_loaded = json.load(data_file)
#         return jsonify(data_loaded)
#
#  # This part is for previous versions of network tariffs
#
# @app.route('/elec-tariffs/network-previous-versions/<version>')
# def network_tariff(version):
#     with open(os.path.join('application', 'AllTariffs_Network_{}.json'.format(version))) as data_file:
#          data_loaded = json.load(data_file)
#          return jsonify(data_loaded)
#
# #  Track the versions and dates
# @app.route('/elec-tariffs/network-previous-versions-list')
# def network_tariff():
#     with open(os.path.join('application', 'AllTariffs_Network_Version_Track.json')) as data_file:
#          data_loaded = json.load(data_file)
#          return jsonify(data_loaded)
#
# # Most up to date version
# @app.route('/elec-tariffs/network')
# def network_tariff():
#     with open(os.path.join('application', 'AllTariffs_Network.json')) as data_file:
#          data_loaded = json.load(data_file)
#          return jsonify(data_loaded)


# This part is for previous versions of retail tariffs or the version list
# try "/v1", "/v2", etc or "/versions" to track the version list
@app.route('/elec-tariffs/retail/<version>')
def retail_tariff_v(version):
    with open(os.path.join('application', 'AllTariffs_Retail_{}.json'.format(version))) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


#  most recent version
@app.route('/elec-tariffs/retail')
def retail_tariff():
    with open(os.path.join('application', 'AllTariffs_Retail.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)

#  Network tariffs:
# This part is for previous versions of Network tariffs or the version list
# try "/v1", "/v2", etc or "/versions" to track the version list
@app.route('/elec-tariffs/network/<version>')
def network_tariff_v(version):
    with open(os.path.join('application', 'AllTariffs_Network_{}.json'.format(version))) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


#  most recent version
@app.route('/elec-tariffs/network')
def network_tariff():
    with open(os.path.join('application', 'AllTariffs_Network.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


#  weather data from NASA Power
@app.route('/weather/<start_date>/<end_date>/<lat>/<long>')
def weather_data(start_date, end_date, lat, long):
    lat = round(2 * float(lat)) / 2
    long = round(2 * float(long)) / 2
    with sqlite3.connect(os.path.join('application', 'nasa_power.db')) as con:
        data_w = pd.read_sql_query(con=con, sql='select TS, CDD, HDD from data where TS > {} and TS < {}'
                                                ' and lat == {} and long == {}'.format(start_date, end_date, str(lat), str(long)))
        data_w2 = data_w.to_json(orient='records')
        return jsonify(data_w2)


# #  Tariff Docs
@app.route('/tariff-source/<tariff_id>')
def tariff_source(tariff_id):
    pdf_to_tariff_map = pd.read_csv(os.path.join('PDFs', 'pdf_to_tariff_map.csv'))
    print(tariff_id)
    print(pdf_to_tariff_map.loc[pdf_to_tariff_map['Tariff ID'] == str(tariff_id)]['PDF'].values[0])
    # try:
    #     return send_file(os.path.join('PDFs', str(pdf_to_tariff_map.loc[pdf_to_tariff_map['Tariff ID'] == str(tariff_id)]['PDF'].values[0]) + '.pdf'))
	# except Exception as e:
	# 	return str(e)