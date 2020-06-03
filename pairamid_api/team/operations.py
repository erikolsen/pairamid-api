from pairamid_api.models import Team, TeamSchema, Role, User
from pairamid_api.extensions import db
from sqlalchemy import asc, desc

def run_fetch_all():
    teams = Team.query.order_by(asc(Team.name)).all()
    schema = TeamSchema(many=True)
    return schema.dump(teams)

def run_fetch(uuid):
    team = Team.query.filter(Team.uuid == uuid).first()
    schema = TeamSchema()
    return schema.dump(team) 

# def run_update(id, data):
#     user = User.query.get(id)
#     role = Role.query.get(data['roleId'])
#     user.role = role
#     user.username = data['initials'].upper()
#     db.session.add(user)
#     db.session.commit()
#     schema = UserSchema()
#     return schema.dump(user)

def run_create(data):
    team = Team(name=data['name'])
    role = Role(name='Default')
    user = User(team=team, role=role)
    team.roles = [role]
    team.users = [user]
    db.session.add(team)
    db.session.add(role)
    db.session.add(user)
    db.session.commit()
    schema = TeamSchema()
    return schema.dump(team)

# def run_delete(id):
#     User.query.filter(User.id == id).delete()
#     db.session.commit()
#     return id