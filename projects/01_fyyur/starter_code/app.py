#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from typing import Dict
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
import os
import datetime
from sqlalchemy import select, func
import config

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from sqlalchemy.inspection import inspect

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
    # check for serial instead of integer
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(250))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean(), nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship("Shows", cascade="all,delete", back_populates="venue")

    ## TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean(), nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship("Shows", cascade="all,delete", back_populates="artist")

    ## TODO: implement any missing fields, as a database migration using Flask-Migrate

class Shows(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), index=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), index=True)
  venue = db.relationship("Venue", cascade="all,delete", back_populates="shows")
  artist = db.relationship("Artist", cascade="all,delete", back_populates="shows")

db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  ## TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  cur.execute("SELECT json_build_object('city', v2.city, 'state', v2.state, 'venues', json_agg(Vens)) FROM venue v2 LEFT JOIN (SELECT v.id id, v.name, coalesce(COUNT(s.id), 0) upcoming FROM venue v LEFT JOIN shows s ON v.id = s.venue_id GROUP by v.id, v.name) as Vens on v2.id = Vens.id GROUP BY v2.city, v2.state")

  rv = cur.fetchall()
  json_data=[]
  for result in rv:
    json_data.append(result[0])
  
  return render_template('pages/venues.html', areas=json_data);
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  ## TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_str = "%" + request.form['search_term'] +"%"
  sql_stmt = "SELECT json_build_object('id', v.id, 'name', v.name, 'num_upcoming_shows', coalesce(COUNT(s.id), 0)) FROM venue v LEFT JOIN shows s ON v.id = s.venue_id WHERE LOWER(v.name) LIKE LOWER(%s) GROUP by v.id, v.name"
  cur.execute(sql_stmt, (search_str,))
  
  rv = cur.fetchall()
  json_data=[]
  search_cnt=0
  for result in rv:
    json_data.append(result[0])
    search_cnt += 1
  
  response = {'count': search_cnt, 'data': json_data}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  ## TODO: replace with real venue data  from the venues table, using venue_id
  
  sql_stmt = "SELECT json_build_object('id', v2.id, 'name', v2.name, 'genres', v2.genres, 'address', v2.address, 'city', v2.city, 'state', v2.state, 'phone', v2.phone, 'website', v2.website, 'facebook_link', v2.facebook_link, 'seeking_talent', v2.seeking_talent, 'image_link', v2.image_link, 'seeking_description', v2.seeking_description) FROM venue v2 WHERE v2.id = %s"

  cur.execute(sql_stmt, (venue_id,))
  rv = cur.fetchall()

  v_dict = rv[0][0]

  a_list = []
  for v, s, a in session.query(Venue, Shows, Artist).filter(Venue.id == Shows.venue_id).filter(Shows.venue_id == venue_id).filter(Shows.artist_id == Artist.id).filter(Shows.start_time < datetime.datetime.now()).all():
      tmp_dict = {}
      tmp_dict['artist_id'] = a.id
      tmp_dict['artist_name'] = a.name
      tmp_dict['artist_image_link'] = a.image_link
      tmp_dict['start_time'] = str(s.start_time)
      a_list.append(tmp_dict) 
  v_dict['past_shows'] = a_list

  a_list = []
  for v, s, a in session.query(Venue, Shows, Artist).filter(Venue.id == Shows.venue_id).filter(Shows.venue_id == venue_id).filter(Shows.artist_id == Artist.id).filter(Shows.start_time >= datetime.datetime.now()).all():
      tmp_dict = {}
      tmp_dict['artist_id'] = a.id
      tmp_dict['artist_name'] = a.name
      tmp_dict['artist_image_link'] = a.image_link
      tmp_dict['start_time'] = str(s.start_time)
      a_list.append(tmp_dict) 
  v_dict['upcoming_shows'] = a_list

  q = session.query(Shows).filter(Shows.venue_id == venue_id).filter(Shows.start_time < datetime.datetime.now())
  count_q = q.statement.with_only_columns([func.count()])
  v_dict['past_shows_count'] = q.session.execute(count_q).scalar()

  q = session.query(Shows).filter(Shows.venue_id == venue_id).filter(Shows.start_time >= datetime.datetime.now())
  count_q = q.statement.with_only_columns([func.count()])
  v_dict['upcoming_shows_count'] = q.session.execute(count_q).scalar()

  #reformat genre array from the db to a list in the dict
  genre_list = v_dict.get('genres').strip("{}").split(",")
  genre_list = [x.strip('"') for x in genre_list] #remove quotes around list elements with spaces
  v_dict['genres'] = genre_list

  return render_template('pages/show_venue.html', venue=v_dict)  


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  ## TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  seek_talent = False
  if request.form.get('seeking_talent') == 'y':
    seek_talent = True

  newvenue = Venue(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      address=request.form['address'],
      city=request.form['city'], 
      state=request.form['state'],
      phone=request.form['phone'],
      website=request.form['website_link'],
      facebook_link=request.form['facebook_link'],
      seeking_talent=seek_talent,
      seeking_description=request.form['seeking_description'],
      image_link=request.form['image_link'],
    )
  # on successful db insert, flash success
  try:
    session.add(newvenue)
    session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('Venue ' + request.form['name'] + ' FAILED to be listed.')

  ## TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    session.query(Venue).filter_by(id = venue_id).delete()
    session.commit()
    flash('Venue ' + str(venue_id) + ' was successfully deleted!')
  except:
    flash('Venue ' + str(venue_id) + ' was NOT deleted!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  ## TODO: replace with real data returned from querying the database

  cur.execute("SELECT json_build_object('id', a.id, 'name', a.name) FROM artist a ORDER BY a.name;")

  rv = cur.fetchall()
  json_data=[]
  for result in rv:
    json_data.append(result[0])

  return render_template('pages/artists.html', artists=json_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  ## TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_str = "%" + request.form['search_term'] +"%"
  sql_stmt = "SELECT json_build_object('id', a.id, 'name', a.name, 'num_upcoming_shows', coalesce(COUNT(s.id), 0)) FROM artist a LEFT JOIN shows s ON a.id = s.artist_id WHERE LOWER(a.name) LIKE LOWER(%s) GROUP by a.id, a.name"
  cur.execute(sql_stmt, (search_str,))
  
  rv = cur.fetchall()
  json_data=[]
  search_cnt=0
  for result in rv:
    json_data.append(result[0])
    search_cnt += 1
  
  response = {'count': search_cnt, 'data': json_data}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  ## TODO: replace with real artist data from the artist table, using artist_id
  
  sql_stmt = "SELECT json_build_object('id', a.id, 'name', a.name, 'genres', a.genres, 'city', a.city, 'state', a.state, 'phone', a.phone, 'website', a.website, 'facebook_link', a.facebook_link, 'seeking_venue', a.seeking_venue, 'image_link', a.image_link, 'seeking_description', a.seeking_description) FROM artist a WHERE a.id = %s"

  cur.execute(sql_stmt, (artist_id,))
  rv = cur.fetchall()

  a_dict = rv[0][0]

  v_list = []
  for v, s, a in session.query(Venue, Shows, Artist).filter(Artist.id == Shows.artist_id).filter(Shows.artist_id == artist_id).filter(Shows.venue_id == Venue.id).filter(Shows.start_time < datetime.datetime.now()).all():
      tmp_dict = {}
      tmp_dict['venue_id'] = v.id
      tmp_dict['venue_name'] = v.name
      tmp_dict['venue_image_link'] = v.image_link
      tmp_dict['start_time'] = str(s.start_time)
      v_list.append(tmp_dict) 
  a_dict['past_shows'] = v_list

  v_list = []
  for v, s, a in session.query(Venue, Shows, Artist).filter(Artist.id == Shows.artist_id).filter(Shows.artist_id == artist_id).filter(Shows.venue_id == Venue.id).filter(Shows.start_time >= datetime.datetime.now()).all():
      tmp_dict = {}
      tmp_dict['venue_id'] = v.id
      tmp_dict['venue_name'] = v.name
      tmp_dict['venue_image_link'] = v.image_link
      tmp_dict['start_time'] = str(s.start_time)
      v_list.append(tmp_dict) 
  a_dict['upcoming_shows'] = v_list

  q = session.query(Shows).filter(Shows.artist_id == artist_id).filter(Shows.start_time < datetime.datetime.now())
  count_q = q.statement.with_only_columns([func.count()])
  a_dict['past_shows_count'] = q.session.execute(count_q).scalar()

  q = session.query(Shows).filter(Shows.artist_id == artist_id).filter(Shows.start_time >= datetime.datetime.now())
  count_q = q.statement.with_only_columns([func.count()])
  a_dict['upcoming_shows_count'] = q.session.execute(count_q).scalar()

  #reformat genre array from the db to a list in the dict
  genre_list = a_dict.get('genres').strip("{}").split(",")
  genre_list = [x.strip('"') for x in genre_list] #remove quotes around list elements with spaces
  a_dict['genres'] = genre_list

  return render_template('pages/show_artist.html', artist=a_dict) 


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>

  artist = session.query(Artist).filter_by(id = artist_id).all()[0].__dict__
  #reformat genre array from the db to a list in the dict
  seek_venue = ''
  if artist['seeking_venue']:
    seek_venue = 'y'
  
  genre_list = artist.get('genres').strip("{}").split(",")
  artist['genres'] = genre_list
  form.genres.data = genre_list
  form.name.data = artist['name']
  form.city.data = artist['city']
  form.state.data = artist['state']
  form.phone.data = artist['phone']
  form.website_link.data = artist['website']
  form.facebook_link.data = artist['facebook_link']
  form.seeking_description.data = artist['seeking_description']
  form.image_link.data = artist['image_link']
  form.seeking_venue.data = seek_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)  


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  seek_venue = False
  if request.form.get('seeking_venue') == 'y':
    seek_venue = True

  data = {
      'name': request.form['name'],
      'genres': request.form.getlist('genres'),
      'city': request.form['city'], 
      'state': request.form['state'],
      'phone': request.form['phone'],
      'website': request.form['website_link'],
      'facebook_link': request.form['facebook_link'],
      'seeking_venue': seek_venue,
      'seeking_description': request.form['seeking_description'],
      'image_link': request.form['image_link'],
  }
  session.query(Artist).filter_by(id = artist_id).update(data)
  session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  ## TODO: populate form with values from venue with ID <venue_id>
  
  venue = session.query(Venue).filter_by(id = venue_id).all()[0].__dict__
  #reformat genre array from the db to a list in the dict
  seek_talent = ''
  if venue['seeking_talent']:
    seek_talent = 'y'
  
  genre_list = venue.get('genres').strip("{}").split(",")
  venue['genres'] = genre_list
  form.genres.data = genre_list
  form.name.data = venue['name']
  form.address.data = venue['address']
  form.city.data = venue['city']
  form.state.data = venue['state']
  form.phone.data = venue['phone']
  form.website_link.data = venue['website']
  form.facebook_link.data = venue['facebook_link']
  form.seeking_description.data = venue['seeking_description']
  form.image_link.data = venue['image_link']
  form.seeking_talent.data = seek_talent
  
  #return render_template('forms/edit_venue.html', form=form, venue=v_dict.get(venue_id))
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  seek_talent = False
  if request.form.get('seeking_talent') == 'y':
    seek_talent = True

  data = {
      'name': request.form['name'],
      'genres': request.form.getlist('genres'),
      'address': request.form['address'],
      'city': request.form['city'], 
      'state': request.form['state'],
      'phone': request.form['phone'],
      'website': request.form['website_link'],
      'facebook_link': request.form['facebook_link'],
      'seeking_talent': seek_talent,
      'seeking_description': request.form['seeking_description'],
      'image_link': request.form['image_link'],
  }
  session.query(Venue).filter_by(id = venue_id).update(data)
  session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  ## TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  seek_venue = False
  if request.form.get('seeking_venue') == 'y':
    seek_venue = True

  newartist = Artist(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      city=request.form['city'], 
      state=request.form['state'],
      phone=request.form['phone'],
      website=request.form['website_link'],
      facebook_link=request.form['facebook_link'],
      seeking_venue=seek_venue,
      seeking_description=request.form['seeking_description'],
      image_link=request.form['image_link'],
    )
  # on successful db insert, flash success  
  try:
    session.add(newartist)
    session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('Artist ' + request.form['name'] + ' FAILED to be listed!!!')

  ## TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  ## TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  cur.execute("SELECT json_build_object('venue_id', sho_ven.id, 'venue_name', vname, 'artist_id', a.id, 'artist_name', a.name, 'artist_image_link', a.image_link, 'start_time', sho_ven.start_time) FROM (SELECT v.id, v.name vname, s.artist_id, s.start_time FROM shows s LEFT JOIN venue v ON v.id = s.venue_id ORDER BY vname) sho_ven LEFT JOIN artist a ON a.id = sho_ven.artist_id ORDER BY vname;")

  rv = cur.fetchall()
  json_data=[]
  for result in rv:
    json_data.append(result[0])
  return render_template('pages/shows.html', shows=json_data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  ## TODO: insert form data as a new Show record in the db, instead
 
  newshow = Shows(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time'],
    )
  # on successful db insert, flash success
  try:
    session.add(newshow)
    session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')

  ## TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
