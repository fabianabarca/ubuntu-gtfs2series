from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer, Float, Date, Time, DateTime, Interval, String, Text
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement

Base = declarative_base()


class Feed(Base):
    """Feed model.

    This is metadata to link other models to a specific feed.
    """

    __tablename__ = "feeds"
    feed_id = Column(String(127), primary_key=True)
    feed_tag = Column(String(127))
    feed_last_modified = Column(DateTime)
    feed_transit_system = Column(String(127))

    agency = relationship("Agency", backref="feed")
    stops = relationship("Stop", backref="feed")
    routes = relationship("Route", backref="feed")
    trips = relationship("Trip", backref="feed")
    stop_times = relationship("StopTime", backref="feed")
    calendar = relationship("Calendar", backref="feed")
    shapes = relationship("Shape", backref="feed")
    geoshapes = relationship("GeoShape", backref="feed")
    frequencies = relationship("Frequency", backref="feed")
    feed_info = relationship("FeedInfo", backref="feed")
    calendar_dates = relationship("CalendarDate", backref="feed")


class Agency(Base):
    """GTFS Agency model v2.0 (agency.txt).

    Transit agencies with service represented in this dataset.

    Reference: https://gtfs.org/schedule/reference/#agencytxt
    """

    __tablename__ = "agency"

    feed_id = Column(String(127), primary_key=True)
    agency_id = Column(String(127), primary_key=True)

    routes = relationship("Route", backref="agency")

    agency_name = Column(String(255))
    agency_url = Column(String(255))
    agency_timezone = Column(String(255))
    agency_lang = Column(String(255))
    agency_phone = Column(String(255))
    agency_fare_url = Column(String(255))
    agency_email = Column(String(255))

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )


class Stop(Base):
    """GTFS Stop model v2.0 (stops.txt).

    Individual locations where vehicles pick up or drop off passengers.

    Reference: https://gtfs.org/schedule/reference/#stopstxt
    """

    __tablename__ = "stops"

    feed_id = Column(String(127), primary_key=True)
    stop_id = Column(String(127), primary_key=True)

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

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )

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

    feed_id = Column(String(127), primary_key=True)
    route_id = Column(String(127), primary_key=True)

    trips = relationship("Trip", backref="route")

    agency_id = Column(String(127))
    route_short_name = Column(String(127))
    route_long_name = Column(String(255))
    route_desc = Column(Text)
    route_type = Column(Integer)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    network_id = Column(String(127))

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "agency_id"],
            ["agency.feed_id", "agency.agency_id"],
        ),
    )


class Trip(Base):
    """GTFS Trip model v2.0 (trips.txt).

    Trips for each route. A trip is a sequence of two or more stops that occur during a specific time period.

    Reference: https://gtfs.org/schedule/reference/#tripstxt
    """

    __tablename__ = "trips"

    feed_id = Column(String(127), primary_key=True)
    trip_id = Column(String(127), primary_key=True)

    route_id = Column(String(127))  # Foreign key
    service_id = Column(String(127))  # Foreign key
    geoshape_id = Column(String(127))  # Foreign key
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(127))
    direction_id = Column(Integer)
    block_id = Column(String(127))
    shape_id = Column(String(127))  # Foreign key (not yet implemented)
    wheelchair_accessible = Column(Integer)
    bikes_allowed = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "route_id"],
            ["routes.feed_id", "routes.route_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "service_id"],
            ["calendar.feed_id", "calendar.service_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "geoshape_id"],
            ["geoshapes.feed_id", "geoshapes.geoshape_id"],
        ),
    )


class StopTime(Base):
    """GTFS Stop Time model v2.0 (stop_times.txt).

    Times that a vehicle arrives at and departs from individual stops for each trip.

    Reference: https://gtfs.org/schedule/reference/#stop_timestxt
    """

    __tablename__ = "stop_times"

    feed_id = Column(String(127), primary_key=True)
    trip_id = Column(String(127), primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)

    stop_id = Column(String(127))
    arrival_time = Column(Interval)
    departure_time = Column(Interval)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    shape_dist_traveled = Column(Float)
    timepoint = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "trip_id"],
            ["trips.feed_id", "trips.trip_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "stop_id"],
            ["stops.feed_id", "stops.stop_id"],
        ),
    )


class Calendar(Base):
    """GTFS Calendar model v2.0 (calendar.txt).

    Service dates specified using a weekly schedule, with start and end dates.

    Reference: https://gtfs.org/schedule/reference/#calendartxt
    """

    __tablename__ = "calendar"

    feed_id = Column(String(127), primary_key=True)
    service_id = Column(String(127), primary_key=True)

    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )


class CalendarDate(Base):
    """GTFS Calendar Date model v2.0 (calendar_dates.txt).

    The calendar_dates.txt table explicitly activates or disables service by date. Exceptions for the services defined in the calendar.txt file. If calendar_dates.txt includes all dates of service, this file may be specified instead of calendar.txt.

    Reference: https://gtfs.org/schedule/reference/#calendar_datestxt
    """

    __tablename__ = "calendar_dates"

    feed_id = Column(String(127), primary_key=True)
    service_id = Column(String(127), primary_key=True)
    date = Column(Date, primary_key=True)

    exception_type = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "service_id"],
            ["calendar.feed_id", "calendar.service_id"],
        ),
    )


class Shape(Base):
    """GTFS Shape model v2.0 (shapes.txt).

    Rules for drawing lines on a map to represent a transit organization's routes.

    Reference: https://gtfs.org/schedule/reference/#shapestxt
    """

    __tablename__ = "shapes"

    feed_id = Column(String(127), primary_key=True)
    shape_id = Column(String(127), primary_key=True)
    shape_pt_sequence = Column(Integer, primary_key=True)

    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_dist_traveled = Column(Float)

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )


class GeoShape(Base):
    """GTFS Shape model v2.0 (an implementation of shapes.txt).

    A GeoAlchemy2 model for storing shapes as linestrings.
    """

    __tablename__ = "geoshapes"

    feed_id = Column(String(127), primary_key=True)
    geoshape_id = Column(String(127), primary_key=True)

    geoshape = Column(Geometry(geometry_type="LINESTRING", srid=4326))

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )


class Frequency(Base):
    """GTFS Frequency model v2.0 (frequency.txt).

    Headway (time between trips) for routes with variable frequency of service.

    Reference: https://gtfs.org/schedule/reference/#frequencytxt
    """

    __tablename__ = "frequencies"

    feed_id = Column(String(127), primary_key=True)
    trip_id = Column(String(127), primary_key=True)
    start_time = Column(Time, primary_key=True)

    end_time = Column(Time)
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
        ForeignKeyConstraint(
            ["feed_id", "trip_id"],
            ["trips.feed_id", "trips.trip_id"],
        ),
    )


class FeedInfo(Base):
    """GTFS Feed Info model v2.0 (feed_info.txt).

    The file contains information about the dataset itself, rather than the services that the dataset describes. In some cases, the publisher of the dataset is a different entity than any of the agencies.

    Reference: https://gtfs.org/schedule/reference/#feed_infotxt
    """

    __tablename__ = "feed_info"

    feed_id = Column(String(127), primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=True)

    feed_publisher_name = Column(String(255))
    feed_publisher_url = Column(String(255))
    feed_lang = Column(String(31))
    default_lang = Column(String(31))
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(127))
    feed_contact_email = Column(String(255))
    feed_contact_url = Column(String(255))

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )
