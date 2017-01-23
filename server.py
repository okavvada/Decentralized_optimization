# GeoJSON server for OLGA
# steps:
# install flask
# pip install flask
# Run server:
# FLASK_DEBUG=1 FLASK_APP=server.py flask run
import flask
from flask import Flask, request
from optimization import *

# set the project root directory as the static folder, you can set others.
app = Flask(__name__)

@app.route('/')
def root():
  return app.send_static_file('index.html')

@app.route("/lat_lng")
def lat_lng():
  lat = float(request.args.get('lat'))
  lng = float(request.args.get('lng'))

  return flask.jsonify(getOlgaGeoJSON(lat = lat, lng = lng))

def fake():
	return """
	{
  "geometry": {
    "coordinates": [
      [
        [
          -122.470817, 
          37.756545
        ], 
        [
          -122.47071000000001, 
          37.758132
        ], 
        [
          -122.47045800000001, 
          37.758593
        ], 
        [
          -122.47001499999999, 
          37.758549
        ], 
        [
          -122.469728, 
          37.758465
        ], 
        [
          -122.46934099999999, 
          37.757364
        ], 
        [
          -122.46928600000001, 
          37.757194
        ], 
        [
          -122.469199, 
          37.756683
        ], 
        [
          -122.46928999999999, 
          37.756662
        ], 
        [
          -122.46963799999999, 
          37.75663
        ], 
        [
          -122.469815, 
          37.756617
        ],
        [
          -122.470817, 
          37.756545
        ]
      ]
    ], 
    "type": "Polygon"
  }, 
  "properties": {
    "houses": "69", 
    "population": 227.78013100000004
  }, 
  "type": "Feature"
}
"""  

def getOlgaGeoJSON(lat,lng):
  # This is where you do all the heavy GeoJSON stuff.
  pol = getServiceArea((lat,lng))
  # import json
  # pol = json.loads(fake())
  # geoJSON = {'lat':lat,'lng':lng}
  return pol

if __name__ == '__main__':
    app.run()