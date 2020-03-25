from app import db
from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# class User(db.Model):
#     id = Column(Integer, primary_key=True)
#     username = Column(String(64), index=True, unique=True)
#     role = Column(String(64))
#     pairing_sessions = relationship('PairingSession', secondary = 'participant')
#     created_date = Column(DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return '<User {}>'.format(self.username)    

# class PairingSession(db.Model):
#     id = Column(Integer, primary_key=True)
#     info = Column(Text)
#     users = relationship('User', secondary = 'participant')
#     created_date = Column(DateTime, default=datetime.utcnow)

# class Participant(db.Model):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     pairing_ssession_id = Column(Integer, ForeignKey('pairing_ssession.id'))

participants = db.Table('participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('pairing_session_id', db.Integer, db.ForeignKey('pairing_session.id'), primary_key=True)
)

class PairingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participants = db.relationship('User', secondary=participants, lazy='subquery',
        backref=db.backref('pairing_session', lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)