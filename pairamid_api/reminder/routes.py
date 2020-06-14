from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('reminder', __name__)

@blueprint.route("/team/<team_uuid>/reminders", methods=["GET"])
def index(team_uuid):
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    return jsonify(operations.run_fetch_all(team_uuid, start_date, end_date))

@blueprint.route("/team/<team_uuid>/reminder", methods=["POST"])
def create(team_uuid):
    return jsonify(operations.run_create(team_uuid, request.json))

# @blueprint.route("/team/<uuid>", methods=["GET"])
# def show(uuid):
#     return jsonify(operations.run_fetch(uuid))

@blueprint.route("/team/<team_uuid>/reminder/<id>", methods=["PUT"])
def update(team_uuid, id):
    print('Got here')
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/team/<uuid>/reminder/<id>", methods=["DELETE"])
def delete(uuid, id):
    print('Here')
    return jsonify(operations.run_delete(id))