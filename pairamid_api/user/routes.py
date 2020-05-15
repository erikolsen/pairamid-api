from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('user', __name__)

@blueprint.route("/users", methods=["GET"])
def index():
    return jsonify(operations.run_fetch_all())

@blueprint.route("/user/<id>", methods=["PUT"])
def update(id):
    return jsonify(operations.run_update(id, request.data))