import os
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
# Grabs the folder where the script runs.

basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# TODO IMPLEMENT DATABASE URL
app = Flask(__name__)
moment = Moment(app)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/fyyur'
db = SQLAlchemy(app)

engine = create_engine('postgresql://postgres:postgres@localhost:5432/fyyur')
Session = sessionmaker(engine)
session = Session()

conn2 = psycopg2.connect("dbname=fyyur user=postgres password=postgres")
cur = conn2.cursor()
## TODO: connect to a local postgresql database

migrate = Migrate(app, db)