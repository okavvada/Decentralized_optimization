from __future__ import print_function
from sys import stderr
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
  metric = request.args.get('metric')

  return flask.jsonify(getMyGeoJSON(lat = lat, lng = lng, path = 'document.csv', metric = metric))

def getMyGeoJSON(lat,lng, path, metric):
  polygon, points = getServiceArea((lat,lng), path, metric,  9.5, -0.3, 0, 0, 8, -0.1, 0, 0)
  return points

if __name__ == '__main__':
    app.run()