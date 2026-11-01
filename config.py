import os

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-this-development-secret"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///workouts.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False