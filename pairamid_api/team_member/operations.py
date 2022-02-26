from pairamid_api.models import TeamMember, Role, Team, PairingSession, FeedbackTagGroup, FeedbackTag, Feedback
from pairamid_api.schema import TeamMemberSchema, FullUserSchema, TeamUserProfile
from pairamid_api.extensions import db, guard
from pairamid_api.pairing_session.operations import add_user_to_available
from sqlalchemy import asc
from .initial_feedback_groups import INITIAL_FEEDBACK_GROUPS, INITIAL_FEEDBACK

def tag_for_name(feedbacks, name):
    return next((x for x in feedbacks if x.name == name), None)

def add_inital_feedback_for(team_member, tags):
    for feedback in INITIAL_FEEDBACK:
        new_feedback = Feedback(
            author_name='Pairamid Team',
            message=feedback.get('message', ''),
            tags=[tag_for_name(tags, tag) for tag in feedback.get('tags', [])],
            recipient=team_member
        )
        db.session.add(new_feedback)
    return True

def build_feedback_tag_groups_for(team_member):
    tags = []
    for group in INITIAL_FEEDBACK_GROUPS:
        fb_group = FeedbackTagGroup(name=group['name'], team_member=team_member)
        db.session.add(fb_group)
        for tag in group['tags']:
            new_tag = FeedbackTag(
                name=tag['name'],
                description=tag['description'],
                group=fb_group
            )
            tags.append(new_tag)
            db.session.add(new_tag)
    return tags

def initials_from(full_name):
    split_name = full_name.split(' ')
    if len(full_name) <= 3 and len(full_name) > 0:
        return full_name.upper()
    if len(split_name) <= 3 and len(split_name) > 0:
        return ''.join([name[0] for name in split_name]).upper()
    return full_name[0].upper()

def run_sign_up(data):
    email = data.get("email", None)
    password = data.get("password", None)
    full_name = data.get("fullName", None)
    try:
        new_user = TeamMember(
            email=email,
            full_name=full_name,
            username=initials_from(full_name),
            password=guard.hash_password(password),
        )
        db.session.add(new_user)
        tags = build_feedback_tag_groups_for(new_user)
        add_inital_feedback_for(new_user, tags)
        db.session.commit()
        return {
            "access_token": guard.encode_jwt_token(new_user),
            "uuid": new_user.uuid,
        }
    except Exception as e:
        raise e

def run_fetch(user_uuid):
    team_member = TeamMember.query.with_deleted().filter(TeamMember.uuid == user_uuid).first()
    schema = FullUserSchema()
    return schema.dump(team_member)

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
