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
import math

logging.basicConfig(
    filename="test_realtime.log",
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
trip_updates = gtfs_rt.FeedMessage()
trip_updates_url = config.get("gtfs", "trip_updates_url")

logging.info(
    f"(TEST) New GTFS Realtime FeedMessage collection session\n{datetime.datetime.now()}\nFetching data from {trip_updates_url}"
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
    trip_updates_response = requests.get(trip_updates_url)
    trip_updates.ParseFromString(trip_updates_response.content)
    timestamp = trip_updates.header.timestamp
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    incrementality = trip_updates.header.incrementality
    gtfsRealtimeVersion = trip_updates.header.gtfs_realtime_version
    entityType = "tripUpdate"

    if not last_timestamp["value"] == timestamp:
        # Save FeedMessage
        feed_message_df = pd.DataFrame(
            {
                "timestamp": [timestamp],
                "entityType": [entityType],
                "incrementality": [incrementality],
                "gtfsRealtimeVersion": [gtfsRealtimeVersion],
            }
        )
        feed_message_df.to_sql("feed_messages", engine, if_exists="append", index=False)

        # Build FeedEntity
        trip_updates_df = pd.json_normalize(
            json_format.MessageToDict(trip_updates)["entity"], sep="_"
        )
        trip_updates_df["feedMessage_timestamp"] = timestamp
        trip_updates_df["feedMessage_entityType"] = entityType
        trip_updates_df.rename(columns={"id": "entityId"}, inplace=True)
        trip_updates_df["tripUpdate_timestamp"] = trip_updates_df.apply(
            lambda row: datetime.datetime.fromtimestamp(int(row.tripUpdate_timestamp)) if pd.notnull(row.tripUpdate_timestamp) else None,
            axis=1,
        )
        # Get StopTimeUpdate
        stop_time_builder = trip_updates_df[["feedMessage_timestamp", "feedMessage_entityType", "entityId", "tripUpdate_stopTimeUpdate"]].copy()
        trip_updates_df.pop("tripUpdate_stopTimeUpdate")
        
        # Save StopTimeUpdate
        for index, row in stop_time_builder.iterrows():
            try:
                stop_time_updates_df = pd.json_normalize(
                    row["tripUpdate_stopTimeUpdate"], sep="_"
                )
            except:
                continue
            stop_time_updates_df["feedMessage_timestamp"] = row["feedMessage_timestamp"]
            stop_time_updates_df["feedMessage_entityType"] = row["feedMessage_entityType"]
            stop_time_updates_df["entityId"] = row["entityId"]
            if "arrival_time" in stop_time_updates_df.columns:
                stop_time_updates_df["arrival_time"] = stop_time_updates_df.apply(
                    lambda row: datetime.datetime.fromtimestamp(int(row.arrival_time)) if pd.notnull(row.arrival_time) else None,
                    axis=1,
                )
            if "departure_time" in stop_time_updates_df.columns:
                stop_time_updates_df["departure_time"] = stop_time_updates_df.apply(
                    lambda row: datetime.datetime.fromtimestamp(int(row.departure_time)) if pd.notnull(row.departure_time) else None,
                    axis=1,
                )
            
            # Save StopTimeUpdate
            stop_time_updates_df.to_sql("stop_time_updates", engine, if_exists="append", index=False)
        print("All stop time updates have been saved!")

        # Save TripUpdate
        trip_updates_df.to_sql("trip_updates", engine, if_exists="append", index=False)
        print("All trip updates have been saved!")
        logging.info(f"Record {timestamp} made at {str(datetime.datetime.now())}")
    else:
        logging.error(
            f"Duplicated FeedMessage with timestamp {timestamp} at {str(datetime.datetime.now())}"
        )

    last_timestamp["value"] = timestamp


while True:
    run_pending()
    time.sleep(1)
