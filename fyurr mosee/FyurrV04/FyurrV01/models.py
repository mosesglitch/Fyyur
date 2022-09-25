from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Show(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  venue_id=db.Column(db.ForeignKey('venue.id'),nullable=False)
  artist_id=db.Column(db.ForeignKey('artist.id'),nullable=False)
  start_time=db.Column(db.String())

class Venue(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    shows=db.relationship('Show',  backref="venue",lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city}.>'

class Artist(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    shows=db.relationship('Show',backref='artist',lazy=True)

    
