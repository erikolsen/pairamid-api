from pairamid_api.models import Team, Role, TeamMember, PairingSession
from pairamid_api.schema import TeamSchema
from pairamid_api.extensions import db
from sqlalchemy import asc
from datetime import datetime, timedelta

def fetch_from_ids(id_string):
    ids = id_string.split(',')
    teams = Team.query.filter(Team.uuid.in_(ids)).all()
    schema = TeamSchema(many=True)
    return schema.dump(teams)

def run_fetch_active():
    ago = datetime.today() - timedelta(days=14)
    teams = {
        ps.team for ps in
        PairingSession.query
        .filter(PairingSession.created_at > ago)
        .filter(PairingSession.info != "UNPAIRED")
        .filter(PairingSession.info != "OUT_OF_OFFICE")
    }
    schema = TeamSchema(many=True)
    return schema.dump(teams)

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
    team = Team(name=data["name"])
    role = Role(name="Default")
    user = TeamMember(team=team, role=role)
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
