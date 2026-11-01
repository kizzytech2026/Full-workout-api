from app import create_app
from models import db, User, Workout

app = create_app()

with app.app_context():

    db.create_all()

    if User.query.count() == 0:

        demo = User(
            username="demo",
            email="demo@example.com"
        )

        demo.set_password("password123")

        db.session.add(demo)
        db.session.flush()

        workouts = [
            Workout(
                title="Morning Run",
                workout_type="Cardio",
                duration_minutes=30,
                notes="Easy pace around the neighborhood",
                user_id=demo.id
            ),

            Workout(
                title="Strength Training",
                workout_type="Strength",
                duration_minutes=45,
                notes="Upper body session",
                user_id=demo.id
            )
        ]

        db.session.add_all(workouts)
        db.session.commit()

        print("Seed data created successfully!")

    else:
        print("Database already contains users.")