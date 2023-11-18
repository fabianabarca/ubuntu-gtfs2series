from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.vehicle_position import VehiclePosition

db_user = "fab"
db_password = "gtfs2series"
db_host = "localhost"
db_port = "5432"
db_name = "gtfs2series"

# Create PostgreSQL engine
engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Create session
Session = sessionmaker(bind=engine)

# Create session instance
session = Session()

# Look for all entries in the vehicle_positions table where vehicle_trip_routeId = "39" and vehicle_trip_directionId = 0
results = session.query(VehiclePosition).filter(VehiclePosition.vehicle_trip_routeId == "39").filter(VehiclePosition.vehicle_trip_directionId == 0).all()
