########### Python 3.2 #############
import urllib.request, json
from flask import Flask, request
import os
from dotenv import load_dotenv
import time
from time import strftime, localtime
import datetime

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

def get_trips_by_route_id(id: str):
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
        
        routes = { # relevant stops with stop id as key and mins to TM as value
            "63": { # route_63_innovation
                "665": 8, # March Road / Solandt
                "663": 13, # March Road / Carling
            },
        }
        

        trips = []
        for obj in json.loads(response.read())['Entity']:
            # print(obj['TripUpdate'])
            if (obj['TripUpdate']['Trip']['RouteId'] != "64"): # testing only 63 for now
                continue
            for upd in obj['TripUpdate']['StopTimeUpdate']:
                if (upd['StopId'] in routes[id]):
                    if upd['Arrival'] is None:
                        print("No departure found")
                        continue
                    timeArrive = strftime('%Y-%m-%d %H:%M:%S', localtime(upd['Arrival']['Time']))
                    print(timeArrive)
                    trips.append(obj)

        #print(trips)
        print(len(trips))

        for trip in trips:
            time_to_next = trip["Arrival"]["Time"]
            next_stop = trip["StopId"]

            arrival_time = calculate_time(time_to_next) + routes[id][next_stop] # time to get to next stop and time from that stop to TM
            if (arrival_time < 600): # 10 minutes
                print("Your bus (63) is arriving in " + arrival_time + " minutes")

    except Exception as e:
        print(e)

# GET request handler
@app.route('/', methods=['GET'])
def get_challenge():
    try:
        print('GEEEEET')
        print(request.args)
        challenge = request.args.get('challenge')
        print(challenge)

        # data=request.json
        # print(data)
        return f"{challenge}"
    except Exception as e:
        return f"Error: {e}"

# POST and PUT request handler
@app.route('/', methods=['POST', 'PUT'])
def post_put_challenge():
    try:
        print('POOOOOST')
        # print(request.form)
        # challenge = request.form.get('challenge')  # For form data in POST/PUT
        # print(challenge)
        
        data=request.json
        print(data)
        return f"{data['challenge']}"
    except Exception as e:
        return f"Error: {e}"

# @app.route('/bus')
# def query(): # requires the next stop as input and estimated arrival time
#     route_63_innovation = { # relevant stops with stop id as key and mins to TM as value
#         "1898": 8, # March Road / Solandt
#         "7985": 13, # March Road / Carling
#     }

try:
    while True:
        get_trips_by_route_id(97)
        time.sleep(20)

except Exception as e:
    print(f"Exception found: {e}")

