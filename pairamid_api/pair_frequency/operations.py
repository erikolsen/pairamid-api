from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, Role, Team
from collections import Counter

def frequencies_for_user(user, group):
    sessions = user.pairing_sessions.filter(~PairingSession.info.in_(PairingSession.FILTERED))
    counts = Counter([u.username for pair in sessions for u in pair.users])
    counts[user.username] = len([p for p in user.pairing_sessions if len(p.users) == 1])
    return [user.username, *[counts.get(u.username, 0) for u in group]]

def run_build_frequency(team_uuid, primary, secondary):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    primary = team.roles.filter(Role.name == primary).first()
    secondary = team.roles.filter(Role.name == secondary).first()
    primary_users = primary.users.all() if primary else team.users.all()
    secondary_users = secondary.users.all() if secondary else team.users.all()
 
    return {
        "header": [" "] + [u.username for u in secondary_users],
        "pairs": [frequencies_for_user(user, secondary_users) for user in primary_users],
    }
