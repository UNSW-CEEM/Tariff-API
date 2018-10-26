from flask import Flask, render_template, request, jsonify
import os


app = Flask(__name__)


# Here you go to http://127.0.0.1:5000
@app.route('/')
def base():
  
  return jsonify(
    { 
    'data' : [1,2,3,4,5] }
  )




# Here you go to http://127.0.0.1:5000/data
@app.route('/data/<state>')
def data(state):
  print(state)
  return jsonify(
    { 'state':state,      
    'data' : [1,2,3,4,5] }
  )

if __name__ == '__main__':
  
  app.run(debug=True)
