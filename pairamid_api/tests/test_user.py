import unittest
from pairamid_api.models import User, UserSchema
from pairamid_api.extensions import db
from datetime import timedelta, datetime

class TestUser(unittest.TestCase):
    def test_users_are_serialize_able(self):
        erik = User(username='Erik', role='home')
        user_schema = UserSchema()

        # db.session.add(erik)
        # db.session.commit()

        data_dump = user_schema.dump(erik)
        print(data_dump)
        self.assertEqual(data_dump['username'], 'Erik')



