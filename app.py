########### Python 3.2 #############
import urllib.request, json
from flask import Flask
import os

app = Flask(__name__)


@app.route('/bus')
def hello():
    print("hello")

try:
    url = "https://nextrip-public-api.azure-api.net/octranspo/gtfs-rt-vp/beta/v1/VehiclePositions?format=json"

    hdr ={
        # Request headers
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': str(os.environ.get('API_KEY')),
    }

    req = urllib.request.Request(url, headers=hdr)

    req.get_method = lambda: 'GET'
    response = urllib.request.urlopen(req)
    print(response.getcode())
    print(response.read())

    # parse data

except Exception as e:
    print(e)
