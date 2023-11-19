import io
import configparser
import datetime
import time
import zipfile
import logging
from schedule import every, repeat, run_pending
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
import requests
import pandas as pd
from models.schedule import *

# Logging configuration
logging.basicConfig(
    filename="schedule.log",
    format="%(levelname)s: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)

# Configuration file
config = configparser.ConfigParser()
config.read("./gtfs2series.cfg")

# Database information
system = config.get("database", "system")
host = config.get("database", "host")
port = config.getint("database", "port")
name = config.get("database", "name")
user = config.get("database", "user")
password = config.get("database", "password")

# Create database engine
engine = create_engine(f"{system}://{user}:{password}@{host}:{port}/{name}")

# GTFS information
feed_transit_system = config.get("gtfs", "transit_system")
schedule_url = config.get("gtfs", "schedule_url")
tables = {
    "agency": "Agency",
    "stops": "Stop",
    "shapes": "Shape",
    "calendar": "Calendar",
    "calendar_dates": "CalendarDate",
    "routes": "Route",
    "trips": "Trip",
    "stop_times": "StopTime",
    "frequencies": "Frequency",
    "feed_info": "FeedInfo",
}  # They must be loaded in this order

logging.info(
    f"New GTFS Schedule updating session\n{feed_transit_system}\n{datetime.datetime.now()}\nData source: {schedule_url}"
)

# Scheduler information
schedule_fetch_interval = config.getint("scheduler", "schedule_fetch_interval")
last_feed_tag = {"value": None}
try:
    # Get last feed_tag from database
    last_feed_tag["value"] = pd.read_sql(
        "SELECT feed_tag FROM feeds WHERE feed_transit_system = {feed_transit_system} ORDER BY feed_last_modified DESC LIMIT 1",
        engine,
    ).loc[0, "feed_tag"]
except:
    logging.info("No feed_tag found in the table 'feeds'")
    logging.info("A new feed will be imported")


# Schedule task
@repeat(every(schedule_fetch_interval).seconds)
def fetch():
    logging.info(f"Checking at {datetime.datetime.now()}")
    global last_feed_tag

    # GTFS Schedule
    schedule_check = requests.head(schedule_url)
    feed_tag = schedule_check.headers["ETag"]
    if not feed_tag == last_feed_tag["value"]:
        logging.info(f"New GTFS Schedule feed detected: {feed_tag}")
        last_feed_tag["value"] = feed_tag

        # Save new feed
        feed_last_modified = datetime.datetime.strptime(
            schedule_check.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
        )
        feed_id = feed_last_modified.strftime("%Y-%m-%dT%H:%M:%S")
        feed = pd.DataFrame(
            {
                "feed_id": [feed_id],
                "feed_tag": [feed_tag],
                "feed_last_modified": [feed_last_modified],
                "feed_transit_system": [feed_transit_system],
            }
        )
        feed.to_sql("feeds", engine, if_exists="append", index=False)

        # Get feed
        schedule_response = requests.get(schedule_url)
        schedule_zip = zipfile.ZipFile(io.BytesIO(schedule_response.content))
        for table_name in tables.keys():
            file = f"{table_name}.txt"
            if file in schedule_zip.namelist():
                table = pd.read_csv(
                    schedule_zip.open(file),
                    dtype=str,
                    keep_default_na=False,
                    na_values="",
                )
                table["feed_id"] = feed_id
                columns = eval(f"{tables[table_name]}.__table__.columns.keys()")
                table = table[[column for column in columns if column in table.columns]]
                table.to_sql(table_name, engine, if_exists="append", index=False)
                logging.info(f"Table {table_name} loaded")
                if table_name == "shapes":
                    shape_ids = table["shape_id"].unique()
                    session = Session(bind=engine)
                    for shape_id in shape_ids:
                        shape = table[table["shape_id"] == shape_id]
                        wkt = "LINESTRING("
                        for _, row in shape.iterrows():
                            wkt += f"{row['shape_pt_lon']} {row['shape_pt_lat']},"
                        wkt = wkt[:-1] + ")"
                        geoshape = GeoShape(
                            feed_id=feed_id,
                            geoshape_id=shape_id,
                            geoshape=WKTElement(wkt, srid=4326),
                        )
                        session.add(geoshape)
                    session.commit()
                    logging.info(f"Table geoshapes loaded")
    else:
        logging.info(
            f"GTFS Schedule feed is unchanged and has not been imported: {feed_tag}"
        )


# Run scheduler
while True:
    run_pending()
    time.sleep(1)
