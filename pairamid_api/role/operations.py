from pairamid_api.models import Role, Team
from pairamid_api.schema import RoleSchema
from pairamid_api.extensions import db
from sqlalchemy import asc

def run_fetch_all(team_uuid):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    roles = team.roles.order_by(asc(Role.name)).all()
    schema = RoleSchema(many=True)
    return schema.dump(roles)


def run_update(id, data):
    role = Role.query.get(id)
    role.name = data["name"]
    role.color = data["color"]
    db.session.add(role)
    db.session.commit()
    schema = RoleSchema()
    return schema.dump(role)


def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    role = Role(team=team)
    db.session.add(role)
    db.session.commit()
    schema = RoleSchema()
    return schema.dump(role)


def run_delete(id):
    Role.query.filter(Role.id == id).delete()
    db.session.commit()
    return id
