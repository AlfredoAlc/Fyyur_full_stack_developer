#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.String(), nullable=False)
    


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    time_created = db.Column(db.String(), nullable=False)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    time_created = db.Column(db.String(), nullable=False)
    
    venues = db.relationship('Venue', secondary='show', backref=db.backref('shows', lazy=True))


# TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    elif format == 'small':
        format="MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

    venues = Venue.query.order_by(Venue.time_created.desc()).all()
    artists = Artist.query.order_by(Artist.time_created.desc()).all()
    data_to_sort =[]
    data=[]

    for venue in venues:
        temp={}
        temp['venue_id']= venue.id
        temp['venue_name']=venue.name
        temp['time_created']=venue.time_created
        data_to_sort.append(temp)

    for artist in artists:
        temp={}
        temp['artist_id']=artist.id
        temp['artist_name']=artist.name
        temp['time_created']=artist.time_created
        data_to_sort.append(temp)

    data_to_sort.sort(key=lambda x:x['time_created'], reverse=True)

    for data_sorted in data_to_sort:
        if(len(data) < 10):
            data.append(data_sorted)


    
    return render_template('pages/home.html', recent_listing=data)


#  Venues
#  ----------------------------------------------------------------

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/venues')
def venues():

    venues = Venue.query.order_by(Venue.city, Venue.state).all()

    data = []
    temp = {}
    prev_city = None
    prev_state = None

    if len(venues) > 0:
        for venue in venues:
            venue_data = {
                'id': venue.id,
                'name': venue.name,
            }
            if venue.city == prev_city and venue.state == prev_state:
                        temp['venues'].append(venue_data)
            else:
                if prev_city is not None:
                    data.append(temp)
                    temp = {}
                temp['city'] = venue.city
                temp['state'] = venue.state
                temp['venues'] = [venue_data]
            prev_city = venue.city
            prev_state = venue.state

        data.append(temp)

    return render_template('pages/venues.html', areas=data)

# TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

@app.route('/venues/search', methods=['POST'])
def search_venues():
    
    search_term = request.form.get('search_term')
    venues_by_name = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    venues_by_location = Venue.query.filter(or_(Venue.state.ilike('%{}%'.format(search_term)), Venue.city.ilike('%{}%'.format(search_term)))).all()
    
    data_by_name = []
    data_by_location = []

    for venue_name in venues_by_name:
        temp={}
        temp['id']=venue_name.id
        temp['name']=venue_name.name
        data_by_name.append(temp)

    response_by_name={}
    response_by_name['count']=len(data_by_name)
    response_by_name['data']=data_by_name

    for venue_location in venues_by_location:
        temp={}
        temp['id']=venue_location.id
        temp['name']=venue_location.name
        data_by_location.append(temp)

    response_by_location={}
    response_by_location['count']=len(data_by_location)
    response_by_location['data']=data_by_location

    
    return render_template('pages/search_venues.html', results_by_name=response_by_name, results_by_location=response_by_location, search_term=request.form.get('search_term', ''))

# shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


@app.route('/venues/<venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    shows =  Show.query.filter(Show.venue_id==venue_id).all()

    past_shows = []
    upcoming_shows = []
    date_list =[]

    if len(shows) > 0:
        for show in shows:
            artist = Artist.query.get(show.artist_id)
            date_compared = format_datetime(str(datetime.today()), 'small') < format_datetime(show.start_time, 'small')
            temp={}
            temp['artist_image_link']=artist.image_link
            temp['artist_id']=show.artist_id
            temp['artist_name']=artist.name
            temp['start_time']=show.start_time
            if(date_compared):
                upcoming_shows.append(temp)
            else:
                past_shows.append(temp)


    genre_list = venue.genres.split(',')

    data = {}
    data['id']=venue.id
    data['name']=venue.name
    data['city']=venue.city
    data['state']=venue.state
    data['address']=venue.address
    data['phone']=venue.phone
    data['genres']= genre_list
    data['image_link']=venue.image_link
    data['facebook_link']=venue.facebook_link
    data['website']=venue.website
    data['seeking_talent']=venue.seeking_talent
    data['seeking_description']=venue.seeking_description
    data['past_shows']=past_shows
    data['upcoming_shows']=upcoming_shows
    data['past_shows_count']=len(past_shows)
    data['upcoming_shows_count']=len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)

# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    error = False
    seek_talent = 'n'

    try:
        seek_talent = request.form['seeking_talent_bool']
    except:
        seek_talent = 'n'
    finally:
        try:
            venue = Venue()
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.phone = request.form['phone']
            tmp_genres = request.form.getlist('genres')
            venue.genres = ', '.join(tmp_genres)
            venue.facebook_link = request.form['facebook_link']
            venue.image_link = request.form['image_link']
            venue.website = request.form['website']
            if seek_talent == 'y':
                venue.seeking_talent = True
            else:
                venue.seeking_talent = False
            venue.seeking_description = request.form['seeking_talent_desc']
            venue.time_created = format_datetime(str(datetime.today()), 'small')
            db.session.add(venue)
            db.session.commit()

        except:
            error = True
            db.session.rollback()

        finally:
            db.session.close()
            if error:
                flash('An error happened, Venue ' + request.form['name'] + ' could not be listed!')
            else:
                flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return redirect(url_for('index'))


# TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))

# TODO: take values from the form submitted, and update existing
# venue record with ID <venue_id> using the new attributes

@app.route('/venues/<venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    
    error = False
    seek_talent ='n'

    try:
        seek_talent = request.form['seeking_talent_bool']
    except:
        seek_talent = 'n'
    finally:
        try:
            venue = Venue.query.get(venue_id)
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.phone = request.form['phone']
            temp_genres = request.form.getlist('genres')
            venue.genres = ','.join(temp_genres)
            venue.facebook_link = request.form['facebook_link']
            venue.image_link = request.form['image_link']
            venue.website = request.form['website']
            if seek_talent == 'y':
                venue.seeking_talent = True
            else:
                venue.seeking_talent = False
            venue.seeking_description = request.form['seeking_talent_desc']
            venue.time_created = format_datetime(str(datetime.today()), 'small')
            db.session.commit()

        except:
            error = True
            db.session.rollback()

        finally:
            db.session.close()
            if error:
                flash('An error happened, Venue ' + request.form['name'] + 'could not be edited!')
            else:
                flash('Venue ' + request.form['name'] + ' was successfully edited!')

    return redirect(url_for('show_venue', venue_id=venue_id))


 # TODO: Complete this endpoint for taking a venue_id, and using
 # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

 # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
 # clicking that button delete it from the db then redirect the user to the homepage

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        Show.query.filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
# TODO: replace with real data returned from querying the database


@app.route('/artists')
def artists():

    return render_template('pages/artists.html', artists=Artist.query.all())

# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
# search for "band" should return "The Wild Sax Band".

@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term')
    artists_by_name = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    artists_by_location = Artist.query.filter(or_(Artist.city.ilike('%{}%'.format(search_term)), Artist.state.ilike('%{}%'.format(search_term)))).all()

    data_by_name = []
    data_by_location = []

    for artist_by_name in artists_by_name:
        temp={}
        temp['id']=artist_by_name.id
        temp['name']=artist_by_name.name
        data_by_name.append(temp)

    response_by_name={}
    response_by_name['count']=len(data_by_name)
    response_by_name['data']=data_by_name

    for artist_by_location in artists_by_location:
        temp={}
        temp['id']=artist_by_location.id
        temp['name']=artist_by_location.name
        data_by_location.append(temp)

    response_by_location={}
    response_by_location['count']=len(data_by_location)
    response_by_location['data']=data_by_location
        

    return render_template('pages/search_artists.html', results_by_name=response_by_name, results_by_location=response_by_location, search_term=request.form.get('search_term', ''))


# shows the aritst page with the given venue_id
# TODO: replace with real artist data from the venues table, using venue_id

@app.route('/artists/<artist_id>')
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)
    shows =  Show.query.filter(Show.artist_id==artist_id).all()

    past_shows = []
    upcoming_shows = []
    date_list =[]

    if len(shows) > 0:
        for show in shows:
            venue = Venue.query.get(show.venue_id)
            date_compared = format_datetime(str(datetime.today()), 'small') < format_datetime(show.start_time, 'small')
            temp={}
            temp['venue_image_link']=venue.image_link
            temp['venue_id']=show.venue_id
            temp['venue_name']=venue.name
            temp['start_time']=show.start_time
            if(date_compared):
                upcoming_shows.append(temp)
            else:
                past_shows.append(temp)

    genre_list = artist.genres.split(',')

    data = {}
    data['id']=artist.id
    data['name']=artist.name
    data['city']=artist.city
    data['state']=artist.state
    data['phone']=artist.phone
    data['genres']=genre_list
    data['image_link']=artist.image_link
    data['facebook_link']=artist.facebook_link
    data['seeking_venue']=artist.seeking_venue
    data['seeking_description']=artist.seeking_description
    data['past_shows']=past_shows
    data['upcoming_shows']=upcoming_shows
    data['past_shows_count']=len(past_shows)
    data['upcoming_shows_count']=len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
# TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))

 # TODO: take values from the form submitted, and update existing
 # artist record with ID <artist_id> using the new attributes


@app.route('/artists/<artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    error = False
    seek_venue ='n'

    try:
        seek_venue = request.form['seeking_venue_bool']
    except:
        seek_venue = 'n'
    finally:
        try:
            artist = Artist.query.get(artist_id)
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            temp_genres = request.form.getlist('genres')
            artist.genres = ','.join(temp_genres)
            artist.facebook_link = request.form['facebook_link']
            artist.image_link = request.form['image_link']
            artist.website = request.form['website']
            if seek_venue == 'y':
                artist.seeking_venue = True
            else:
                artist.seeking_venue = False
            artist.seeking_description = request.form['seeking_venue_desc']
            artist.time_created = format_datetime(str(datetime.today()), 'small')
            db.session.commit()

        except:
            error = True
            db.session.rollback()

        finally:
            db.session.close()
            if error:
                flash('An error happened, Artist ' + request.form['name'] + 'could not be edited!')
            else:
                flash('Artist ' + request.form['name'] + ' was successfully edited!')

    return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():

    form = ArtistForm()

    return render_template('forms/new_artist.html', form=form)

# called upon submitting the new artist listing form
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion

# on successful db insert, flash success
# flash('Artist ' + request.form['name'] + ' was successfully listed!')
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    error = False
    seek_venue ='n'

    try:
        seek_venue = request.form['seeking_venue_bool']
    except:
        seek_venue = 'n'
    finally:
        try:
            artist = Artist()
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            temp_genres = request.form.getlist('genres')
            artist.genres = ','.join(temp_genres)
            artist.facebook_link = request.form['facebook_link']
            artist.image_link = request.form['image_link']
            artist.website = request.form['website']
            if seek_venue == 'y':
                artist.seeking_venue = True
            else:
                artist.seeking_venue = False
            artist.seeking_description = request.form['seeking_venue_desc']
            artist.time_created = format_datetime(str(datetime.today()), 'small')
            db.session.add(artist)
            db.session.commit()

        except:
            error = True
            db.session.rollback()

        finally:
            db.session.close()
            if error:
                flash('An error happened, Artist ' + request.form['name'] + ' could not be listed!')
            else:
                flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
    return redirect(url_for('index'))


@app.route('/artist/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):

    try:
        Show.query.filter_by(artist_id=artist_id).delete()
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return jsonify({'success': True})

#  Shows
#  ----------------------------------------------------------------

# displays list of shows at /shows
# TODO: replace with real venues data.
# num_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/shows')
def shows():

    shows = Show.query.all()

    show_info = []
    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        temp = {}
        temp['venue_id']=show.venue_id
        temp['artist_id']=show.artist_id
        temp['artist_name']=artist.name
        temp['venue_name']=venue.name
        temp['artist_image_link']=artist.image_link
        temp['start_time']=show.start_time
        show_info.append(temp)
    

    return render_template('pages/shows.html', shows=show_info)

# renders form. do not touch.

@app.route('/shows/create')
def create_shows():

    form = ShowForm()

    return render_template('forms/new_show.html', form=form)

# called to create new shows in the db, upon submitting new show listing form
# TODO: insert form data as a new Show record in the db, instead
# on successful db insert, flash success flash('Show was successfully listed!')
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Show could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    error = False

    try:
        show = Show()
        show.artist_id = request.form['artist_id']
        show.venue_id = request.form['venue_id']
        show.start_time = request.form['start_time']
        db.session.add(show)
        db.session.commit()
        
    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()
        if error:
            flash('An error happened, Show could not be listed!')
        else:
            flash('Show was successfully listed!')
            

    return redirect(url_for('index'))

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
