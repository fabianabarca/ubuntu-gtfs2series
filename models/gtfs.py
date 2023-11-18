from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import Integer, Float, Date, Time, DateTime, String, Text
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement

Base = declarative_base()


# GTFS Schedule models


class Feed(Base):
    """Feed model.

    This is metadata to link other models to a specific feed.
    """

    __tablename__ = "feeds"
    feed_id = Column(String(63), primary_key=True)
    feed_tag = Column(String(63))


class Agency(Base):
    """GTFS Agency model v2.0 (agency.txt).

    Transit agencies with service represented in this dataset.

    Reference: https://gtfs.org/schedule/reference/#agencytxt
    """

    __tablename__ = "agencies"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="agencies")

    routes = relationship("Route", backref="agency")

    agency_id = Column(String(63), primary_key=True)
    agency_name = Column(String(255))
    agency_url = Column(String(255))
    agency_timezone = Column(String(255))
    agency_lang = Column(String(255))
    agency_phone = Column(String(255))
    agency_fare_url = Column(String(255))
    agency_email = Column(String(255))


class Stop(Base):
    """GTFS Stop model v2.0 (stops.txt).

    Individual locations where vehicles pick up or drop off passengers.

    Reference: https://gtfs.org/schedule/reference/#stopstxt
    """

    __tablename__ = "stops"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="stops")

    stop_id = Column(String(63), primary_key=True)
    stop_code = Column(String(127))
    stop_name = Column(String(255))
    stop_desc = Column(String(511))
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    stop_point = Column(Geometry(geometry_type="POINT", srid=4326))
    zone_id = Column(String(127))
    stop_url = Column(String(255))
    location_type = Column(Integer)
    parent_station = Column(String(127))
    stop_timezone = Column(String(127))
    wheelchair_boarding = Column(Integer)
    platform_code = Column(String(127))

    @classmethod
    def create_record(cls, stop_lat, stop_lon, **kwargs):
        point = WKTElement(f"POINT({stop_lon} {stop_lat})", srid=4326)
        fields = {"stop_point": point, **kwargs}
        return cls(**fields)


class Route(Base):
    """GTFS Route model v2.0 (routes.txt).

    Transit routes. A route is a group of trips that are displayed to riders as a single service.

    Reference: https://gtfs.org/schedule/reference/#routestxt
    """

    __tablename__ = "routes"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="routes")
    agency_id = Column(String(63), ForeignKey("agencies.agency_id"))
    agency = relationship("Agency", backref="routes")

    route_id = Column(String(63), primary_key=True)
    route_short_name = Column(String(63))
    route_long_name = Column(String(255))
    route_desc = Column(Text)
    route_type = Column(Integer)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    network_id = Column(String(63))


class Trip(Base):
    """GTFS Trip model v2.0 (trips.txt).

    Trips for each route. A trip is a sequence of two or more stops that occur during a specific time period.

    Reference: https://gtfs.org/schedule/reference/#tripstxt
    """

    __tablename__ = "trips"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="trips")
    route_id = Column(String(63), ForeignKey("routes.route_id"))
    route = relationship("Route", backref="trips")
    service_id = Column(String(63), ForeignKey("calendar.service_id"))
    service = relationship("Calendar", backref="trips")
    geoshape_id = Column(String(63), ForeignKey("geoshapes.geoshape_id"))
    geoshape = relationship("GeoShape", backref="trips")

    trip_id = Column(String(63), primary_key=True)
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(63))
    direction_id = Column(Integer)
    block_id = Column(String(127))
    shape_id = Column(String(127))
    wheelchair_accessible = Column(Integer)
    bikes_allowed = Column(Integer)


class StopTime(Base):
    """GTFS Stop Time model v2.0 (stop_times.txt).

    Times that a vehicle arrives at and departs from individual stops for each trip.

    Reference: https://gtfs.org/schedule/reference/#stop_timestxt
    """

    __tablename__ = "stop_times"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="stop_times")
    trip_id = Column(String(63), ForeignKey("trips.trip_id"), primary_key=True)
    trip = relationship("Trip", backref="stop_times")
    stop_id = Column(String(63), ForeignKey("stops.stop_id"))
    stop = relationship("Stop", backref="stop_times")

    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    shape_dist_traveled = Column(Float)
    timepoint = Column(Integer)


class Calendar(Base):
    """GTFS Calendar model v2.0 (calendar.txt).

    Service dates specified using a weekly schedule, with start and end dates.

    Reference: https://gtfs.org/schedule/reference/#calendartxt
    """

    __tablename__ = "calendar"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="calendar")

    service_id = Column(String(63), primary_key=True)
    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)


class GeoShape(Base):
    """GTFS Shape model v2.0 (an implementation of shapes.txt).

    A GeoAlchemy2 model for storing shapes as linestrings.
    """

    __tablename__ = "geoshapes"

    feed_id = Column(String(63), ForeignKey("feeds.feed_id", ondelete="CASCADE"), primary_key=True)
    feed = relationship("Feed", backref="geoshapes")

    geoshape_id = Column(String(63), primary_key=True)
    geoshape = Column(Geometry(geometry_type="LINESTRING", srid=4326))


# GTFS Realtime models


class FeedMessage(Base):
    """Header of a GTFS Realtime FeedMessage.

    This is metadata to link records of other models to a retrieved FeedMessage containing several entities, typically (necessarilly, in this implementation) of a single kind.

    This model has a composite primary key: the timestamp and the entityType. This is because a timestamp is "almost" unique (the moment at which the feed was created) but not quite (theoretically, two or three feeds of different entity types could be created at the same moment). The entityType is added to ensure uniqueness.
    """

    __tablename__ = "feed_messages"

    timestamp = Column(DateTime, primary_key=True)
    entityType = Column(String(63), primary_key=True)
    incrementality = Column(String(15))
    gtfsRealtimeVersion = Column(String(15))

    trip_updates = relationship("TripUpdate", backref="feedMessage")
    vehicle_positions = relationship("VehiclePosition", backref="feedMessage")
    alerts = relationship("Alert", backref="feedMessage")


class TripUpdate(Base):
    """GTFS Realtime TripUpdate entity v2.0 (normalized).

    Trip updates represent fluctuations in the timetable.

    This model has a composite primary key: the FeedMessage key (itself a composite key of the timestamp and the entityType) and the entityId. This is because the entityId is feed-unique (according to the GTFS reference), and thus the primary key of the TripUpdate entity is the combination of the FeedMessage key and the entityId.
    """

    __tablename__ = "trip_updates"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)

    stop_time_updates = relationship("StopTimeUpdate", backref="tripUpdate")

    # TripDescriptor (message)
    tripUpdate_trip_tripId = Column(String(255))
    tripUpdate_trip_routeId = Column(String(255))
    tripUpdate_trip_directionId = Column(Integer)
    tripUpdate_trip_startTime = Column(Time)
    tripUpdate_trip_startDate = Column(Date)
    tripUpdate_trip_scheduleRelationship = Column(String(31))  # (enum)
    # VehicleDescriptor (message)
    tripUpdate_vehicle_id = Column(String(255))
    tripUpdate_vehicle_label = Column(String(255))
    tripUpdate_vehicle_licensePlate = Column(String(255))
    tripUpdate_vehicle_wheelchairAccessible = Column(String(31))  # (enum)
    # Timestamp (uint64)
    tripUpdate_timestamp = Column(DateTime)
    # Delay (int32)
    tripUpdate_delay = Column(Integer)
    # TripProperties (experimental message) is omitted

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType],
            ["feed_messages.timestamp", "feed_messages.entityType"],
        ),
    )


class StopTimeUpdate(Base):
    """GTFS Realtime TripUpdate message v2.0 (normalized).

    Realtime update for arrival and/or departure events for a given stop on a trip, linked to a TripUpdate entity in a FeedMessage.
    """

    __tablename__ = "stop_time_updates"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)
    stopSequence = Column(Integer, primary_key=True)

    # Stop sequence (uint32) (composite primary key)
    # Stop ID (string)
    stopId = Column(String(127))
    # StopTimeEvent (message): arrival
    arrival_delay = Column(Integer)
    arrival_time = Column(DateTime)
    arrival_uncertainty = Column(Integer)
    # StopTimeEvent (message): departure
    departure_delay = Column(Integer)
    departure_time = Column(DateTime)
    departure_uncertainty = Column(Integer)
    # OccupancyStatus (enum)
    departureOccupancyStatus = Column(String(255))
    # ScheduleRelationship (enum)
    scheduleRelationship = Column(String(255))
    # Omitted: StopTimeProperties (message)

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType, entityId],
            [
                "trip_updates.feedMessage_timestamp",
                "trip_updates.feedMessage_entityType",
                "trip_updates.entityId",
            ],
        ),
    )


