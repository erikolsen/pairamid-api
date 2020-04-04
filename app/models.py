from app import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from uuid import uuid4

#### Tables 

participants = db.Table('participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('pairing_session_id', db.Integer, db.ForeignKey('pairing_session.id'), primary_key=True)
)

class PairingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', secondary=participants, passive_deletes=True, 
        backref=db.backref('pairing_sessions'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    username = db.Column(db.String(64))
    role = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PairHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pairs = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#### Schemas

class UserSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = User

class PairingSessionSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = PairingSession
        include_relationships = True
    
    users = fields.Nested(UserSchema, many=True)

class PairHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PairHistory


def seed():
    eo = User(username='eo', role='HOME')
    nh = User(username='nh', role='HOME')
    bd = User(username='bd', role='HOME')
    jh = User(username='jh', role='HOME')
    ms = User(username='ms', role='HOME')
    es = User(username='es', role='HOME')
    kd = User(username='kd', role='HOME')
    mj = User(username='mj', role='HOME')
    jw = User(username='jw', role='HOME')
    ar = User(username='ar', role='HOME')
    mvs = User(username='mvs', role='HOME')

    cd = User(username='cd', role='VISITOR')
    tp = User(username='tp', role='VISITOR')
    mr = User(username='mr', role='VISITOR')
    rp = User(username='rp', role='VISITOR')
    rj = User(username='rj', role='VISITOR')
    jl = User(username='jl', role='VISITOR')
    cp = User(username='cp', role='VISITOR')

    home = [eo, nh, bd, jh, ms, es, kd]
    solos = [[mvs], [mj], [jw], [ar]]
    visitor = [cd, tp, mr, rp, rj, jl, cp]


    for user in home + visitor:
        db.session.add(user)

    for pair in solos:
        pairing_session = PairingSession(users=list(pair))
        db.session.add(pairing_session)

    for pair in list(zip(home, visitor)):
        pairing_session = PairingSession(users=list(pair))
        db.session.add(pairing_session)

    db.session.commit()
