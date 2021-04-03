from flask import Flask, render_template, request, jsonify, send_file,flash, redirect, url_for, make_response
import os
import io
import json
import pandas as pd
from flask_cors import CORS
import sqlite3
import numpy as np

from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
# cwd = os.getcwd()

# refer to Tariff-API-data-prep for preparing the backend data

@app.route('/')
def base():
    return jsonify('Welcome to CEEM''s API centre! Please select an API. For example: api.ceem.org.au/electricity-tariffs/network')
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
@app.route('/electricity-tariffs/retail/<version>')
def retail_tariff_v(version):
    with open(os.path.join('application', 'AllTariffs_Retail_{}.json'.format(version))) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


#  the version compatible with Tariff tool (nb: this name will change to retail and the previous one will be removed. It is not removed now because it is being used by SunSpoT
@app.route('/electricity-tariffs/retail')
def retail_tariff():
    with open(os.path.join('application', 'AllTariffs_Retail.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


#  For SunSpoT project. We will remove this later
@app.route('/elec-tariffs/retail')
def retail_tariff_SunSpoT():
    with open(os.path.join('application', 'AllTariffs_Retail_SunSpoT.json')) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)

#  Network tariffs:
# This part is for previous versions of Network tariffs or the version list
# try "/v1", "/v2", etc or "/versions" to track the version list
@app.route('/electricity-tariffs/network/<version>')
def network_tariff_v(version):
    with open(os.path.join('application', 'AllTariffs_Network_{}.json'.format(version))) as data_file:
        data_loaded = json.load(data_file)
        return jsonify(data_loaded)


#  most recent version
@app.route('/electricity-tariffs/network')
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
        data_w = pd.read_sql_query(con=con, sql='select TS, CDD, HDD from data where TS >= {} and TS <= {}'
                                                ' and lat == {} and long == {}'.format(start_date, end_date, str(lat), str(long)))
        data_w = data_w.drop_duplicates(subset='TS', keep='last')
        data_w2 = data_w.to_json(orient='records')
        return jsonify(data_w2)


# #  Tariff Docs
@app.route('/tariff-source/<tariff_id>')
def tariff_source(tariff_id):
    if tariff_id.startswith('TR'):
        return str('We have obtained the retail tariffs from EnergyMadeEasy Website (https://www.energymadeeasy.gov.au/). Please refer to this website and search for this tariff for more information.')
    else:
        pdf_to_tariff_map = pd.read_csv(os.path.join('application', 'PDFs', 'pdf_to_tariff_map.csv'))
        # print(tariff_id)
        # return(pdf_to_tariff_map.loc[pdf_to_tariff_map['Tariff ID'] == str(tariff_id)]['PDF'].values[0])
        try:
            return send_file(os.path.join('PDFs', str(pdf_to_tariff_map.loc[pdf_to_tariff_map['Tariff ID'] == tariff_id]['PDF'].values[0]) + '.pdf'))
        except:
            return str('There is no document for this tariff.')

# uploading load profiles
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/lp_upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        file_read = pd.read_csv(file,header=None)
        NEM12_1 = file_read.copy()

        Chunks = np.where((NEM12_1[NEM12_1.columns[0]] == 200) | (NEM12_1[NEM12_1.columns[0]] == 900))[0]
        NEM12_2 = pd.DataFrame()
        for i in range(0, len(Chunks) - 1):
            if NEM12_1.iloc[Chunks[i], 4].startswith('E'):
                this_part = NEM12_1.iloc[Chunks[i] + 1: Chunks[i + 1], :].copy()
                this_part = this_part[this_part[this_part.columns[0]] == 300].copy()
                this_part2 = this_part.iloc[:, 2:50]
                this_part2 = this_part2.astype(float)
                if (this_part2[
                        this_part2 < 0.01].count().sum() / this_part2.count().sum()) < 0.3:  # assume for controlled load more 30% of data points are zero
                    NEM12_2 = NEM12_1.iloc[Chunks[i] + 1: Chunks[i + 1], :].copy()
                    NEM12_2.reset_index(inplace=True, drop=True)

        NEM12_2 = NEM12_2[NEM12_2[NEM12_2.columns[0]] == 300].copy()
        NEM12_2[NEM12_2.columns[1]] = NEM12_2[NEM12_2.columns[1]].astype(int).astype(str)

        Nem12 = NEM12_2.iloc[:, 1:50].melt(id_vars=[1], var_name="HH",
                                           value_name="kWh")  # it was 49.. need to check if Dan manually changed it
        Nem12['HH'] = Nem12['HH'] - 1
        Nem12['kWh'] = Nem12['kWh'].astype(float)

        Nem12['Datetime'] = pd.to_datetime(Nem12[1], format='%Y%m%d') + pd.to_timedelta(Nem12['HH'] * 30, unit='m')
        Nem12.sort_values('Datetime', inplace=True)
        # Nem12_ = Nem12.groupby(['Datetime','HH']).sum().reset_index()
        Nem12.reset_index(inplace=True, drop=True)
        sample_load = Nem12[['Datetime', 'kWh']].copy()
        sample_load.rename(columns={'Datetime': 'TS'}, inplace=True)
        sample_load['TS'] = pd.to_datetime(sample_load['TS'])
        sample_load = sample_load[sample_load['TS'].dt.normalize() != '2020-02-29'].copy()
        sample_load['TS'] = sample_load['TS'].dt.strftime("%d/%m/%Y %H:%M")
        # cols=file_read.columns
        resp = make_response(sample_load.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp
    return '''
    <!doctype html>
    <title>Upload your load profile</title>
    <h1>Convert your load profile to standard format</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''