import flask_praetorian
from flask import jsonify, request, Blueprint
from . import operations
from pairamid_api.extensions import guard

blueprint = Blueprint("feedback-tags", __name__)

@blueprint.route("/feedback-tags", methods=["POST"])
def create():
    return jsonify(operations.run_create(request.json))

@blueprint.route("/feedback-tags/<id>", methods=["POST"])
def update(id):
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/feedback-tags/<id>", methods=["DELETE"])
def delete(id):
    return jsonify(operations.run_delete(id))