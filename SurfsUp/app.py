# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime, timedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# SQLALCHEMY engine creation
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

app=Flask(__name__)

#Variables
Recent1 = "2017-08-23"
date_precipitation = dt.date (2017,8,23) - dt.timedelta(days = 365)
station_counter = func.count(Measurement.station)
Station_Activity = session.query(Measurement.station, station_counter).group_by(Measurement.station).order_by(station_counter.desc()).all()
print(Station_Activity)
session.close()
Oldest1=session.query(Measurement.date).order_by(Measurement.date).first()
print(f'The oldest data point listed was on {Oldest1}')
Recent1=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
print(f'The most recent data point listed was on {Recent1}')

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"/api/v1.0/precipitation<br/>"    
        f"/api/v1.0/stations<br/>"    
        f"/api/v1.0/tobs<br/>"   
        f"/api/v1.0/<start>  date format mm-dd-yyyy(start date)<br/>"     
        f"//api/v1.0/<start>/<end>  date format mm-dd-yyyy(start date / end date)"  
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    query=session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= date_precipitation).\
        order_by(Measurement.date).all()
    session.close()

    precipitations = []
    for date, prcp in query:
        precipitation_dict ={}
        precipitation_dict["prcp"]= prcp
        precipitation_dict["date"]= date
        precipitations.append(precipitation_dict)

    return jsonify(precipitations)


@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    query=session.query(Station.station).all()
    session.close()
    query_list = list(np.ravel(query))
    return jsonify(query_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs1 = session.query(Measurement.tobs, Station.name, Measurement.date).\
        filter(Measurement.date >= date_precipitation)
    tobs_list = []
    for i in tobs1:
        tobs = {}
        tobs['Date'] = i[1]
        tobs['Station'] = i[0]
        tobs['Temperature'] = i[2]
        tobs_list.append(tobs)
        session.close()
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_stats(start):
    session = Session(engine)
    tmin= func.min(Measurement.tobs)
    tmax= func.max(Measurement.tobs)
    tavg= func.max(Measurement.tobs)
    statistics_query = session.query(tmin,tmax,tavg).\
        filter(Measurement.date.between(("2012-01-01"), ("2012-08-23"))).all()
    session.close()

    statistics_list = []
    for min, max, avg in statistics_query:
        statistics_dict = {}
        statistics_dict["Min"] = min
        statistics_dict["Avg"] = avg
        statistics_dict["Max"] = max
        statistics_list.append(statistics_dict)
    return jsonify(statistics_list)


@app.route("//api/v1.0/<start>/<end>")
def start_end(start, end):
    session =Session(engine)
    tmin= func.min(Measurement.tobs)
    tmax= func.max(Measurement.tobs)
    tavg= func.max(Measurement.tobs)
    statistics_query2 = session.query(tmin,tmax,tavg).\
        filter(Measurement.date.between(("2010-01-01"), ("2017-08-23"))).all()
    session.close()

    statistics_list2 = []
    for min, max, avg in statistics_query2:
        statistics_dict2 = {}
        statistics_dict2["Min"] = min
        statistics_dict2["Avg"] = avg
        statistics_dict2["Max"] = max
        statistics_list2.append(statistics_dict2)
    return jsonify(statistics_list2)

if __name__ == '__main__':
    app.run(debug=True)