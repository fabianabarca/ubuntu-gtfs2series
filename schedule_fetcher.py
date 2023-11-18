import io
import configparser
import datetime
import time
import zipfile
import logging
from schedule import every, repeat, run_pending
from sqlalchemy import create_engine
import requests
import pandas as pd

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

# GTFS configuration
schedule_url = config.get("gtfs", "schedule_url")
files = [
    "agency",
    "calendar",
    "calendar_dates",
    "routes",
    "shapes",
    "stop_times",
    "stops",
    "trips",
    "shapes",
    "frequencies",
    "feed_info",
]

logging.info(
    f"New GTFS Schedule updating session\n{datetime.datetime.now()}\nData source: {schedule_url}"
)

# Scheduler information
schedule_fetch_interval = config.getint("scheduler", "schedule_fetch_interval")
last_feed_tag = {"value": None}


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
        tables = {}
        schedule_response = requests.get(schedule_url)
        schedule_zip = zipfile.ZipFile(io.BytesIO(schedule_response.content))
        for file in schedule_zip.namelist():
            if file[:-4] in files:
                tables[file[:-4]] = pd.read_csv(
                    schedule_zip.open(file), dtype=str, keep_default_na=False
                )
                logging.info(f"Table {file[:-4]} loaded")
    else:
        logging.info(f"GTFS Schedule feed unchanged: {feed_tag}")


# Run scheduler
while True:
    run_pending()
    time.sleep(1)
