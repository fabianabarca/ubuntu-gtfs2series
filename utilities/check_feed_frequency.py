"""
Get GTFS Realtime FeedMessages until the timestamp changes.

Save a couple of measurements of the time between FeedMessages
with different timestamps.
"""

from datetime import datetime
import requests
from google.transit import gtfs_realtime_pb2 as gtfs_rt
from google.protobuf import json_format

realtime_feed_url = "https://cdn.mbta.com/realtime/VehiclePositions.pb"

# Create a FeedMessage object from the GTFS Realtime FeedMessage
feed_message = gtfs_rt.FeedMessage()

# Configure the loop
N = 10
time_deltas = []
last_timestamp = datetime.now()
checks = 0

while len(time_deltas) <= N:
    response = requests.get(realtime_feed_url)
    checks += 1
    feed_message.ParseFromString(response.content)
    feed_message_dict = json_format.MessageToDict(feed_message)
    timestamp = datetime.fromtimestamp(int(feed_message_dict["header"]["timestamp"]))
    if not last_timestamp == timestamp:
        time_deltas.append(timestamp - last_timestamp)
        last_timestamp = timestamp
    else:
        continue

time_deltas.pop(0)

print(
    "Time difference (seconds) between each change of timestamp in GTFS Realtime FeedMessage\n"
)
print(f"Data from {realtime_feed_url}")
print(f"Number of requests: {checks}")
print(f"Number of sampled changes: {N}\n")

sum_time_deltas = 0
for time_delta in time_deltas:
    sum_time_deltas += time_delta.total_seconds()
    print(time_delta.total_seconds())

# Average time difference
average_time_delta = sum_time_deltas / len(time_deltas)
print(f"\nAverage time difference: {average_time_delta} seconds")
