from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, Role, Team, Participants, Reminder
import random
import functools
import arrow

def generate_username():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.sample(letters, 3))

class TeamFactory:
    def __init__(self, name="Test Team", role_count=1, user_count=4):
        self.name = name
        self.role_count = role_count
        self.user_count = user_count

    @property
    @functools.lru_cache
    def team(self):
        team = Team(name=self.name)
        team.roles = self.roles
        team.users = self.users
        db.session.add(team)
        db.session.commit()
        return team

    @property
    @functools.lru_cache
    def roles(self):
        return [Role(name=f"Role{i}") for i in range(1, self.role_count + 1)]

    @property
    @functools.lru_cache
    def users(self):
        users = []
        for i in range(1, self.user_count + 1):
            users.append(
                User(username=generate_username(), role=random.choice(self.roles))
            )
        db.session.add_all(users)
        db.session.commit()
        return sorted(tuple(users))

    def mark_ooo(self, user):
        reminder = Reminder(
            team=self.team,
            start_date=arrow.utcnow().format(),
            end_date=arrow.utcnow().format(),
            message="OUT_OF_OFFICE",
            user=user
        )
        db.session.add(reminder)
        db.session.commit()

    def add_pair(self, users, info=None):
        pair = PairingSession(team=self.team, users=users, info=info)
        db.session.add(pair)
        db.session.commit()

    def update_roles(self, role_name, *users):
        for user in users:
            user.role = Role.query.filter(Role.name == role_name).first()
            db.session.add(user)
        db.session.commit()