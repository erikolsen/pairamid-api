from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('reminder', __name__)

@blueprint.route("/team/<team_uuid>/reminders", methods=["GET"])
def index(team_uuid):
    date = request.args.get('date')
    return jsonify(operations.run_fetch_all(team_uuid, date))

@blueprint.route("/team/<team_uuid>/reminder", methods=["POST"])
def create(team_uuid):
    return jsonify(operations.run_create(request.json))

# @blueprint.route("/team/<uuid>", methods=["GET"])
# def show(uuid):
#     return jsonify(operations.run_fetch(uuid))

# @blueprint.route("/team/<uuid>", methods=["PUT"])
# def update(uuid):
#     return jsonify(operations.run_update(id, request.json))

@blueprint.route("/team/<uuid>/reminder/<id>", methods=["DELETE"])
def delete(uuid, id):
    print('Here')
    return jsonify(operations.run_delete(id))