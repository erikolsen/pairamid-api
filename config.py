import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    user = 'postgres' or os.environ['POSTGRES_USER']
    password = 'docker' or os.environ['POSTGRES_PASSWORD']
    host = '0.0.0.0' or os.environ['POSTGRES_HOST']
    database = 'postgres' or os.environ['POSTGRES_DB']
    port = '5432' or os.environ['POSTGRES_PORT']

    DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

    SQLALCHEMY_DATABASE_URI = DATABASE_CONNECTION_URI 
    SQLALCHEMY_TRACK_MODIFICATIONS = False