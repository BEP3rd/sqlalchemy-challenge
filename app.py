import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

engine =create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect and existing database
Base = automap_base()
#Refelct the tables
Base.prepare(engine, reflect=True)

#Save the refrences to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create app
app = Flask(__name__)

# Routes

# /
# Home page.
# List all routes that are available.
@app.route("/")
def home():

    return (
        f"<h2>Routes for the Climate App</h2> <br>"
        
        f"<ul> <li> /api/v1.0/precipitation </li><br>"
        f"<li>/api/v1.0/stations</li> <br>"
        f"<li>/api/v1.0/tobs </li><br>"
        "The following routes are interactive. <br/>"
        "Replace YYYY-MM-DD with dates between 2010-01-01 and 2017-08-23 for statistics after start date and before end date <br/>"
        "<br/>"
        f"<li>/api/v1.0/YYYY-MM-DD </li>"
        f"<li>/api/v1.0/YYYY-MM-DD /YYYY-MM-DD </li>"
    )



# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    db_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    dateOI = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= dateOI)

    session.close()

    prcp_dict = {}
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    return jsonify(prcp_dict)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()

    station_list = list(np.ravel(stations))

    return jsonify(station_list)
    
# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    busiest_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    busiest_station = busiest_stations.station
    dateOI = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    station_tobs = session.query(Measurement.tobs).filter(Measurement.station == busiest_station).filter(Measurement.date >= dateOI).all()
    station_data = list(np.ravel(station_tobs))
    session.close()
    return jsonify(station_data)





# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    stats = session.query(*[func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]).filter(Measurement.date >= start).all()
    stats_list  = list(np.ravel(stats))
    session.close()
    return jsonify(stats_list)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
    stats = session.query(*[func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    stats_list  = list(np.ravel(stats))
    session.close()
    return jsonify(stats_list)

if __name__ == "__main__":
    app.run(debug=True)