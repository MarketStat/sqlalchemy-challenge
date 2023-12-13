# Import the dependencies.
import numpy as np
import datetime as dt
from flask import Flask
from flask import jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

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

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return (
        f"Welcome to the Hawaii Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last year<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the last year<br/>"
        f"/api/v1.0/start_date - Temperature statistics from the start date to the end of the dataset<br/>"
        f"/api/v1.0/start_date/end_date - Temperature statistics for a specific date range<br/>"
    )

@app.route('/api/v1.0/precipitation')
### define the precipitation function
def precipitation():
    # subtract 365 days from the latest date in the data set
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Take the date and precipitation information from a year from the latest date to the latest date 
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago_date).all()
    
    session.close()
    
    # Create a dictionary with the precipitation data setting the date as the key and precipitation as the value
    precipitation_data = {date: prcp for date, prcp in results}
    
    # JSONify the precipitation data
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():

    # Query the station data to return all station colun information
    results = session.query(station.station).all()

    # Create a list with all station results using a query
    station_list = [result[0] for result in results]

    # JSONify the station list
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # subtract 365 days from the latest date in the data set
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query the dates and temperature observations of the most-active station for the previous year of data
    active_station = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').filter(measurement.date >= year_ago_date).all()
    
    # Close the session
    session.close()
    
    # Create a dictionary with the precipitation data setting the date as the key and temperature as the value
    most_active = {date: temp for date, temp in active_station}
    return jsonify(most_active)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    
    # Preform a query to retrieve the minimum, maximum, and average temperature for a specified start date to the end of the dataset
    query_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the row data
    start_date = {
        "Minimum Temperature": query_results[0][0],
        "Maxium Temperature": query_results[0][1],
        "Average Temperature": query_results[0][2]
    }
    return jsonify(start_date)
    

@app.route("/api/v1.0/<start>/<end>")
def range_date(start,end):
    session = Session(engine)
    
    # Query for a  list of the minimum temperature, the average temperature, and the max temperature for a specified start or start-end range.
    query_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Close Session                                                
    session.close()
    
    # Create a dictionary from data to list out the minimum, max and average temperatures
    range_date = {
        "Minimum Temperature": query_results[0][0],
        "Maxium Temperature": query_results[0][1],
        "Average Temperature": query_results[0][2]
    }
    
    return jsonify(range_date)
    
if __name__ == '__main__':
    app.run(debug=True)