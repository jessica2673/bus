########### Python 3.2 #############
import urllib.request, json
from flask import Flask, request
import os
from dotenv import load_dotenv
import time
import requests
from typing import List, Dict
from time import strftime, localtime
import datetime
# from slack_sdk.errors import SlackApiError
# from slack_sdk.webhook import WebhookClient

app = Flask(__name__)
load_dotenv()

# wait_on_station=False

def calculate_time(arrival_time):
    current_timestamp = int(time.time())
    print(current_timestamp)
    return arrival_time - current_timestamp

def post_message_to_slack(text: str, blocks: List[Dict[str, str]] = None, channel: str = os.getenv("SLACK_APP_CHANNEL")):
    print("token ", os.getenv("SLACK_APP_TOKEN"))
    print("channel ", os.getenv("SLACK_APP_CHANNEL"))
    # if channel == "D085VHCS7T3":
    #     text = "mimimimimimi"
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': os.getenv("SLACK_APP_TOKEN"),
        'channel': channel,
        'text': text,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()

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
            "63": { # route_63_innovation going north
                "665": 6, # March Road / Solandt
                "663": 10, # March Road / Carling
            },
            "663": { # route_63_innovation going south
                "2824": 5, # March Road / Ad. 501
                "671": 6, # Terry Fox / March
                "7958": 6, # Innovation / Terry Fox
                "9546": 8, # Innovation B
                "4574": 10, # Flamborough / Terry Fox
            },
            "64": { # route 64 going south from TM
                "609": 3, # Hines / Innovation
                "608": 3, # Innovation / Hines
                "607": 5, # Innovation / Ad. 2000
                "606": 5, # Innovation / Ad. 3000
                "605": 5, # Innovation / Goulbourn Forced
                "9546": 5, # Innovation A
                "4574": 7, # Flamborough / Terry Fox
                "4573": 8, # Flamborough / Halton
                "2705": 9, # Flamborough / Laxford
                "2704": 10, # Flamborough / Keighley
            },
            "64": { # route 64 going north from TM
                "664": 1, # Solandt / March
                "599": 5, # Legget / Solandt
                "598": 5, # Legget / Ad. 350
                "597": 6, # Legget / Ad. 309
                "5144": 8, # 4048 Carling
                "663": 8, # March Road / Carling
                "662": 9, # 360 March
                "661": 10, # March / Teron
            },
        }
        
        trips = []
        for obj in json.loads(response.read())['Entity']:
            # print(obj['TripUpdate'])
            if (obj['TripUpdate']['Trip']['RouteId'] != id):
                continue
            for upd in obj['TripUpdate']['StopTimeUpdate']:
                if (upd['StopId'] in routes[id]):
                    if upd['Arrival'] is None:
                        print("No departure found")
                        continue
                    timeArrive = strftime('%Y-%m-%d %H:%M:%S', localtime(upd['Arrival']['Time']))
                    print("debugging timeArrive: " + timeArrive)
                    trips.append(obj)

        print(trips)
        print(len(trips))

        for trip in trips:
            time_to_next = trip["Arrival"]["Time"]
            next_stop = trip["StopId"]

            arrival_time = calculate_time(time_to_next) + routes[id][next_stop] # time to get to next stop and time from that stop to TM
            if (arrival_time < 600): # 10 minutes
                print("Your bus is arriving in " + arrival_time + " minutes")

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
    
# def send_slack_message(user_id, message): 
#     try: 
#         slack_client.chat_postMessage(channel=user_id, text=message) 
#     except SlackApiError as e: 
#         print(f"Error sending message: {e.response['error']}")

# POST and PUT request handler
@app.route('/', methods=['POST', 'PUT'])
def post_put_challenge():
    # event = data["event"]
    # used_id = event.get("user")
    # text = event.get("text", "").lower()

    try:
        # if wait_on_station:



        print('POOOOOST')
        # print(request.form)
        # challenge = request.form.get('challenge')  # For form data in POST/PUT
        # print(challenge)
        print(request)
        data=request.json
        print(data)
        print(data['event'])
        print(data['event']['text'])
        # file_path = 'test.json'
        # with open(file_path, 'w') as json_file:
        #     json_file.write(json.dumps(data))
        text = data["event"]["text"]
        channel = data['event']['channel']
        if channel == "D085VHCS7T3":
            # for i in range(69):
            post_message_to_slack(text="mimimimimimimimimimimimi 🦆🦆🦆", channel=channel)
        elif text in ["hi", "hello"]:
            # wait_on_station = True
            post_message_to_slack(text="Hello! Enter your nearest bus stop: ", channel=channel)
        else:
            pass
            # wait_on_station = False
        return f"{data['challenge']}"
    except Exception as e:
        return f"Error: {e}"

# @app.route('/bus')
# def query(): # requires the next stop as input and estimated arrival time
#     route_63_innovation = { # relevant stops with stop id as key and mins to TM as value
#         "1898": 8, # March Road / Solandt
#         "7985": 13, # March Road / Carling
#     }

# try:
#     while True:
#         get_trips_by_route_id(64)
#         time.sleep(20)

# except Exception as e:
#     print(f"Exception found: {e}")
#     arrival_time = calculate_time(next_stop) + route_63_innovation["next_stop"] # time to get to next stop and time from that stop to TM
#     if (arrival_time < 600): # 10 minutes
#         print("Your bus (63) is arriving in " + arrival_time + " minutes")

# post_message_to_slack(text="Busin")


if __name__ == '__main__':

    app.run()


    # count = 0
    # while True:
    #     blocks = None
    #     requests.post('https://slack.com/api/chat.postMessage', {
    #         'token': os.getenv("SLACK_APP_TOKEN"),
    #         'channel': 'busin',
    #         'text': f'MIMIMIMIMIx{count}',
    #         'blocks': json.dumps(blocks) if blocks else None
    #     }).json()
    #     count += 1
    #     time.sleep(5)
