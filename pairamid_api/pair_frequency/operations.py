from datetime import datetime 
from pairamid_api.lib.date_helpers import start_of_day, end_of_day
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, Role, Team
from collections import Counter

def parse_date(iso_date_string):
    return datetime.strptime(iso_date_string, '%Y-%m-%d')

def frequencies_for_user(user, group, start, end):
    start = start_of_day(parse_date(start))
    end = end_of_day(parse_date(end))
    sessions = (user.pairing_sessions
                    .filter(~PairingSession.info.in_(PairingSession.FILTERED))
                    .filter(PairingSession.created_at >= start)
                    .filter(PairingSession.created_at <= end)
    )
    counts = Counter([u.username for pair in sessions for u in pair.users if u is not user])
    counts[user.username] = len([p for p in sessions if len(p.users) == 1])
    return [user.username, *[counts.get(u.username, 0) for u in group]]

def run_build_frequency(team_uuid, primary, secondary, start, end):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    primary = team.roles.filter(Role.name == primary).first()
    secondary = team.roles.filter(Role.name == secondary).first()
    primary_users = primary.users.all() if primary else team.users.all()
    secondary_users = secondary.users.all() if secondary else team.users.all()
 
    return {
        "header": [" "] + [u.username for u in secondary_users],
        "pairs": [frequencies_for_user(user, secondary_users, start, end) for user in primary_users],
    }
