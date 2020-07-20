from pairamid_api.models import User, UserSchema, Role, Team
from pairamid_api.extensions import db
from pairamid_api.pairing_session.operations import add_user_to_available
from sqlalchemy import asc, desc


def run_fetch_all(team_uuid):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    users = team._users.order_by(asc(User.username)).all() # includes soft deleted
    schema = UserSchema(many=True)
    return schema.dump(users)


def run_update(id, data):
    user = User.query.get(id)
    role = Role.query.get(data["roleId"])
    user.role = role
    user.username = data["initials"].upper()
    db.session.add(user)
    db.session.commit()
    schema = UserSchema()
    return schema.dump(user)


def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    role = team.roles.first()
    user = User(team=team, role=role)
    db.session.add(user)
    add_user_to_available(user)
    db.session.commit()
    schema = UserSchema()
    return schema.dump(user)


def run_delete(id):
    user = User.query.get(id)
    user.soft_delete()
    schema = UserSchema()
    return schema.dump(user)
