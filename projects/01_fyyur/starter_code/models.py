import json
from starter_code import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import select, func
from sqlalchemy.orm import relationship, backref
import psycopg2
from sqlalchemy.exc import IntegrityError
import datetime,decimal
from starter_code.config import *
import sys

db = SQLAlchemy(app)
migrate = Migrate(app,db)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(engine)
session = Session()

# = psycopg2.connect
conn = psycopg2.connect(
  host = DB_CONFIG['host'],
  user = DB_CONFIG['user'],
  password = DB_CONFIG['password'],
  database = DB_CONFIG['dbname'],  
)
cur = conn.cursor()

from sqlalchemy.inspection import inspect

try:
    session.flush()
except:
    print(str(sys.exc_info()[0]))
    session.rollback()


class ModelMixin:
    """Provide dict-like interface to db.Model subclasses."""

    def __getitem__(self, key):
        """Expose object attributes like dict values."""
        return getattr(self, key)

    def keys(self):
        """Identify what db columns we have."""
        return inspect(self).attrs.keys()

def to_json(inst, cls):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    # add your coversions for things like datetime's 
    # and what-not that aren't serializable.
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)

'''
class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        # Optional: convert datetime objects to ISO format
        with suppress(AttributeError):
            return obj.isoformat()
        return dict(obj)
app.json_encoder = MyJSONEncoder
'''

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Shows", cascade="all,delete",  back_populates="venue")

    def __repr__(self):
        return '<User {}>'.format(self.id)

    @property
    def json(self):
        return to_json(self, self.__class__)
    

    # TODO: implement any missing fields as a database migration using Flask-Migrate

class Artist(db.Model, ModelMixin):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Shows", cascade="all,delete",  back_populates="artist")

    def __repr__(self):
        return '<User {}>'.format(self.id)

    @property
    def json(self):
        return to_json(self, self.__class__)

class Shows(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), index=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), index=True)
    venue = db.relationship("Venue", cascade="all,delete", back_populates="shows")
    artist = db.relationship("Artist", cascade="all,delete", back_populates="shows")

    def __repr__(self):
        return '<User {}>'.format(self.id)

    @property
    def json(self):
        return to_json(self, self.__class__)

db.create_all()