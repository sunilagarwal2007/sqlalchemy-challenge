import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
#List all routes that are available
@app.route("/")
def welcome():

     return (
         f"/api/v1.0/precipitation<br/>"
         f"/api/v1.0/stations<br/>"
         f"/api/v1.0/tobs<br/>"
         f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start>/<end><br/>"
     )


@app.route("/api/v1.0/precipitation")
def precip():
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    #find date 12 months before
    last_year_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    results = query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year_date).all()

    rain_season = []
    for date, prcp in results:
        data = {}
        data['date'] = date
        data['prcp'] = prcp
        rain_season.append(data)

    return jsonify(rain_season)


@app.route("/api/v1.0/stations")
def stations():
    
    results = session.query(Station.name, Station.station, Station.elevation).all()

    #create dictionary for JSON
    station_list = []
    for result in results:
        row = {}
        row['name'] = result[0]
        row['station'] = result[1]
        row['elevation'] = result[2]
        station_list.append(row)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature_tobs():
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2017-01-01", Measurement.date <= "2018-01-01").\
        all()

    #use dictionary, create json
    tobs_list = []
    for result in results:
        row = {}
        row["Date"] = result[1]
        row["Station"] = result[0]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(
        Measurement.date).all()
    from_start_list = list(from_start)
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(
        Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list = list(between_dates)
    return jsonify(between_dates_list)

if __name__ == "__main__":
    app.run(debug=True)
