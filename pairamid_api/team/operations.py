from pairamid_api.models import Team, TeamSchema, Role
from pairamid_api.extensions import db
from sqlalchemy import asc, desc

# def run_fetch_all():
#     users = User.query.order_by(asc(User.username)).all()
#     schema = UserSchema(many=True)
#     return schema.dump(users) 

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
    team.roles = [role]
    print('Team', team)
    # db.session.add(team)
    # db.session.commit()
    schema = TeamSchema()
    return schema.dump(team)

# def run_delete(id):
#     User.query.filter(User.id == id).delete()
#     db.session.commit()
#     return id