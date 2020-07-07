from flask import current_app
from pairamid_api.extensions import socketio
from . import operations
from flask_socketio import join_room, leave_room


@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)


@socketio.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)


@socketio.on("add pair")
def create(json, methods=["GET", "POST"]):
    new_pair = operations.run_create(json["teamId"])
    socketio.emit("add pair", new_pair, room=json["teamId"])
    return True


@socketio.on("delete pair")
def delete(json, methods=["GET", "POST"]):
    uuid = operations.run_delete(json["uuid"])
    socketio.emit("delete pair", uuid, room=json["teamId"])
    return True


@socketio.on("batch update pairs")
def batch_update(json, methods=["GET", "POST"]):
    pairs = operations.run_batch_update(json["pairs"])
    socketio.emit("batch update pairs", pairs, room=json["teamId"])
    return True


@socketio.on_error_default
def default_error_handler(e):
    current_app.log_exception(e)
    return {"error": True, "message": str(e)}
