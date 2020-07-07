from rocket_chat import RocketChat
from flask import jsonify, request, Blueprint

blueprint = Blueprint("rocket_chat", __name__)


@blueprint.route("/post_message", methods=["POST"])
def post_message():
    content = request.get_json()

    result = RocketChat.post(content["message"])

    if result:
        return jsonify(status="success"), 200

    return jsonify(status="failed"), 500
