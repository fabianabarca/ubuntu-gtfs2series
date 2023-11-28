from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import (
    Integer,
    Float,
    Date,
    Time,
    DateTime,
    Interval,
    String,
    Text,
)
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement

Base = declarative_base()


class Feed(Base):
    """Feed model.

    This is metadata to link other models to a specific feed.
    """

    __tablename__ = "feeds"

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)

    # Columns

    feed_tag = Column(String(255))
    feed_last_modified = Column(DateTime)
    feed_transit_system = Column(String(255))

    # Relationships and foreign keys

    agency = relationship("Agency", viewonly=True)
    stops = relationship("Stop", viewonly=True)
    routes = relationship("Route", viewonly=True)
    trips = relationship("Trip", viewonly=True)
    stop_times = relationship("StopTime", viewonly=True)
    calendar = relationship("Calendar", viewonly=True)
    shapes = relationship("Shape", viewonly=True)
    geoshapes = relationship("GeoShape", viewonly=True)
    frequencies = relationship("Frequency", viewonly=True)
    feed_info = relationship("FeedInfo", viewonly=True)
    calendar_dates = relationship("CalendarDate", viewonly=True)


class Agency(Base):
    """GTFS Agency model v2.0 (agency.txt).

    Transit agencies with service represented in this dataset.

    Reference: https://gtfs.org/schedule/reference/#agencytxt
    """

    __tablename__ = "agency"

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    agency_id = Column(String(255), primary_key=True)

    # Columns

    agency_name = Column(String(255))
    agency_url = Column(String(255))
    agency_timezone = Column(String(255))
    agency_lang = Column(String(255))
    agency_phone = Column(String(255))
    agency_fare_url = Column(String(255))
    agency_email = Column(String(255))

    # Relationships and foreign keys

    routes = relationship("Route", back_populates="agency")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    stop_id = Column(String(255), primary_key=True)

    # Columns

    stop_code = Column(String(255))
    stop_name = Column(String(255))
    stop_desc = Column(String(511))
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    stop_point = Column(Geometry(geometry_type="POINT", srid=4326))
    zone_id = Column(String(255))
    stop_url = Column(String(255))
    location_type = Column(Integer)
    parent_station = Column(String(255))
    stop_timezone = Column(String(255))
    wheelchair_boarding = Column(Integer)
    platform_code = Column(String(255))

    # Relationships and foreign keys

    stop_times = relationship("StopTime", back_populates="stop")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    route_id = Column(String(255), primary_key=True)

    # Columns

    agency_id = Column(String(255))
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_desc = Column(Text)
    route_type = Column(Integer)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    network_id = Column(String(255))

    # Relationships and foreign keys

    agency = relationship("Agency", back_populates="routes")
    trips = relationship("Trip", back_populates="route")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    trip_id = Column(String(255), primary_key=True)

    # Columns

    route_id = Column(String(255))  # Foreign key
    service_id = Column(String(255))  # Foreign key
    geoshape_id = Column(String(255))  # Foreign key
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    direction_id = Column(Integer)
    block_id = Column(String(255))
    shape_id = Column(String(255))  # Foreign key (not yet implemented)
    wheelchair_accessible = Column(Integer)
    bikes_allowed = Column(Integer)

    # Relationships and foreign keys

    route = relationship("Route", back_populates="trips")
    calendar = relationship("Calendar", back_populates="trips")
    geoshape = relationship("GeoShape", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip")
    frequencies = relationship("Frequency", back_populates="trip")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    trip_id = Column(String(255), primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)

    # Columns

    stop_id = Column(String(255))
    arrival_time = Column(Interval)
    departure_time = Column(Interval)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)
    continuous_pickup = Column(Integer)
    continuous_drop_off = Column(Integer)
    shape_dist_traveled = Column(Float)
    timepoint = Column(Integer)

    # Relationships and foreign keys

    trip = relationship("Trip", back_populates="stop_times")
    stop = relationship("Stop", back_populates="stop_times")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    service_id = Column(String(255), primary_key=True)

    # Columns

    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    # Relationships and foreign keys

    trips = relationship("Trip", back_populates="calendar")
    calendar_dates = relationship("CalendarDate", back_populates="calendar")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    service_id = Column(String(255), primary_key=True)
    date = Column(Date, primary_key=True)

    # Columns

    exception_type = Column(Integer)

    # Relationships and foreign keys

    calendar = relationship("Calendar", back_populates="calendar_dates")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    shape_id = Column(String(255), primary_key=True)
    shape_pt_sequence = Column(Integer, primary_key=True)

    # Columns

    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_dist_traveled = Column(Float)

    # Relationships and foreign keys

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    geoshape_id = Column(String(255), primary_key=True)

    # Columns

    geoshape = Column(Geometry(geometry_type="LINESTRING", srid=4326))

    # Relationships and foreign keys

    trips = relationship("Trip", back_populates="geoshape")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    trip_id = Column(String(255), primary_key=True)
    start_time = Column(Time, primary_key=True)

    # Columns

    end_time = Column(Time)
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    # Relationships and foreign keys

    trip = relationship("Trip", back_populates="frequencies")

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

    # Primary key columns

    feed_id = Column(String(255), primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Columns

    feed_publisher_name = Column(String(255))
    feed_publisher_url = Column(String(255))
    feed_lang = Column(String(31))
    default_lang = Column(String(31))
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(255))
    feed_contact_email = Column(String(255))
    feed_contact_url = Column(String(255))

    # Realtionships and foreign keys

    __table_args__ = (
        ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.feed_id"],
        ),
    )


"""
Notes:

- It's important to note that the ForeignKeyConstraint is the only way to define a composite foreign key. While we could also have placed individual ForeignKey objects on individual columns, SQLAlchemy would not be aware that these two values should be paired together - it would be two individual foreign key constraints instead of a single composite foreign key referencing two columns. (https://docs.sqlalchemy.org/en/20/core/constraints.html)
"""
