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
  a = float(request.args.get('a'))
  b = float(request.args.get('b'))
  c = float(request.args.get('d'))
  d = float(request.args.get('c'))

  return flask.jsonify(getMyGeoJSON(lat = lat, lng = lng, path = 'document.csv', metric = metric, a = a, b = b, c = c, d = d))

def getMyGeoJSON(lat,lng, path, metric, a, b, c, d):
  polygon, points = getServiceArea((lat,lng), path, metric,  a, b, c, d, 0)
  return points

if __name__ == '__main__':
    app.run()