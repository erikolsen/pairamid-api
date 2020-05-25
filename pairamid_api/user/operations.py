from pairamid_api.models import User, UserSchema, Role, Team
from pairamid_api.extensions import db
from sqlalchemy import asc, desc

def run_fetch_all(team_uuid):
    team = Team.query.filter(Team.uuid==team_uuid).first()
    users = team.users.order_by(asc(User.username)).all()
    schema = UserSchema(many=True)
    return schema.dump(users) 

def run_update(id, data):
    user = User.query.get(id)
    role = Role.query.get(data['roleId'])
    user.role = role
    user.username = data['initials'].upper()
    db.session.add(user)
    db.session.commit()
    schema = UserSchema()
    return schema.dump(user)

def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid==team_uuid).first()
    user = User(team=team)
    db.session.add(user)
    db.session.commit()
    schema = UserSchema()
    return schema.dump(user)

def run_delete(id):
    User.query.filter(User.id == id).delete()
    db.session.commit()
    return id