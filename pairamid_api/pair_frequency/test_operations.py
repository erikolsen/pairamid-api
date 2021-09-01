import unittest
import time
from .operations import run_build_frequency
from pairamid_api.app import create_app
from pairamid_api.extensions import db
from pairamid_api.test.team_factory import TeamFactory
import pendulum

class PairFrequencyCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_object="pairamid_api.test_config")
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
        factory.add_pair([u1])
        factory.add_pair([u4])
        factory.add_pair([u1, u2])
        factory.add_pair([u1, u2])
        factory.add_pair([u1, u2])
        factory.add_pair([u3, u4])
        factory.add_pair([u2, u3])
        expected = [
            {
                'username': u1.username,
                'roleName': u1.role.name,
                'frequencies': {
                    u1.username: 1,
                    u2.username: 3,
                },
            },
            {
                'username': u2.username,
                'roleName': u2.role.name,
                'frequencies': {
                    u1.username: 3,
                    u2.username: 0,
                    u3.username: 1,
                },
            },
            {
                'username': u3.username,
                'roleName': u3.role.name,
                'frequencies': {
                    u2.username: 1,
                    u3.username: 0,
                    u4.username: 1,
                },
            },
            {
                'username': u4.username,
                'roleName': u4.role.name,
                'frequencies': {
                    u3.username: 1,
                    u4.username: 1,
                },
            },
        ]

        subject = run_build_frequency(team.uuid, None, None)

        self.assertEqual(expected, subject)

    def test_run_build_frequency_by_date(self):
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
        factory.add_pair([u2, u4], info="UNPAIRED")
        factory.add_pair([u1, u3], info="OUT_OF_OFFICE")
        today = pendulum.now()

        start_date = today.subtract(days=1).to_date_string()
        end_date = today.add(days=1).to_date_string()

        expected = [
            {
                'username': u1.username,
                'roleName': u1.role.name,
                'frequencies': {
                    u1.username: 0,
                    u3.username: 1,
                    u4.username: 1,
                },
            },
            {
                'username': u2.username,
                'roleName': u2.role.name,
                'frequencies': {
                    u2.username: 0,
                    u3.username: 1,
                    u4.username: 1,
                },
            },
            {
                'username': u3.username,
                'roleName': u3.role.name,
                'frequencies': {
                    u1.username: 1,
                    u2.username: 1,
                    u3.username: 0,
                },
            },
            {
                'username': u4.username,
                'roleName': u4.role.name,
                'frequencies': {
                    u1.username: 1,
                    u2.username: 1,
                    u4.username: 0,
                },
            },
        ]

        subject = run_build_frequency(team.uuid, start_date, end_date)

        self.assertEqual(expected, subject)

