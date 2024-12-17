########### Python 3.2 #############
import urllib.request, json
from flask import Flask, request
import os
from dotenv import load_dotenv
import time

app = Flask(__name__)
load_dotenv()

def calculate_time(arrival_time):
    current_timestamp = int(time.time())
    print(current_timestamp)
    return arrival_time - current_timestamp

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
            'Ocp-Apim-Subscription-Key': str(os.getenv('API_KEY')),
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

# routes
@app.route('/', methods=['GET'])
def hello():
    try:
        challenge = request.args.get('challenge')
        return f"{challenge}"
    except Exception as e:
        return f"{e}"
    
@app.route('/', methods=['POST', 'PUT'])
def hello():
    try:
        challenge = request.form.get('challenge')
        return f"{challenge}"
    except Exception as e:
        return f"{e}"

# @app.route('/bus')
# def query(): # requires the next stop as input and estimated arrival time
#     route_63_innovation = { # relevant stops with stop id as key and mins to TM as value
#         "1898": 8, # March Road / Solandt
#         "7985": 13, # March Road / Carling
#     }

#     arrival_time = calculate_time(next_stop) + route_63_innovation["next_stop"] # time to get to next stop and time from that stop to TM
#     if (arrival_time < 600): # 10 minutes
#         print("Your bus (63) is arriving in " + arrival_time + " minutes")

if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()
    # try:
    #     get_trips_by_route_id(97)
    # except Exception as e:
    #     print(f"Exception found: {e}")
