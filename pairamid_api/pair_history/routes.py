import json
from pairamid_api.extensions import db
from pairamid_api.models import (
    PairingSession, 
    PairingSessionSchema, 
    PairHistory, 
    PairHistorySchema
)
from flask import jsonify, request, Blueprint
from sqlalchemy import asc

blueprint = Blueprint('pair_history', __name__)

@blueprint.route("/history", methods=["POST"])
def create_history():
    current_pairs = PairingSession.query.all()
    for current_pair in current_pairs:
        if len(current_pair.users) == 0:
            continue
        pairs = [user.username for user in current_pair.users]
        pairs.sort()

        pair_history = PairHistory()
        pair_history.pairs = " ".join(pairs)
        db.session.add(pair_history)

    db.session.commit()
    return jsonify(status='success'), 201

def _split_usernames(pair_history):
    pair_history['pairs'] = pair_history['pairs'].split(" ")

    return pair_history

@blueprint.route("/history", methods=["GET"])
def fetch_history():
    pair_history = PairHistory.query.order_by(asc(PairHistory.created_at)).all()
    schema = PairHistorySchema()
    display_history = [schema.dump(history) for history in pair_history]

    list(map(_split_usernames, display_history))

    return jsonify(display_history)
