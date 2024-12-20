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

from Database.crud import (
    add_route,
    add_user_to_route,
    remove_user_from_route,
    delete_route,
    get_users_from_route,
)
from Database.config import db

app = Flask(__name__)
load_dotenv()

# global variables
channels = { # dictionary with key: str representing the bus and value: list of channels to notify on slack
    "63n": [],
    "63s": [],
    "64s": [],
    "64n": [],
}
    
stop_to_bus_map = {
    1: "63n",
    2: "63s",
    3: "64s",
    4: "64n"
}

def calculate_time(arrival_time):
    current_timestamp = int(time.time())
    print(current_timestamp)
    return arrival_time - current_timestamp

def post_message_to_slack(text: str, blocks: List[Dict[str, str]] = None, channel: str = os.getenv("SLACK_APP_CHANNEL")):
    print("token ", os.getenv("SLACK_APP_TOKEN"))
    print("channel ", os.getenv("SLACK_APP_CHANNEL"))
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
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': str(os.getenv('API_KEY')),
        }

        req = urllib.request.Request(url, headers=hdr)

        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)
        print(response.read())

    except Exception as e:
        print(e)

# id is the bus (63n, 63s, 64n, 64s)
@app.route('/update/', methods=['GET'])
def get_trips_by_route_id(id = "63n"):
    id = request.args.get("id")
    # id = "63n"
    global channels
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
            "63n": { # route_63_innovation going north
                "665": 6, # March Road / Solandt
                "663": 10, # March Road / Carling
            },
            "63s": { # route_63_innovation going south
                "2824": 5, # March Road / Ad. 501
                "671": 6, # Terry Fox / March
                "7958": 6, # Innovation / Terry Fox
                "9546": 8, # Innovation B
                "4574": 10, # Flamborough / Terry Fox
            },
            "64s": { # route 64 going south from TM
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
            "64n": { # route 64 going north from TM
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
            if (obj['TripUpdate']['Trip']['RouteId'] != id[:-1]):
                continue
            for upd in obj['TripUpdate']['StopTimeUpdate']:
                if (upd['StopId'] in routes[id]):
                    if upd['Arrival'] is None:
                        print("No departure found")
                        continue
                    timeArrive = strftime('%Y-%m-%d %H:%M:%S', localtime(upd['Arrival']['Time']))
                    print("debugging timeArrive: " + str(timeArrive))
                    trips.append(upd)
        print(f"check bus {id}")
        print("trips: ", trips)
        print("num trips: ", len(trips))

        for trip in trips:
            time_to_next = trip["Arrival"]["Time"]
            next_stop = trip["StopId"]

            arrival_time = calculate_time(time_to_next) + routes[id][next_stop] # time to get to next stop and time from that stop to TM
            if (arrival_time//60 < 30): # 10 minutes
                for person in get_users_from_route(db, id): # here send a message back to each "person"
                    print("CHANNEL: ", person)
                    post_message_to_slack(text=f"Your bus {id} is arriving in " + str(arrival_time//60) + " minutes", channel=person)
                    print("Your bus is arriving in " + str(arrival_time) + " minutes")
        return "Success" 

    except Exception as e:
        print(f"Error string: {e}")
        print(f"Error", e)
        return f"Error: {e}"

# GET request handler
@app.route('/', methods=['GET'])
def get_challenge():
    global channels
    try:
        print('GET')
        print(request.args)
        challenge = request.args.get('challenge')
        print(challenge)

        return f"{challenge}"
    except Exception as e:
        return f"Error: {e}"

# POST and PUT request handler
@app.route('/', methods=['POST', 'PUT'])
def post_put_challenge():
    global channels
    try:
        print('POST')
        data=request.json
        print(data['event'])
        print(data['event']['text'])
        text = data["event"]["text"]
        channel = data['event']['channel']
        print(channel)

        if (text == "Hello! To add a bus subscription, enter your bus number and bus stop separated by a comma. Here are the bus stop options:\n\n1. (63n) March Road / Solandt\n2. (63s) March Road / Ad. 501\n3. (64s) Hines / Innovation\n4. (64n) Solandt / March" 
            or text == "All bus subscriptions removed"
            or text == "Your desired bus is successfully configured. Type hi or hello to input another bus. \nType deactivate to remove all bus subscriptions. \nType check to check current bus subscriptions"
            or text.startswith("You are subscribed to bus ")
            or text.startswith("Your bus is arriving in ")
            or text == "You are not subscribed to any buses"
            or "bot_profile" in data["event"]
        ):
            pass
        elif text in ["busin", 'BUSIN']:
            post_message_to_slack(text="That's me :D", channel=channel)
        elif text in ["hi", "hello"]:
            post_message_to_slack(text="Hello! To add a bus subscription, enter your bus number and bus stop separated by a comma. Here are the bus stop options:\n\n1. (63n) March Road / Solandt\n2. (63s) March Road / Ad. 501\n3. (64s) Hines / Innovation\n4. (64n) Solandt / March", channel=channel)
        elif text == "deactivate":
            for route in ["63n", "63s", "64s", "64n"]:

                remove_user_from_route(db, channel, route)
            post_message_to_slack(text="All bus subscriptions removed", channel=channel)
        elif text == "check":
            msg_sent = False
            for route in ["63n", "63s", "64s", "64n"]:

                users = get_users_from_route(db, route)
                if channel in users:
                    post_message_to_slack(text=f"You are subscribed to bus {route}", channel=channel)
                    msg_sent = True
            if not msg_sent:
                post_message_to_slack(text=f"You are not subscribed to any buses", channel=channel)
        else:
            try:
                info = text.split(',')
                print(info)
                if (len(info) == 2 and info[0].strip().isdigit() and info[1].strip().isdigit()):
                    bus = int(info[0].strip())
                    stop = int(info[1].strip())
                    add_user_to_route(db, channel, stop_to_bus_map[stop])
                    post_message_to_slack(text="Your desired bus is successfully configured. Type hi or hello to input another bus. \nType deactivate to remove all bus subscriptions. \nType check to check current bus subscriptions", channel=channel)
                else:
                    post_message_to_slack(text="Hello! To add a bus subscription, enter your bus number and bus stop separated by a comma. Here are the bus stop options:\n\n1. (63n) March Road / Solandt\n2. (63s) March Road / Ad. 501\n3. (64s) Hines / Innovation\n4. (64n) Solandt / March", channel=channel)
                pass
            except Exception as e:
                print("ERROR ", e)
        return f"{data['challenge']}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':

    app.run()
