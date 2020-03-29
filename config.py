import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql+psycopg2://postgres:docker@0.0.0.0:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RocketChat connection parameters
    auth_token = '' or os.environ['RC_AUTH_TOKEN']
    user_id = '' or os.environ['RC_USER_ID']
    rc_base_url = '' or os.environ['RC_URL']
    rc_channel = '' or os.environ['RC_CHANNEL']
