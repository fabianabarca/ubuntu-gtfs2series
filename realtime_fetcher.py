import configparser
import datetime
import time
import logging
from schedule import every, repeat, run_pending
from sqlalchemy import create_engine
import requests
import pandas as pd
from google.transit import gtfs_realtime_pb2 as gtfs_rt
from google.protobuf import json_format

logging.basicConfig(
    filename="realtime.log",
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
vehicle_positions = gtfs_rt.FeedMessage()
vehicle_positions_url = config.get("gtfs", "vehicle_positions_url")

logging.info(
    f"New GTFS Realtime FeedMessage collection session\n{datetime.datetime.now()}\nFetching data from {vehicle_positions_url}"
)

# Scheduler information
realtime_fetch_interval = config.getint("scheduler", "realtime_fetch_interval")
last_timestamp = {"value": None}


# Schedule task
@repeat(every(realtime_fetch_interval).seconds)
def fetch():
    logging.info(f"Fetching begins at {datetime.datetime.now()}")
    global last_timestamp

    # VehiclePostion entity
    vehicle_positions_response = requests.get(vehicle_positions_url)
    vehicle_positions.ParseFromString(vehicle_positions_response.content)
    timestamp = vehicle_positions.header.timestamp
    # TODO: Get the foreign key of the current GTFS Schedule feed
    if not last_timestamp["value"] == timestamp:
        vehicle_positions_df = pd.json_normalize(
            json_format.MessageToDict(vehicle_positions)["entity"], sep="_"
        )
        vehicle_positions_df.rename(columns={"id": "entity_id"}, inplace=True)
        vehicle_positions_df["feedMessage_timestamp"] = timestamp
        vehicle_positions_df["vehicle_position_point"] = vehicle_positions_df.apply(
            lambda row: f"POINT({row.vehicle_position_longitude} {row.vehicle_position_latitude})",
            axis=1,
        )
        try:
            del vehicle_positions_df["vehicle_multiCarriageDetails"]
        except:
            pass
        try:
            vehicle_positions_df.to_sql(
                "vehicle_positions", engine, if_exists="append", index=False
            )
            logging.info(f"Record {timestamp} made at {str(datetime.datetime.now())}")
        except:
            logging.error(
                f"Error at recording at {str(datetime.datetime.now())}"
            )
    else:
        logging.error(
            f"Duplicated FeedMessage with timestamp {timestamp} at {str(datetime.datetime.now())}"
        )

    last_timestamp["value"] = timestamp


while True:
    run_pending()
    time.sleep(1)
