# GeoJSON server for OLGA
# steps:
# install flask
# pip install flask
# Run server:
# FLASK_DEBUG=1 FLASK_APP=server.py flask run
import flask
from flask import Flask, request
from optimization2 import *

# set the project root directory as the static folder, you can set others.
app = Flask(__name__)

@app.route('/')
def root():
  return app.send_static_file('index.html')

@app.route("/lat_lng")
def lat_lng():
  lat = float(request.args.get('lat'))
  lng = float(request.args.get('lng'))

  return flask.jsonify(getMyGeoJSON(lat = lat, lng = lng))

def getMyGeoJSON(lat,lng):
  # This is where you do all the heavy GeoJSON stuff.
  polygon, points = getServiceArea((lat,lng))
  return points

if __name__ == '__main__':
    app.run()