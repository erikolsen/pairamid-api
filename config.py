import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql+psycopg2://postgres:docker@0.0.0.0:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False