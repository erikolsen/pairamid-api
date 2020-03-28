import json
from app import app, db
from app.models import User, PairingSession, PairingSessionSchema
from flask import jsonify, request
from sqlalchemy import desc


@app.route('/pairing_sessions')
def index():
    pairs = PairingSession.query.order_by(desc(PairingSession.created_at)).all()
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs) 

    return jsonify(display_pairs)

@app.route('/pairing_sessions', methods=["POST"])
def create():
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