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

user_pending_input = {}

# global variables
channels = { # dictionary with key: str representing the bus and value: list of channels to notify on slack
    "63n": [],
    "63s": [],
    "64s": [],
    "64n": [],
}

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

# id is the bus (63n, 63s, 64n, 64s)
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
                for person in channels[id]: # here send a message back to each "person"
                    post_message_to_slack("Your bus is arriving in " + arrival_time + " minutes", person)
                    print("Your bus is arriving in " + arrival_time + " minutes")

    except Exception as e:
        print(e)

# def add_person(id: str, channel: str):
#     if channel not in channels[id]:
#         channels[id].add(channel)

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
    
stop_to_bus_map = {
    1: "63n",
    2: "63s",
    3: "64s",
    4: "64n"
}
    
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
        # print(request)
        data=request.json
        # print(data)
        # print(data['event'])
        print(data['event']['text'])
        # file_path = 'test.json'
        # with open(file_path, 'w') as json_file:
        #     json_file.write(json.dumps(data))
        text = data["event"]["text"]
        channel = data['event']['channel']
        print(channel)
        # if channel == "D085VHCS7T3":
        #     # for i in range(69):
        #     post_message_to_slack(text="mimimimimimimimimimimimi 🦆🦆🦆", channel=channel)
        # el
        if text in ["hi", "hello"]:
            # wait_on_station = True
            user_pending_input[channel] = -1
            post_message_to_slack(text="Hello! Enter your bus number. Type cancel to cancel: ", channel=channel)
        elif text == "deactivate":
            for k,v in channels.items():
                if channel in v:
                    v.remove(channel)
            post_message_to_slack(text="All bus subscriptions removed", channel=channel)
        elif text == "cancel":
            if channel in user_pending_input:
                post_message_to_slack(text="Bus subscription operation has been cancelled", channel=channel)
                user_pending_input.pop(channel)
        else:
            try:
                if channel in user_pending_input and user_pending_input[channel] == -1 and text.isdigit():
                    print('bus number ', text)
                    print("channels ", channels)
                    user_pending_input[channel] = int(text)
                    post_message_to_slack(text="Now input the number corresponding to your desired bus stop from one of these options. Type cancel to cancel: \n\n1. (63n) March Road / Solandt\n2. (63s) March Road / Ad. 501\n3. (64s) Hines / Innovation\n4. (64n) Solandt / March", channel=channel)
                elif channel in user_pending_input and user_pending_input[channel] >= 0 and text.isdigit():
                    bus = user_pending_input[channel]
                    stop = int(text)
                    print('bus station ', text, " ", stop_to_bus_map(stop))
                    print("channels ", channels)
                    channels[stop_to_bus_map(stop)].append(channel)

                    post_message_to_slack(text="Your desired bus is successfully configured. Type hi or hello to input another bus. Type deactivate to remove all bus subscriptions", channel=channel)
                    user_pending_input.pop(channel)
                # else:
                #     if channel in user_pending_input:
                #         post_message_to_slack(text="Invalid input. Bus subscription operation has been cancelled", channel=channel)
                #         user_pending_input.pop(channel)
                    # else:
                    #     post_message_to_slack(text="Can not understand user input. Type hi or hello to add a bus subscription", channel=channel)
                    # pass
                # why
                # pass
            except Exception as e:
                print("ERROR ", e)
                user_pending_input.pop(channel)
                # pass
            # wait_on_station = False
        return f"{data['challenge']}"
    except Exception as e:
        return f"Error: {e}"

try:
    while True:
        get_trips_by_route_id("63n")
        get_trips_by_route_id("63s")
        get_trips_by_route_id("64s")
        get_trips_by_route_id("63n")
        time.sleep(30)

except Exception as e:
    print(f"Exception found: {e}")

post_message_to_slack(text="Busin")


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
