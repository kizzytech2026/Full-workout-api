from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from config import Config
from models import db, bcrypt, User, Workout

migrate = Migrate()


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # HOME ROUTE
    @app.get("/")
    def home():
        return jsonify({
            "message": "Workout Tracker API is running"
        }), 200

    # REGISTER
    @app.post("/api/auth/register")
    def register():

        data = request.get_json(silent=True) or {}

        username = str(data.get("username", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = data.get("password", "")

        if (
            not username
            or not email
            or not isinstance(password, str)
            or len(password) < 8
        ):
            return jsonify({
                "error": "Username, email and a password of at least 8 characters are required"
            }), 400

        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            return jsonify({
                "error": "Username or email already exists"
            }), 409

        session.clear()
        session["user_id"] = user.id

        return jsonify({
            "message": "Registration successful",
            "user": user.to_dict()
        }), 201

    # LOGIN
    @app.post("/api/auth/login")
    def login():

        data = request.get_json(silent=True) or {}

        identifier = str(
            data.get("username") or data.get("email") or ""
        ).strip()

        password = data.get("password", "")

        user = User.query.filter(
            db.or_(
                User.username == identifier,
                User.email == identifier.lower()
            )
        ).first()

        if (
            not user
            or not isinstance(password, str)
            or not user.check_password(password)
        ):
            return jsonify({
                "error": "Invalid username/email or password"
            }), 401

        session.clear()
        session["user_id"] = user.id

        return jsonify({
            "message": "Login successful",
            "user": user.to_dict()
        }), 200

    # LOGOUT
    @app.delete("/api/auth/logout")
    def logout():

        if "user_id" not in session:
            return jsonify({
                "error": "Authentication required"
            }), 401

        session.clear()

        return jsonify({
            "message": "Logged out successfully"
        }), 200

    # CHECK CURRENT SESSION
    @app.get("/api/auth/me")
    def me():

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "error": "Authentication required"
            }), 401

        user = db.session.get(User, user_id)

        if not user:
            session.clear()

            return jsonify({
                "error": "Authentication required"
            }), 401

        return jsonify({
            "user": user.to_dict()
        }), 200

    # GET CURRENT USER
    def current_user():

        user_id = session.get("user_id")

        if not user_id:
            return None

        return db.session.get(User, user_id)

    # GET ALL WORKOUTS (PAGINATION)
    @app.get("/api/workouts")
    def list_workouts():

        user = current_user()

        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401

        try:
            page = max(int(request.args.get("page", 1)), 1)

            per_page = min(
                max(int(request.args.get("per_page", 10)), 1),
                100
            )

        except (TypeError, ValueError):
            return jsonify({
                "error": "page and per_page must be integers"
            }), 400

        pagination = Workout.query.filter_by(
            user_id=user.id
        ).order_by(
            Workout.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            "workouts": [
                workout.to_dict()
                for workout in pagination.items
            ],

            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200

    # CREATE WORKOUT
    @app.post("/api/workouts")
    def create_workout():

        user = current_user()

        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401

        data = request.get_json(silent=True) or {}

        title = str(data.get("title", "")).strip()

        workout_type = str(
            data.get("workout_type", "")
        ).strip()

        duration = data.get("duration_minutes")

        notes = data.get("notes", "")

        if not title or not workout_type:
            return jsonify({
                "error": "title and workout_type are required"
            }), 400

        if (
            isinstance(duration, bool)
            or not isinstance(duration, int)
            or duration <= 0
        ):
            return jsonify({
                "error": "duration_minutes must be a positive integer"
            }), 400

        workout = Workout(
            title=title,
            workout_type=workout_type,
            duration_minutes=duration,
            notes=str(notes) if notes is not None else None,
            user_id=user.id
        )

        db.session.add(workout)
        db.session.commit()

        return jsonify({
            "message": "Workout created successfully",
            "workout": workout.to_dict()
        }), 201

    # UPDATE WORKOUT
    @app.patch("/api/workouts/<int:workout_id>")
    def update_workout(workout_id):

        user = current_user()

        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401

        workout = Workout.query.filter_by(
            id=workout_id,
            user_id=user.id
        ).first()

        if not workout:
            return jsonify({
                "error": "Workout not found"
            }), 404

        data = request.get_json(silent=True) or {}

        if "title" in data:

            title = str(data["title"]).strip()

            if not title:
                return jsonify({
                    "error": "title cannot be empty"
                }), 400

            workout.title = title

        if "workout_type" in data:

            workout_type = str(data["workout_type"]).strip()

            if not workout_type:
                return jsonify({
                    "error": "workout_type cannot be empty"
                }), 400

            workout.workout_type = workout_type

        if "duration_minutes" in data:

            duration = data["duration_minutes"]

            if (
                isinstance(duration, bool)
                or not isinstance(duration, int)
                or duration <= 0
            ):
                return jsonify({
                    "error": "duration_minutes must be a positive integer"
                }), 400

            workout.duration_minutes = duration

        if "notes" in data:
            workout.notes = data["notes"]

        db.session.commit()

        return jsonify({
            "message": "Workout updated successfully",
            "workout": workout.to_dict()
        }), 200

    # DELETE WORKOUT
    @app.delete("/api/workouts/<int:workout_id>")
    def delete_workout(workout_id):

        user = current_user()

        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401

        workout = Workout.query.filter_by(
            id=workout_id,
            user_id=user.id
        ).first()

        if not workout:
            return jsonify({
                "error": "Workout not found"
            }), 404

        db.session.delete(workout)
        db.session.commit()

        return jsonify({
            "message": "Workout deleted successfully"
        }), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)