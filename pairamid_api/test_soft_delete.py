import unittest
import time
from pairamid_api.app import create_app
from pairamid_api.extensions import db
from pairamid_api.test.team_factory import TeamFactory
from pairamid_api.models import User, PairingSession, Participants, Reminder

class SoftDeleteCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_object="pairamid_api.test_config")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_soft_delete(self):
        # arrange
        factory = TeamFactory(user_count=3)
        team = factory.team
        u1, u2, u3 = factory.users
        factory.add_pair([u1, u2])
        factory.add_pair([u2, u3])
        factory.mark_ooo(u1)
        factory.mark_ooo(u2)
        # act
        u1.soft_delete()
        # assert
        self.assertEqual(User.query.count(), 2)
        self.assertEqual(team.users.count(), 2)
        self.assertEqual(PairingSession.query.count(), 1)
        self.assertEqual(team.pairing_sessions.count(), 1)
        self.assertEqual(Participants.query.count(), 2)
        self.assertEqual(Reminder.query.count(), 1)
        self.assertEqual(team.reminders.count(), 1)

    def test_user_soft_delete_with_deleted(self):
        # arrange
        factory = TeamFactory(user_count=3)
        u1, u2, u3 = factory.users
        factory.add_pair([u1, u2])
        factory.add_pair([u2, u3])
        factory.mark_ooo(u1)
        factory.mark_ooo(u2)
        # act
        u1.soft_delete()
        # assert
        self.assertEqual(User.query.with_deleted().count(), 3)
        self.assertEqual(PairingSession.query.with_deleted().count(), 2)
        self.assertEqual(Participants.query.with_deleted().count(), 4)
        self.assertEqual(Reminder.query.with_deleted().count(), 2)

    def test_user_revive(self):
        # arrange
        factory = TeamFactory(user_count=3)
        u1, u2, u3 = factory.users
        factory.add_pair([u1, u2])
        factory.add_pair([u2, u3])
        factory.mark_ooo(u1)
        factory.mark_ooo(u2)
        # act
        u1.soft_delete()
        u1.revive()
        # assert
        self.assertEqual(User.query.count(), 3)
        self.assertEqual(PairingSession.query.count(), 2)
        self.assertEqual(Participants.query.count(), 4)
        self.assertEqual(Reminder.query.count(), 2)





