from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('user', __name__)

@blueprint.route("/users", methods=["GET"])
def index():
    return jsonify(operations.run_fetch_all())

@blueprint.route("/user", methods=["POST"])
def create():
    return jsonify(operations.run_create(request.json))

@blueprint.route("/user/<id>", methods=["PUT"])
def update(id):
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/user/<id>", methods=["DELETE"])
def delete(id):
    return jsonify(operations.run_delete(id))