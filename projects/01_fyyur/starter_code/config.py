import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# TODO: connect to a local postgresql database

DEBUG = True

DB_CONFIG = {
        'host':  'localhost',
        'dbname': 'fyyur',
        'user': 'postgres',
        'password': 'postgres'
}

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/fyyur"