class VehiclePosition(Base):
    """GTFS Realtime VehiclePosition entity v2.0 (normalized).

    Vehicle position represents a few basic pieces of information about a particular vehicle on the network.

    This model has a composite primary key: the FeedMessage key (itself a composite key of the timestamp and the entityType) and the entityId. This is because the entityId is feed-unique (according to the GTFS reference), and thus the primary key of the VehiclePosition entity is the combination of the FeedMessage key and the entityId.
    """

    __tablename__ = "vehicle_positions"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)

    # TripDescriptor (message)
    vehicle_trip_tripId = Column(String(255))
    vehicle_trip_routeId = Column(String(255))
    vehicle_trip_directionId = Column(Integer)
    vehicle_trip_startTime = Column(Time)
    vehicle_trip_startDate = Column(Date)
    vehicle_trip_scheduleRelationship = Column(String(31))  # (enum)
    # VehicleDescriptor (message)
    vehicle_vehicle_id = Column(String(255))
    vehicle_vehicle_label = Column(String(255))
    vehicle_vehicle_licensePlate = Column(String(255))
    vehicle_vehicle_wheelchairAccessible = Column(String(31))  # (enum)
    # Position (message)
    vehicle_position_latitude = Column(Float)
    vehicle_position_longitude = Column(Float)
    vehicle_position_point = Column(Geometry(geometry_type="POINT", srid=4326))
    vehicle_position_bearing = Column(Float)
    vehicle_position_odometer = Column(Float)
    vehicle_position_speed = Column(Float)  # (meters/second)
    # Current stop sequence (uint32)
    vehicle_currentStopSequence = Column(Integer)
    # Stop ID (string)
    vehicle_stopId = Column(String(255))
    # VehicleStopStatus (enum)
    vehicle_currentStatus = Column(String)
    # Timestamp (uint64)
    vehicle_timestamp = Column(DateTime)
    # CongestionLevel (enum)
    vehicle_congestionLevel = Column(String)
    # OccupancyStatus (enum)
    vehicle_occupancyStatus = Column(String)
    # OccupancyPercentage (uint32)
    vehicle_occupancyPercentage = Column(Integer)
    # CarriageDetails (message)
    vehicle_multiCarriageDetails = Column(String)

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType],
            ["feed_messages.timestamp", "feed_messages.entityType"],
        ),
    )

    @classmethod
    def create_record(
        cls, vehicle_position_latitude, vehicle_position_longitude, **kwargs
    ):
        point = WKTElement(
            f"POINT({vehicle_position_longitude} {vehicle_position_latitude})",
            srid=4326,
        )
        fields = {
            "vehicle_position_point": point,
            **kwargs,
        }
        return cls(fields)


class Alert(Base):
    """GTFS Realtime Alert entity v2.0 (normalized).

    Service alerts represent higher level problems with a particular entity and are generally in the form of a textual description of the disruption.

    active_period and informed_entity have their own models.

    TranslatedStrings fields (cause_detail, effect_detail, url, header_text, description_text) are stored in the Translation model.

    tts_header_text, tts_description_text, image and image_alternative_text are omitted.

    This model has a composite primary key: the FeedMessage key (itself a composite key of the timestamp and the entityType) and the entityId. This is because the entityId is feed-unique (according to the GTFS reference), and thus the primary key of the Alert entity is the combination of the FeedMessage key and the entityId.
    """

    __tablename__ = "alerts"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)

    active_periods = relationship("ActivePeriod", backref="alert")
    informed_entities = relationship("InformedEntity", backref="alert")
    translations = relationship("Translation", backref="alert")

    # Cause (enum)
    alert_cause = Column(String(255))
    # Effect (enum)
    alert_effect = Column(String(255))
    # SeverityLevel (enum)
    alert_severityLevel = Column(String(255))

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType],
            ["feed_messages.timestamp", "feed_messages.entityType"],
        ),
    )


class ActivePeriod(Base):
    """
    Time when the alert should be shown to the user.
    """

    __tablename__ = "active_periods"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)
    activePeriodId = Column(Integer, primary_key=True)

    start = Column(DateTime)
    end = Column(DateTime)

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType, entityId],
            [
                "alerts.feedMessage_timestamp",
                "alerts.feedMessage_entityType",
                "alerts.entityId",
            ],
        ),
    )


class InformedEntity(Base):
    """GTFS Realtime InformedEntity message v2.0 (normalized).

    Entities whose users we should notify of this alert. At least one informed_entity must be provided.
    """

    __tablename__ = "informed_entities"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)
    informedentityId = Column(Integer, primary_key=True)

    agencyId = Column(String(63))
    routeId = Column(String(63))
    routeType = Column(Integer)
    directionId = Column(Integer)
    trip = Column(String(127))
    stopId = Column(String(63))

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType, entityId],
            [
                "alerts.feedMessage_timestamp",
                "alerts.feedMessage_entityType",
                "alerts.entityId",
            ],
        ),
    )


class Translation(Base):
    """GTFS Realtime Translation message v2.0 (normalized).

    An internationalized message containing per-language versions of a snippet of text or a URL.

    Translations fields are stored in the Translation model and are identified by the alert_translatedString field with possible values "cause_detail", "effect_detail", "url", "header_text", "description_text".
    """

    __tablename__ = "translations"

    feedMessage_timestamp = Column(DateTime, primary_key=True)
    feedMessage_entityType = Column(String(63), primary_key=True)
    entityId = Column(String(127), primary_key=True)
    alert_translatedString = Column(String(127), primary_key=True)
    translationId = Column(Integer, primary_key=True)

    # Translation (message)
    translation_text = Column(Text)
    translation_language = Column(String(31))

    __table_args__ = (
        ForeignKeyConstraint(
            [feedMessage_timestamp, feedMessage_entityType, entityId],
            [
                "alerts.feedMessage_timestamp",
                "alerts.feedMessage_entityType",
                "alerts.entityId",
            ],
        ),
    )
