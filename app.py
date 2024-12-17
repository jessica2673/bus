########### Python 3.2 #############
import urllib.request, json
from flask import Flask
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()


@app.route('/bus')
def hello():
    print("hello")

def get_vehicle_positions():
    try:
        url = "https://nextrip-public-api.azure-api.net/octranspo/gtfs-rt-vp/beta/v1/VehiclePositions?format=json"

        hdr ={
            # Request headers
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': str(os.getenv('API_KEY')),
        }

        req = urllib.request.Request(url, headers=hdr)

        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)
        print(response.read())

        # parse data

    except Exception as e:
        print(e)

def get_trips_by_route_id(id: int):
    try:
        url = "https://nextrip-public-api.azure-api.net/octranspo/gtfs-rt-tp/beta/v1/TripUpdates?format=json"

        hdr ={
            # Request headers
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': '2946d77caec44abf9b829e13aaa24595',
        }

        req = urllib.request.Request(url, headers=hdr)

        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)
        # print(response.getcode())
        # print(json.loads(response.read()))
        trips = []
        for obj in json.loads(response.read())['Entity']:
            if (obj['TripUpdate']['Trip']['RouteId'] == str(id)):
                trips.append(obj)
        print(trips)
        print(len(trips))
    except Exception as e:
        print(e)

try:
    get_entity_by_trip_id(97)
except Exception as e:
    print(f"Exception found: {e}")