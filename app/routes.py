import json
from app import app, db
from app.models import User, PairingSession, PairingSessionSchema
from app.rocket_chat import RocketChat
from flask import jsonify, request
from sqlalchemy import asc


@app.route('/pairing_sessions', methods=["GET"])
def index():
    pairs = PairingSession.query.order_by(asc(PairingSession.created_at)).all()
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs) 

    return jsonify(display_pairs)

@app.route('/pairing_sessions/batch', methods=["PUT"])
def batch_update():
    for pair in json.loads(request.data):
        user_ids = [user['id'] for user in pair['users']]
        users = User.query.filter(User.id.in_(user_ids))
        session = PairingSession.query.get(pair['id'])
        session.info = pair['info']
        session.users = list(users)

        db.session.add(session)

    try:
        db.session.commit()
        return jsonify(status='success'), 200
    except Exception as e:
        print('Error', e)
        return jsonify(status='failed', message='Pair failed to update.'), 500

@app.route('/pairing_sessions', methods=["POST"])
def create():
    pair = PairingSession()
    db.session.add(pair)
    db.session.commit()

    schema = PairingSessionSchema()
    display_pair = schema.dump(pair) 

    return jsonify(display_pair)


@app.route("/pairing_sessions/<uuid>", methods=["DELETE"])
def delete(uuid):
    PairingSession.query.filter(PairingSession.uuid == uuid).delete()
    try:
        db.session.commit()
        return jsonify(status='success'), 200
    except Exception as e:
        print('Error', e)
        return jsonify(status='failed'), 500

# @app.route('/post_message', methods=["POST"])
# def post_message():
#     content = request.get_json()

#     result = RocketChat.post(content["message"])

#     if result:
#         return jsonify(status='success'), 200

#     return jsonify(status='failed'), 500
