from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('team', __name__)

# @blueprint.route("/teams", methods=["GET"])
# def index():
#     return jsonify(operations.run_fetch_all())

@blueprint.route("/team", methods=["POST"])
def create():
    return jsonify(operations.run_create(request.json))

@blueprint.route("/team/<uuid>", methods=["GET"])
def show(uuid):
    return jsonify(operations.run_fetch(uuid))

# @blueprint.route("/team/<uuid>", methods=["PUT"])
# def update(uuid):
#     return jsonify(operations.run_update(id, request.json))

# @blueprint.route("/team/<uuid>", methods=["DELETE"])
# def delete(uuid):
#     return jsonify(operations.run_delete(id))