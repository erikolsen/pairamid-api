from pairamid_api.models import TeamMember, Role, Team, PairingSession
from pairamid_api.schema import TeamMemberSchema, TeamUserProfile
from pairamid_api.extensions import db
from pairamid_api.pairing_session.operations import add_user_to_available
from sqlalchemy import asc

def run_fetch_team_user(user_uuid):
    team_member = TeamMember.query.with_deleted().filter(TeamMember.uuid == user_uuid).first()
    schema = TeamUserProfile()
    return schema.dump(team_member)


def run_fetch_all(team_uuid):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    team_members = team.all_team_members.order_by(asc(TeamMember.username)).all() # includes soft deleted
    schema = TeamMemberSchema(many=True)
    return schema.dump(team_members)


def run_update(id, data):
    team_member = TeamMember.query.get(id)
    role = Role.query.get(data["roleId"])
    team_member.role = role
    team_member.username = data["initials"].upper()
    db.session.add(team_member)
    db.session.commit()
    schema = TeamMemberSchema()
    return schema.dump(team_member)


def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    role = team.roles.first()
    team_member = TeamMember(team=team, role=role)
    db.session.add(team_member)
    add_user_to_available(team_member)
    db.session.commit()
    schema = TeamMemberSchema()
    return schema.dump(team_member)


def run_delete(id):
    team_member = TeamMember.query.with_deleted().get(id)
    schema = TeamMemberSchema()
    if team_member.pairing_sessions.filter(PairingSession.info != "UNPAIRED").count() == 0:
        hard_delete = True
        team_member.hard_delete()
    else:
        hard_delete = False
        team_member.soft_delete()
    dump = schema.dump(team_member)
    dump['hardDelete'] = hard_delete
    return dump 

def run_revive(id):
    team_member = TeamMember.query.with_deleted().get(id)
    team_member.revive()
    schema = TeamMemberSchema()
    return schema.dump(team_member)
