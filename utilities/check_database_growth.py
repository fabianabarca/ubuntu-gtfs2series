import configparser
import psycopg2

# Read configuration file
config = configparser.ConfigParser()
config.read("./gtfs2series.cfg")

# Define connection parameters
params = {
    "dbname": config.get("database", "name"),
    "user": config.get("database", "user"),
    "password": config.get("database", "password"),
    "host": config.get("database", "host"),
    "port": config.getint("database", "port"),
}

# Establish a connection to the database
conn = psycopg2.connect(**params)

# Create a new cursor object
cur = conn.cursor()

# Execute the SQL query to get the size of the database
cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")

# Fetch the result of the query
size = cur.fetchone()[0]

# Close the cursor and the connection
cur.close()
conn.close()

print(f"The size of the database is: {size}")
