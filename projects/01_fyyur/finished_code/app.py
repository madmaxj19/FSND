#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    seeking_talent=db.Column(db.String)
    seeking_description=db.Column(db.String)
    
    def __repr__(self):
        return f'<Venue.ID: {self.id}, Venue.Name: {self.name}>, Venue.City: {self.city}, Venue.State: {self.state}, Venue.Address: {self.address}, Venue.genres: {self.genres}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue=db.Column(db.String)

    def __repr__(self):
        return f'<Artist.ID: {self.id}, Artist.Name: {self.name}>, Artist.City: {self.city}, Artist.State: {self.state}, Artist.genres: {self.genres}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Show.ID: {self.id}, Show.venue_id: {self.venue_id}>, Show.artist_id: {self.artist_id}, Show.start_time: {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  #data=[{
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "venues": [{
  #    "id": 1,
  #    "name": "The Musical Hop",
  #    "num_upcoming_shows": 0,
  #  }, {
  #    "id": 3,
  #    "name": "Park Square Live Music & Coffee",
  #    "num_upcoming_shows": 1,
  #  }]
  #}, {
  #  "city": "New York",
  #  "state": "NY",
  #  "venues": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}]

  cityAndstateData  = db.session.query(Venue.city, Venue.state).group_by(Venue.city,Venue.state).all();
  venueAndShowData  = db.session.query(Venue, Show).filter(Venue.id == Show.venue_id).all();
  data              = []
  today             = datetime.today()
  today             = today.strftime("%m/%d/%Y %H:%M:%S")
  for csdata in cityAndstateData:
    venue_data = []
    for vsdata in venueAndShowData:
      if vsdata.Venue.city == csdata[0] and vsdata.Venue.state == csdata[1] :
        noofshows   = 0        
        if vsdata.Show.start_time > today:
          noofshows = 1
        temp_venue_data = { "id" : vsdata.Venue.id,
        "name" : vsdata.Venue.name, "num_upcoming_shows": noofshows}
        venue_data.append(temp_venue_data)
    temp_cs         = { "city" : csdata.city,
                        "state" : csdata.state,
                        "venues" : venue_data}
    data.append(temp_cs)
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form['search_term']
  #print('print value of search_term:' ,search_term)

  venues = db.session.query(Venue).filter(Venue.name.ilike('%'+search_term+'%')).all()
  
  noofmatchingrecord = len(venues)
  #print ('noofmatchingrecord', noofmatchingrecord)
  if noofmatchingrecord == 0:
    response = { "count" : noofmatchingrecord }
  else:
    venue_dict = []
    for venue in venues:
      temp_dict = {
        "id": venue.id,
        "name": venue.name
      }
      venue_dict.append(temp_dict)
    response = { "count" : noofmatchingrecord ,
      "data" : venue_dict
    }

  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data1={
  #  "id": 1,
  #  "name": "The Musical Hop",
  #  "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #  "past_shows": [{
  #    "artist_id": 4,
  #    "artist_name": "Guns N Petals",
  #    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data2={
  #  "id": 2,
  #  "name": "The Dueling Pianos Bar",
  #  "genres": ["Classical", "R&B", "Hip-Hop"],
  #  "address": "335 Delancey Street",
  #  "city": "New York",
  #  "state": "NY",
  #  "phone": "914-003-1132",
  #  "website": "https://www.theduelingpianos.com",
  #  "facebook_link": "https://www.facebook.com/theduelingpianos",
  #  "seeking_talent": False,
  #  "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #  "past_shows": [],
  #  "upcoming_shows": [],
  #  "past_shows_count": 0,
  #  "upcoming_shows_count": 0,
  #}
  #data3={
  #  "id": 3,
  #  "name": "Park Square Live Music & Coffee",
  #  "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #  "address": "34 Whiskey Moore Ave",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "415-000-1234",
  #  "website": "https://www.parksquarelivemusicandcoffee.com",
  #  "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #  "seeking_talent": False,
  #  "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #  "past_shows": [{
  #    "artist_id": 5,
  #    "artist_name": "Matt Quevedo",
  #    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
  #  "upcoming_shows": [{
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-01T20:00:00.000Z"
  #  }, {
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-08T20:00:00.000Z"
  #  }, {
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-15T20:00:00.000Z"
  #  }],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 1,
  #}
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  venue = db.session.query(Venue).filter_by(id = venue_id).first()

  today             = datetime.today()
  today             = today.strftime("%m/%d/%Y %H:%M:%S")

  genres = venue.genres  

  if venue.genres != None:
    genres = genres[1: len(genres)-1]
    venue.genres = genres.split(',')

  data = venue.__dict__

  past_shows  = db.session.query(Venue.id, Show.id, Artist.id,Artist.name,Artist.image_link,Show.start_time).join(Venue).join(Artist)\
                .filter(Venue.id == venue_id).filter(Show.start_time < today).all()

  pshow_dict = []
  if len(past_shows) > 0 :
    temp_dict = []
    for pshow in past_shows:
      temp_dict = { 
                    "artist_id" : pshow[2],
                    "artist_name" : pshow[3],
                    "artist_image_link" : pshow[4],
                    "start_time" : pshow[5]
                   }
      pshow_dict.append(temp_dict)
    data.update({"past_shows" : pshow_dict })

  upcoming_shows  = db.session.query(Venue.id, Show.id, Artist.id,Artist.name,Artist.image_link,Show.start_time).join(Venue).join(Artist)\
                .filter(Venue.id == venue_id).filter(Show.start_time > today).all()


  ushow_dict = []
  if len(upcoming_shows) > 0 :
    temp_dict = []
    for ushow in upcoming_shows:
      temp_dict = { 
                    "artist_id" : ushow[2],
                    "artist_name" : ushow[3],
                    "artist_image_link" : ushow[4],
                    "start_time" : ushow[5]
                   }
      ushow_dict.append(temp_dict)
    data.update({"upcoming_shows" : ushow_dict })

  past_shows_count = len(past_shows)
  
  upcoming_shows_count = len(upcoming_shows)

  data.update({"past_shows_count" : past_shows_count})
  data.update({"upcoming_shows_count" : upcoming_shows_count})

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  transaction   = "success"
  venue         = ""
  venue_name    = request.form['name']
  try:
    venue = Venue(name=request.form['name'], city=request.form['city'],
    address=request.form['address'], state=request.form['state'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'), 
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'],
    seeking_talent=request.form['seeking_talent'],
    seeking_description=request.form['seeking_description'])
  except:
    transaction = "failed"
    db.session.rollback()
  finally:
    db.session.close()

  if transaction == "success":
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue_name + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + venue_name + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #data=[{
  #  "id": 4,
  #  "name": "Guns N Petals",
  #}, {
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #}, {
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #}]
  data = Artist.query.order_by('id').all();
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  #print('print value of search_term:' ,search_term)

  artists = db.session.query(Artist).filter(Artist.name.ilike('%'+search_term+'%')).all()
  
  #print (artists)
  #print (artists[0])
  noofmatchingrecord = len(artists)
  #print ('noofmatchingrecord', noofmatchingrecord)
  if noofmatchingrecord == 0:
    response = { "count" : noofmatchingrecord }
  else:
    artist_dict = []
    for artist in artists:
      temp_dict = {
        "id": artist.id,
        "name": artist.name
      }
      artist_dict.append(temp_dict)
    #print("dictionary", artist_dict)
    response = { "count" : noofmatchingrecord ,
      "data" : artist_dict
    }

  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 4,
  #    "name": "Guns N Petals",
  #    "num_upcoming_shows": 0,
  #  }]
  #}


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data1={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #  "past_shows": [{
  #    "venue_id": 1,
  #    "venue_name": "The Musical Hop",
  #    "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data2={
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #  "genres": ["Jazz"],
  #  "city": "New York",
  #  "state": "NY",
  #  "phone": "300-400-5000",
  #  "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #  "seeking_venue": False,
  #  "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #  "past_shows": [{
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data3={
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #  "genres": ["Jazz", "Classical"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "432-325-5432",
  #  "seeking_venue": False,
  #  "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "past_shows": [],
  #  "upcoming_shows": [{
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-01T20:00:00.000Z"
  #  }, {
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-08T20:00:00.000Z"
  #  }, {
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-15T20:00:00.000Z"
  #  }],
  #  "past_shows_count": 0,
  #  "upcoming_shows_count": 3,
  #}
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

  artist = db.session.query(Artist).filter_by(id = artist_id).first()

  today  = datetime.today()
  today  = today.strftime("%m/%d/%Y %H:%M:%S")

  genres = artist.genres  

  if artist.genres != None:
    genres = genres[1: len(genres)-1]
    artist.genres = genres.split(',')

  data = artist.__dict__

  past_shows  = db.session.query(Artist.id, Show.id, Venue.id,Venue.name,Venue.image_link,Show.start_time).join(Venue).join(Artist)\
                .filter(Artist.id == artist_id).filter(Show.start_time < today).all()

  pshow_dict = []
  if len(past_shows) > 0 :
    temp_dict = []
    for pshow in past_shows:
      temp_dict = { 
                    "venue_id" : pshow[2],
                    "venue_name" : pshow[3],
                    "venue_image_link" : pshow[4],
                    "start_time" : pshow[5]
                   }
      pshow_dict.append(temp_dict)
    data.update({"past_shows" : pshow_dict })

  upcoming_shows  = db.session.query(Artist.id, Show.id, Venue.id,Venue.name,Venue.image_link,Show.start_time).join(Venue).join(Artist)\
                .filter(Artist.id == artist_id).filter(Show.start_time > today).all()


  ushow_dict = []
  if len(past_shows) > 0 :
    temp_dict = []
    for pshow in past_shows:
      temp_dict = { 
                    "venue_id" : pshow[2],
                    "venue_name" : pshow[3],
                    "venue_image_link" : pshow[4],
                    "start_time" : pshow[5]
                   }
      ushow_dict.append(temp_dict)
    data.update({"upcoming_shows" : ushow_dict })

  past_shows_count = len(past_shows)
  
  upcoming_shows_count = len(upcoming_shows)

  data.update({"past_shows_count" : past_shows_count})
  data.update({"upcoming_shows_count" : upcoming_shows_count})

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #artist={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  #}

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  print ("artist: ", artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = db.session.query(Artist).filter_by(id = artist_id).first()

  artist.id = artist_id
  artist.name=request.form['name']
  artist.city=request.form['city']
  artist.state=request.form['state']
  artist.phone=request.form['phone']
  artist.genres=request.form.getlist('genres')
  artist.facebook_link=request.form['facebook_link']
  artist.image_link=request.form['image_link']
  artist.seeking_venue=request.form['seeking_venue']

  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  #venue={
  #  "id": 1,
  #  "name": "The Musical Hop",
  #  "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  #}
  # TODO: populate form with values from venue with ID <venue_id>
  venue = db.session.query(Venue).filter_by(id = venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = db.session.query(Venue).filter_by(id = venue_id).first()

  venue.id = venue_id
  venue.name=request.form['name']
  venue.city=request.form['city']
  venue.address=request.form['address']
  venue.state=request.form['state']
  venue.phone=request.form['phone']
  venue.genres=request.form.getlist('genres')
  venue.image_link=request.form['image_link']
  venue.facebook_link=request.form['facebook_link']
  venue.seeking_talent=request.form['seeking_talent']
  venue.seeking_description=request.form['seeking_description']

  db.session.commit()
  
  #return redirect(url_for('show_venue', venue_id=venue_id))
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  transaction   = "success"
  artist        = ""
  artist_name    = request.form['name']
  try:
    artist = Artist(name=request.form['name'], city=request.form['city'],
    #address=request.form['address'], 
    state=request.form['state'],
    phone=request.form['phone'], 
    genres=request.form.getlist('genres'),
    seeking_venue=request.form['seeking_venue'],
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'])
  except:
    transaction = "failed"
    db.session.rollback()
    print ("Unexpected error:", sys.exc_info()[0])
  finally:
    db.session.close()

  if transaction == "success":
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist_name + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + artist_name + ' could not be listed.')

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  #data=[{
  #  "venue_id": 1,
  #  "venue_name": "The Musical Hop",
  #  "artist_id": 4,
  #  "artist_name": "Guns N Petals",
  #  "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #  "start_time": "2019-05-21T21:30:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 5,
  #  "artist_name": "Matt Quevedo",
  #  "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #  "start_time": "2019-06-15T23:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-01T20:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-08T20:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-15T20:00:00.000Z"
  #}]

  dataarr = db.session.query(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).filter(Venue.id == Show.venue_id).filter(Artist.id == Show.artist_id).all()
  data = []
  for objlist in dataarr:
    tempdict = { 
      "venue_id" : objlist[0],
      "venue_name" : objlist[1],
      "artist_id" : objlist[2],
      "artist_image_link": objlist[3],
      "artist_image_link": objlist[4],
      "start_time": objlist[5]
    }
    data.append(tempdict)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  transaction = True
  show = None
  duplicate = False
  venue_id= 0
  artist_id= 0
  start_time = None
  try:
    venue_id=request.form['venue_id']
    artist_id=request.form['artist_id']
    start_time=request.form['start_time']
    show = db.session.query(Show).filter_by(venue_id = venue_id).filter_by(artist_id = artist_id).filter_by(start_time = start_time).all()
    
    if len(show) == 0:
      show = Show(venue_id=venue_id,
                  artist_id=artist_id,
                  start_time=start_time)
      db.session.add(show)
      db.session.commit()
    else :
      transaction = False
      duplicate = True
  except:
    db.session.rollback()
    transaction = False
    print ("Unexpected error:", sys.exc_info()[0])
  finally:
    db.session.close()

  # on successful db insert, flash success
  if transaction == True:
    flash('Show was successfully listed!')
  else:
    if duplicate == True:
      flash('Show on ('+start_time+') already registered with Venue Id ('+venue_id+') Artist Id ('+artist_id+')')
    else:
      flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
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
