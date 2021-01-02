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

    def test_user_soft_delete_with_hard_delete_users_who_have_not_paired(self):
        # arrange
        factory = TeamFactory(user_count=3)
        team = factory.team
        u1, u2, _u3 = factory.users
        # act
        u1.soft_delete()
        # assert
        self.assertNotIn(u1, User.query.with_deleted().all())

    def test_user_soft_delete_today_removes_user_from_pairs(self):
        # arrange
        factory = TeamFactory(user_count=3)
        _team = factory.team
        u1, u2, _u3 = factory.users
        pair = factory.add_pair([u1, u2])
        # act
        u1.soft_delete()
        # assert
        self.assertNotIn(u1, pair.users)
        self.assertIn(u2, pair.users)

    def test_user_soft_delete_today_removes_users_from_default_pairs(self):
        # arrange
        factory = TeamFactory(user_count=3)
        _team = factory.team
        u1, u2, _u3 = factory.users
        factory.mark_ooo(u2)
        unpaired, ooo, _empty = factory.start_day_pairs()
        # act
        u1.soft_delete()
        u2.soft_delete()
        # assert
        self.assertNotIn(u1, unpaired.users)
        self.assertEqual(len(unpaired.users), 1)
        self.assertNotIn(u2, ooo.users)

    def test_user_soft_delete_filters_by_default(self):
        # arrange
        factory = TeamFactory(user_count=3)
        team = factory.team
        u1, u2, u3 = factory.users
        factory.add_pair([u1, u2], date_offset=-7)
        factory.add_pair([u2, u3], date_offset=-7)
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

    def test_user_soft_delete_with_deleted_shows_all_user_records(self):
        # arrange
        factory = TeamFactory(user_count=3)
        team = factory.team
        u1, u2, u3 = factory.users
        factory.add_pair([u1, u2], date_offset=-7)
        factory.add_pair([u2, u3], date_offset=-7)
        factory.mark_ooo(u1)
        factory.mark_ooo(u2)
        # act
        u1.soft_delete()
        # assert
        self.assertEqual(User.query.with_deleted().count(), 3)
        self.assertEqual(team.all_users.count(), 3)
        self.assertEqual(PairingSession.query.with_deleted().count(), 2)
        self.assertEqual(team.all_pairing_sessions.count(), 2)
        self.assertEqual(Participants.query.with_deleted().count(), 4)
        self.assertEqual(Reminder.query.with_deleted().count(), 2)
        self.assertEqual(team.all_reminders.count(), 2)

    def test_user_revive(self):
        # arrange
        factory = TeamFactory(user_count=3)
        u1, u2, u3 = factory.users
        unpaired, _ooo, _new = factory.start_day_pairs()
        factory.add_pair([u1, u2], date_offset=-7)
        factory.add_pair([u2, u3], date_offset=-7)
        factory.mark_ooo(u1)
        factory.mark_ooo(u2)
        # act
        u1.soft_delete()
        u1.revive()
        # assert
        self.assertEqual(User.query.count(), 3)
        self.assertIn(u1, unpaired.users)
        self.assertEqual(PairingSession.query.count(), 5)
        self.assertEqual(Participants.query.count(), 7)
        self.assertEqual(Reminder.query.count(), 2)
