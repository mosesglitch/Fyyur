#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from ssl import ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY
import dateutil.parser
import babel
from flask import (Flask, 
                  render_template,
                  jsonify,
                  request, 
                  Response, 
                  abort,flash, 
                  redirect, 
                  url_for)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime
import os
from models import db, Show, Venue, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="y:MM:dd"
  elif format=='please':
      format="Y/MM/dd h:mm:s"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_artists=db.session.query(Artist).order_by(Artist.id).limit(10)
  recent_venues=db.session.query(Venue).order_by(Venue.id).limit(10)

  return render_template('pages/home.html', recent_artists=recent_artists,recent_venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  locals=[]
  venues=Venue.query.all()
  places=Venue.query.distinct(Venue.city,Venue.state).all()
  for place in places:
    locals.append({
      'city':place.city,
      'state':place.state,
      'venues':[{
           'id':venue.id,
           'name':venue.name,}
            for venue in venues if venue.city ==place.city and venue.state ==place.state
      ]})

  return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term=request.form.get('search_term', '')
  response=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  upcoming=db.session.query(Show).join(Venue).join(Artist).filter_by(id=venue_id).all()
  upcoming_shows=[]
  past_shows=[]

  for x in upcoming:
    current_date=datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    sd=format_datetime(x.start_time, format='please')
    show_date = datetime.strptime(sd, '%Y/%m/%d %H:%M:%S').date()
    cd=datetime.strptime(current_date,"%Y/%m/%d %H:%M:%S").date()
    formatted_date=format_datetime(x.start_time, format='medium')
    if cd<show_date:
      upcoming_shows.append({
        'artist_id':x.artist.id,
        'artist_name':x.artist.name,
        'artist_image_link':x.artist.image_link,
        'start_time':formatted_date,
      })
    else:
      past_shows.append({
        'artist_id':x.venue.id,
        'artist_name':x.venue.name,
        'artist_image_link':x.artist.image_link,
        'start_time':formatted_date,
      })
  venue=Venue.query.filter_by(id=venue_id).order_by('id').first()
  return render_template('pages/show_venue.html', venue=venue, upcoming_shows=upcoming_shows,past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    venue=Venue(
    name =form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    genres = form.genres.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data,
    website_link = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    )
    db.session.add(venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except Exception as e:
        db.session.rollback()
        print(e)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()
    
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error=False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was deleted!')
  except Exception as e:
    db.session.rollback()
    flash('Venue was not deleted! Please check if there are any existing shows or atists')
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return jsonify({'success': True})

  render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term=request.form.get('search_term', '')
  response=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  datals=Artist.query.filter_by(id=artist_id).first()
  upcoming=db.session.query(Show).join(Venue).join(Artist).filter_by(id=artist_id).all()
  upcoming_shows=[]
  past_shows=[]

  for x in upcoming:
    current_date=datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    sd=format_datetime(x.start_time, format='please')
    show_date = datetime.strptime(sd, '%Y/%m/%d %H:%M:%S').date()
    cd=datetime.strptime(current_date,"%Y/%m/%d %H:%M:%S").date()
    formatted_date=format_datetime(x.start_time, format='medium')
    if cd<show_date:
      upcoming_shows.append({
        'venue_id':x.venue.id,
        'venue_name':x.venue.name,
        'venue_image_link':x.venue.image_link,
        'start_time':formatted_date,
      })
    else:
      past_shows.append({
        'venue_id':x.venue.id,
        'venue_name':x.venue.name,
        'venue_image_link':x.venue.image_link,
        'start_time':formatted_date,
      })
  return render_template('pages/show_artist.html', artist=datals,past_shows=past_shows,upcoming_shows=upcoming_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }

  artist=Artist.query.filter_by(id=artist_id).first()
  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.genres.data=artist.genres
  form.facebook_link.data=artist.facebook_link
  form.image_link.data=artist.image_link
  form.website_link.data=artist.website_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  name = request.form['name']
  city = request.form['city']
  state = request.form['state'] 
  phone = request.form['phone']
  genres = request.form['genres']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  try:
    seeking_venue = request.form['seeking_venue']
    seeking_venue = True
  except:
    seeking_venue = False

  seeking_description = request.form['seeking_description']

  artist=Artist.query.filter_by(id=artist_id).first()
  
  artist.name=name
  artist.city=city
  artist.state=state
  artist.phone=phone
  artist.genres=genres
  artist.image_link=image_link
  artist.facebook_link=facebook_link
  artist.website_link=website_link
  artist.seeking_venue=seeking_venue
  artist.seeking_description=seeking_description
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue=Venue.query.filter_by(id=venue_id).first()
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.genres.data=venue.genres
  form.facebook_link.data=venue.facebook_link
  form.image_link.data=venue.image_link
  form.website_link.data=venue.website_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address=request.form['address'] 
  phone = request.form['phone']
  genres = request.form['genres']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  try:
    seeking_talent = request.form['seeking_talent']
    seeking_talent = True
  except:
    seeking_talent = False

  seeking_description = request.form['seeking_description']

  venue=Venue.query.filter_by(id=venue_id).first()
  
  venue.name=name
  venue.city=city
  venue.state=state
  venue.address=address
  venue.phone=phone
  venue.genres=genres
  venue.image_link=image_link
  venue.facebook_link=facebook_link
  venue.website_link=website_link
  venue.seeking_talent=seeking_talent
  venue.seeking_description=seeking_description

  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)
  try:
    artist=Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    genres = form.genres.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data,
    website_link = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
      )

    db.session.add(artist)
    db.session.commit()
 
    flash('Artist ' + request.form['name'] + '  was successfully listed!')

  except Exception as e:
        db.session.rollback()
        print(e)
        flash('An error occurred. Artist ' + request.form['name'] + '  could not be listed.')
  finally:
      db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  shows_query = db.session.query(Show).join(Artist).join(Venue).all()
  for show in shows_query: 
    print(show.venue_id)
    print(show.venue.name)
    print(show.artist.name)
    print(show.venue.city)
  data = []
  for show in shows_query: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form=ShowForm(request.form)

  try:
    show=Show(
    venue_id = form.venue_id.data,
    artist_id = form.artist_id.data,
    start_time = form.start_time.data
    )

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
 
  except :
    b=sys.exc_info()
    flash('An error occurred. Show could not be listed.Please ensure the Artist_id and Venue_id are valid')
  finally:
      db.session.close()
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
  port = int(os.environ.get('PORT', 5000))
  app.debug=True
  app.run(host='0.0.0.0', port=port)


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
