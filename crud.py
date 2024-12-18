import random
import json


def add_route(db, _id):
    try:
        routes = db.routes
        routes.insert_one({"_id": _id, "users": []})
    except:
        print("Failed to create route")


def delete_route(db, _id):
    try:
        routes = db.routes
        routes.delete_one({"_id": _id})
    except:
        print("route does not exist")


def add_user_to_route(db, user_id, route_id):
    if (db.routes.find_one({"_id": route_id})) is None:
        add_route(db, route_id)
    try:
        routes = db.routes
        data = routes.find()
        for item in data:
            print("get route id", item)
        routes.update_one({"_id": route_id}, {"$push": {"users": user_id}})

        users = db.users
        if (users.find_one({"_id": user_id})) is None:
            try:
                username = generate_random_username()
                users.insert_one({"_id": user_id, "username": username})
            except:
                print("Failed creating user")

    except:
        print("Failed to add user to route")


def remove_user_from_route(db, user_id, route_id):
    try:
        routes = db.routes
        routes.update_one({"_id": route_id}, {"$pull": {"users": user_id}})
    except:
        print("Failed to remove user from route")


def remove_user(db, user_id):
    try:
        users = db.users
        users.delete_one({"_id": user_id})
    except:
        print("Failed to remove user")


def get_users_from_route(db, route_id):
    try:
        routes = db.routes
        return routes.find_one({"_id": route_id})["users"]
    except:
        print("Failed to get routes users")


def get_route_id_from_user(db, user_id):
    try:
        routes = db.routes
        data = routes.find()
        for item in data:
            print("get route id", item)
        return routes.find_one({"users": {"$in": [user_id]}})["_id"]
    except:
        print("Failed to find route user is in")
        return 0


def get_username(db, user_id):
    try:
        users = db.users
        username = users.find_one({"_id": user_id})["username"]
        return username

    except:
        print("Failed to retrieve username")
        return 0


def set_username(db, user_id, new_username):
    try:
        users = db.users
        users.update_one({"_id": user_id}, {"$set": {"username": new_username}})
        return True
    except:
        print("Failed to set username")
        return 0


def get_random_word():
    try:
        with open("./Database/words.json", "r") as file:
            words_data = json.load(file)
            words = words_data["data"]
        return random.choice(words)
    except Exception as e:
        print("ERROR:", e)
        return "---"


def generate_random_username():
    word1 = get_random_word()
    word2 = get_random_word()
    word3 = get_random_word()

    random_string = f"{word1.capitalize()}{word2.capitalize()}{word3.capitalize()}"
    return random_string