import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('sensor_data.db')

# Query all records in the accelerometer_data table
df = pd.read_sql_query("SELECT * FROM accelerometer_data", conn)

# Print the DataFrame in a table format
print(df)
