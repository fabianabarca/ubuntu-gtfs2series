"""
Get a single GTFS Realtime FeedMessage from a URL and save a JSON file.
"""

import requests
from google.transit import gtfs_realtime_pb2 as gtfs_rt
from google.protobuf import json_format

realtime_feed_url = "https://cdn.mbta.com/realtime/TripUpdates.pb"

# Create a FeedMessage object from the GTFS Realtime FeedMessage
feed_message = gtfs_rt.FeedMessage()

# Get the Protobuf FeedMessage from the URL
response = requests.get(realtime_feed_url)

# Parse the FeedMessage from the content of the response
feed_message.ParseFromString(response.content)

# Convert the FeedMessage to a dictionary
feed_message_dict = json_format.MessageToDict(feed_message)

# Get the timestamp from the FeedMessage
timestamp = feed_message_dict["header"]["timestamp"]

# Save the FeedMessage as a JSON file
with open(f"feed_message_{timestamp}.json", "w") as f:
    f.write(json_format.MessageToJson(feed_message))
