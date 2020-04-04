import json
from app import app, db
from app.models import User, PairingSession, PairingSessionSchema, PairHistory, PairHistorySchema
from app.rocket_chat import RocketChat
from flask import jsonify, request
from sqlalchemy import asc


@app.route('/pairing_sessions', methods=["GET"])
def index():
    pairs = PairingSession.query.order_by(asc(PairingSession.created_at)).all()
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs) 

    return jsonify(display_pairs)

@app.route('/pairing_sessions', methods=["POST"])
def create():
    pair = PairingSession()
    db.session.add(pair)
    db.session.commit()

    schema = PairingSessionSchema()
    display_pair = schema.dump(pair) 

    return jsonify(display_pair)

@app.route('/pairing_sessions', methods=["PUT"])
def update():
    for pair in json.loads(request.data):
        user_ids = [user['id'] for user in pair['users']]
        users = User.query.filter(User.id.in_(user_ids))
        session = PairingSession.query.get(pair['id'])
        session.info = pair['info']
        session.users = list(users)

        db.session.add(session)

    if db.session.commit():
        return 'Success'
    return 'Failure'

@app.route("/pairing_session/<uuid>", methods=["DELETE"])
def delete(uuid):
    PairingSession.query.filter(PairingSession.uuid == uuid).delete()
    if db.session.commit():
        return 'Success'
    return 'Failure'

# @app.route('/post_message', methods=["POST"])
# def post_message():
#     content = request.get_json()

#     result = RocketChat.post(content["message"])

#     if result:
#         return jsonify(status='success'), 200

#     return jsonify(status='failed'), 500

@app.route("/history", methods=["POST"])
def create_history():
    current_pairs = PairingSession.query.all()
    for current_pair in current_pairs:
        pairs = [user.username for user in current_pair.users]
        pairs.sort()

        pair_history = PairHistory()
        pair_history.pairs = " ".join(pairs)
        db.session.add(pair_history)

    try: 
        db.session.commit()
        return jsonify(status='success'), 201
    except:
        return jsonify(status='failure'), 500

def _split_usernames(pair_history):
    pair_history['pairs'] = pair_history['pairs'].split(" ")

    return pair_history

@app.route("/history", methods=["GET"])
def fetch_history():
    pair_history = PairHistory.query.order_by(asc(PairHistory.created_at)).all()
    schema = PairHistorySchema()
    display_history = [schema.dump(history) for history in pair_history]

    list(map(_split_usernames, display_history))

    return jsonify(display_history)
