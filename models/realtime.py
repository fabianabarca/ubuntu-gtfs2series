from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import Integer, Float, Date, Time, DateTime, String, Text
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement

Base = declarative_base()


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
    vehicle_trip_tripId = Column(String(255), primary_key=True)
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
