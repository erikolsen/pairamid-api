from app import app
from app.models import User, PairingSession, PairingSessionSchema
from flask import jsonify


@app.route('/')
@app.route('/pairing_sessions')
def index():
    pairs = PairingSession.query.all()
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs) 

    return jsonify(display_pairs)

