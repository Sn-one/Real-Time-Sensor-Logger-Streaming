from flask import Flask, request, jsonify
import json
import pandas as pd
import sqlite3
from datetime import datetime
from threading import local
from producer import kafka_producer


app = Flask(__name__)
threadlocal = local()

def get_db():
    db = getattr(threadlocal, 'db', None)
    if db is None:
        db = threadlocal.db = sqlite3.connect('sensor_data.db')
    return db

def create_tables():
    conn = get_db()
    c = conn.cursor()

    # Create tables with the defined schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS accelerometer_data (
            messageId INTEGER,
            sessionId TEXT,
            deviceId TEXT,
            sensorName TEXT,
            time INTEGER,
            accuracy INTEGER,
            x REAL,
            y REAL,
            z REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS orientation_data (
            messageId INTEGER,
            sessionId TEXT,
            deviceId TEXT,
            sensorName TEXT,
            time INTEGER,
            accuracy INTEGER,
            qx REAL,
            qy REAL,
            qz REAL,
            qw REAL,
            roll REAL,
            pitch REAL,
            yaw REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS magnetometer_data (
            messageId INTEGER,
            sessionId TEXT,
            deviceId TEXT,
            sensorName TEXT,
            time INTEGER,
            accuracy INTEGER,
            x REAL,
            y REAL,
            z REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS gyroscope_data (
            messageId INTEGER,
            sessionId TEXT,
            deviceId TEXT,
            sensorName TEXT,
            time INTEGER,
            accuracy INTEGER,
            x REAL,
            y REAL,
            z REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS gravity_data (
            messageId INTEGER,
            sessionId TEXT,
            deviceId TEXT,
            sensorName TEXT,
            time INTEGER,
            accuracy INTEGER,
            x REAL,
            y REAL,
            z REAL
        )
    ''')

    conn.commit()

@app.route('/sensor_data', methods=['POST'])
def receive_data():
    data = request.get_json()  # Get JSON data from the request

    # Save data as JSON
    with open('data.json', 'w') as f:
        json.dump(data, f)

    # Convert JSON data to DataFrame
    df = pd.DataFrame(data)

    # Save DataFrame as CSV
    df.to_csv('data.csv', index=False)

    # Get the current time
    now = datetime.now()

    # Format the time as a string
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Get the database connection
    conn = get_db()
    c = conn.cursor()

    # For each sensor in the payload
    for sensor in data['payload']:
        # Get the sensor name
        sensor_name = sensor['name']

        # Depending on the sensor name, decide which table to insert the data into
        if sensor_name in ['accelerometer', 'totalacceleration']:
            table_name = 'accelerometer_data'
        elif sensor_name == 'orientation':
            table_name = 'orientation_data'
        elif sensor_name == 'magnetometer':
            table_name = 'magnetometer_data'
        elif sensor_name == 'gyroscope':
            table_name = 'gyroscope_data'
        elif sensor_name == 'gravity':
            table_name = 'gravity_data'
        else:
            table_name = 'other_data'

        # Insert the sensor data into the table
        if sensor_name == 'orientation':
            c.execute(f'INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (data['messageId'], data['sessionId'], data['deviceId'], sensor_name, sensor['time'], sensor['accuracy'], sensor['values']['qx'], sensor['values']['qy'], sensor['values']['qz'], sensor['values']['qw'], sensor['values']['roll'], sensor['values']['pitch'], sensor['values']['yaw']))
        else:
            c.execute(f'INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (data['messageId'], data['sessionId'], data['deviceId'], sensor_name, sensor['time'], sensor['accuracy'], sensor['values']['x'], sensor['values']['y'], sensor['values']['z']))

        # Commit the changes
        conn.commit()

        # Send the sensor data to Kafka
        kafka_producer(sensor)

    # Return a message and the current time
    return jsonify({'message': 'Data received successfully', 'time': time_string}), 200


if __name__ == '__main__':
        # Run the dashboard in a separate thread
   
    create_tables()  # Create the tables when the server starts
    app.run(host='0.0.0.0', port=5000)  # Run the server
