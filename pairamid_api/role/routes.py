from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('role', __name__)

@blueprint.route("/roles", methods=["GET"])
def index():
    return jsonify(operations.run_fetch_all())

@blueprint.route("/role", methods=["POST"])
def create():
    return jsonify(operations.run_create(request.json))

@blueprint.route("/role/<id>", methods=["PUT"])
def update(id):
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/role/<id>", methods=["DELETE"])
def delete(id):
    return jsonify(operations.run_delete(id))