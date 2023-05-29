# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def Welcome():
    """All Available API Routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )
#Returns json with the date as the key and the value as the precipitation
#Only return the jsonified precipitation data for the last year in the database
#All routes require a extra "/". For example: //api/v1.0/stations

@app.route("/api/v1.0/precipitation")
def precipitation():

    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)

    year_precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago, Measurement.prcp != None).\
    order_by(Measurement.date).all()

    return jsonify(dict(year_precipitation))

#Returns jsonified data of all of the stations in the database
@app.route("/api/v1.0/stations")
def stations():
    session.query(Measurement.station).distinct().count()
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
                               group_by(Measurement.station).\
                               order_by(func.count(Measurement.station).desc()).all()

    return jsonify(dict(active_stations))

#Returns jsonified data for the most active station (USC00519281)
#Only returns the jsonified data for the last year of data

@app.route("/api/v1.0/tobs")
def tobs():
    
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    year_temp = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').\
         order_by(Measurement.tobs).all()

    yr_temp = []
    for y_t in year_temp:
        yrtemp = {}
        yrtemp["tobs"] = y_t.tobs
        yr_temp.append(yrtemp)

    return jsonify(yr_temp)


if __name__ == '__main__':
    app.run(debug=True)
