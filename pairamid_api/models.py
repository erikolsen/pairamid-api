from pairamid_api.extensions import db
from pairamid_api.lib.date_helpers import end_of_day
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
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
    info = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    users = db.relationship('User', secondary=participants, passive_deletes=True, 
        order_by="User.username")

    def __lt__(self, obj):
        return self.created_at.date() < obj.created_at.date()

    def __eq__(self, obj):
        return sorted(self.users) == sorted(obj.users)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    username = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.relationship("Role", uselist=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pairing_sessions = db.relationship('PairingSession', secondary=participants,
        order_by="desc(PairingSession.created_at)", lazy='dynamic')

    def __lt__(self, obj):
        return self.username < obj.username

    def __repr__(self):
        return f'<User {self.username} {self.role.name} >'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    color = db.Column(db.String(64), default='#7F9CF5')
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Role {self.name} >'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship("User", backref='user', lazy='dynamic')
    pairing_sessions = db.relationship("PairingSession", backref='pairing_session', lazy='dynamic')
    roles = db.relationship("Role", backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Team {self.name} {self.uuid} >'

#### Schemas
class RoleSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = Role

class UserSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = User

    role = fields.Nested(RoleSchema)

class TeamSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = Team

    roles = fields.Nested(RoleSchema, many=True)
    members = fields.fields.Method('member_count')

    def member_count(self, obj):
        if bool(obj.users):
            return obj.users.count()

        return 0

class PairingSessionSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = PairingSession
        include_relationships = True
    
    users = fields.Nested(UserSchema, many=True)
    history = fields.fields.Method('counter')

    def counter(self, obj):
        if bool(obj.users):
            ps = (obj.users[0].pairing_sessions
                              .filter(PairingSession.info != 'UNPAIRED')
                              .filter(PairingSession.created_at < end_of_day(obj.created_at))
                              .limit(10))
            count = 0
            for pair in ps:
                if pair == ps[0]:
                    count += 1 
                else:
                    break
            return count
        else:
            return 0
