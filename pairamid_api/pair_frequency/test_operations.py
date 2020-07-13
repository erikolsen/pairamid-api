import unittest
import time
from .operations import run_build_frequency
from pairamid_api.app import create_app
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, Role, Team, Participants
import random
import functools


def generate_username():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return "".join(random.sample(letters, 3))


class TeamFactory:
    def __init__(self, name='Test Team', role_count=1, user_count=4):
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
        return [Role(name=f"Role{i}") for i in range(1, self.role_count+1)]

    @property
    @functools.lru_cache
    def users(self):
        users = []
        for i in range(1, self.user_count+1):
            users.append(User(username=generate_username(), 
                              role=random.choice(self.roles)))
        db.session.add_all(users)
        db.session.commit()
        return sorted(tuple(users))

    def add_pair(self, users, info=None):
        pair = PairingSession(team=self.team, users=users, info=info)
        db.session.add(pair)
        db.session.commit()

    def update_roles(self, role_name, *users):
        for user in users:
            user.role = Role.query.filter(Role.name == role_name).first()
            db.session.add(user)
        db.session.commit()
        


class PairFrequencyCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_object='pairamid_api.test_config')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_run_build_frequency_all(self):
        factory = TeamFactory(user_count=4)
        team = factory.team
        u1, u2, u3, u4 = factory.users 
        factory.add_pair([u1, u2])
        factory.add_pair([u1, u2])
        factory.add_pair([u1, u2])
        factory.add_pair([u3, u4])
        factory.add_pair([u2, u3])

        expected = {'header': [' ', u1.username, u2.username, u3.username, u4.username], 
                    'pairs': [
                        [u1.username, '-', 3, 0, 0], 
                        [u2.username, 3, '-', 1, 0], 
                        [u3.username, 0, 1, '-', 1], 
                        [u4.username, 0, 0, 1, '-'], 
                    ]}

        subject = run_build_frequency(team.uuid, None, None)

        self.assertEqual(expected, subject)


    def test_run_build_frequency_by_role(self):
        factory = TeamFactory(user_count=4, role_count=2)
        team = factory.team
        role1, role2 = factory.roles 
        u1, u2, u3, u4 = factory.users 
        factory.update_roles(role1.name, u1, u2)
        factory.update_roles(role2.name, u3, u4)
        factory.add_pair([u1, u3])
        factory.add_pair([u2, u3])
        factory.add_pair([u1, u4])
        factory.add_pair([u2, u4])
        factory.add_pair([u2, u4], info='UNPAIRED')
        factory.add_pair([u1, u3], info='OUT_OF_OFFICE')

        expected = {'header': [' ', u1.username, u2.username], 
                    'pairs': [
                        [u3.username, 1, 1], 
                        [u4.username, 1, 1], 
                    ]}

        subject = run_build_frequency(team.uuid, role2.name, role1.name)

        self.assertEqual(expected, subject)
    