import os
import pendulum

SQLALCHEMY_DATABASE_URI = (
    os.environ.get("DATABASE_URL")
    or f"postgresql+psycopg2://postgres:docker@0.0.0.0:5432/postgres"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_ACCESS_LIFESPAN = os.environ.get("JWT_ACCESS_LIFESPAN") or pendulum.duration(days=7)
JWT_REFRESH_LIFESPAN = os.environ.get("JWT_REFRESH_LIFESPAN") or pendulum.duration(months=6)