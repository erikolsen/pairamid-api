import flask_praetorian
from flask import jsonify, request, Blueprint
from . import operations
from pairamid_api.extensions import guard

blueprint = Blueprint("feedback", __name__)

@blueprint.route("/users/<id>/feedback/new", methods=["GET"])
def user_new_feedback(id):
    return jsonify(operations.fetch_feedback_user(id))

@blueprint.route("/feedbacks", methods=["POST"])
def create():
    return jsonify(operations.run_create(request.json))

@blueprint.route("/feedbacks/<id>", methods=["POST"])
def update(id):
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/feedbacks/<id>", methods=["DELETE"])
def delete(id):
    return jsonify(operations.run_delete(id))

@blueprint.route("/feedbacks/<id>/duplicate", methods=["POST"])
def duplicate(id):
    return jsonify(operations.run_duplicate(id))