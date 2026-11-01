from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(128),
        nullable=False
    )

    workouts = db.relationship(
        "Workout",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash,
            password
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(120),
        nullable=False
    )

    workout_type = db.Column(
        db.String(80),
        nullable=False
    )

    duration_minutes = db.Column(
        db.Integer,
        nullable=False
    )

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="workouts"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "workout_type": self.workout_type,
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }