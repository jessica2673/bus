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


def add_user_to_route(db, channel, route_id):
    if (db.routes.find_one({"_id": route_id})) is None:
        add_route(db, route_id)
    try:
        routes = db.routes
        data = routes.find()
        for item in data:
            print("get route id", item)
        routes.update_one({"_id": route_id}, {"$push": {"users": channel}})

    except:
        print("Failed to add user to route")


def remove_user_from_route(db, channel, route_id):
    try:
        routes = db.routes
        routes.update_one({"_id": route_id}, {"$pull": {"users": channel}})
    except:
        print("Failed to remove user from route")


def get_users_from_route(db, route_id):
    try:
        routes = db.routes
        return routes.find_one({"_id": route_id})["users"]
    except:
        print("Failed to get routes users")
