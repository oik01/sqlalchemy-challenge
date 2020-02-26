

from flask import Flask, jsonify
from sqlalchemy import create_engine, inspect, func, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Design a query to retrieve the last 12 months of precipitation data and plot the results
con = engine.connect()

app = Flask(__name__)

@app.route('/')
def home_page():
    print(' server routed to homepage')
    return 'Hello! Following is a list of available routes: \n /api/v1.0/precipitation : JSON dictionary of precipitation by date \n /api/v1.0/stations  : JSON list of stations \n /api/v1.0/tobs  : JSON dictionary of temperature by dates during a year \n /api/v1.0/<start> : Tmin, Tavg, and Tmax following start date \n api/v1.0/<start>/<end>: Tmin, Tavg, and Tmax between dates \n'

@app.route('/api/v1.0/precipitation')
def precip():

    print( ' server request for precipitation data')
    # figure out last date so I can figure out the date before the last 12 months
    session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Query data more than the date 12 months before the last date
    data = session.query(measurement.date, measurement.prcp).filter(measurement.date > dt.date(2016,8,23)).order_by(measurement.date.asc()).all()
    precipitation_data = []
    for date, precipitation in data:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['precipitation'] = precipitation
        precipitation_data.append(precipitation_dict)
    
    return jsonify(precipitation_data)



@app.route('/api/v1.0/stations')
def stations():

    print( ' server request for stations data')
    # figure out unique stations
    records = session.query(measurement.station).group_by(measurement.station).all()
    stations = list(np.ravel(records))
    return jsonify(stations)
    
@app.route('/api/v1.0/tobs')
def temperatures_12mo():

    print( ' server request for temperature data')
    # obtaine information from last 12 months
    query_date = dt.date(2016,8,18)
    records= session.query(measurement.date, measurement.tobs, measurement.station).filter(measurement.date > query_date).all()
    #unpack
    temp_data = []
    for date, temperature, station in records:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['temperature'] = temperature
        temp_dict['station'] = station
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route('/api/v1.0/<start>', methods=['GET'])
def calc_temps(start):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    print( ' server request for temperature data')
    date = dt.datetime.strptime(start, '%Y-%m-%d')
    record = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= date).all()
    for min_temp, avg_temp, max_temp in record:

        return (
            f'minimum temperature is {min_temp}<br/>'
            f'maximum temperature is {max_temp}<br/>'
            f'average temperature is {avg_temp}<br/>'
            )


@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def calc_temps_2dates(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    print( ' server request for temperature data')
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    record = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    for min_temp, avg_temp, max_temp in record:

        return (
            f'minimum temperature is {min_temp}<br/>'
            f'maximum temperature is {max_temp}<br/>'
            f'average temperature is {avg_temp}<br/>'
            )

