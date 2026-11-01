# Workout Tracker API

## Description

A Flask REST API that allows users to register, log in, and
manage their personal workout records.

The application uses session-based authentication,
Flask-Bcrypt, SQLite, SQLAlchemy and Flask-Migrate.

## Features

- User registration
- User login and logout
- Session checking
- Secure password hashing
- Create workouts
- View workouts
- Update workouts
- Delete workouts
- Pagination
- User ownership protection
- Automated tests

## Installation

Clone the repository:

    git clone <YOUR-REPOSITORY-URL>

Enter the project:

    cd workout-api

Install dependencies:

    pipenv install --dev

Activate the environment:

    pipenv shell

## Database setup

Initialize migrations:

    flask --app app db init

Create migration:

    flask --app app db migrate -m "create users and workouts"

Apply migration:

    flask --app app db upgrade

## Seed database

    python seed.py

Demo credentials:

Username: demo
Email: demo@example.com
Password: password123

## Run application

    flask --app app run

The API runs at:

http://127.0.0.1:5000

## Authentication endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login |
| DELETE | /api/auth/logout | Logout |
| GET | /api/auth/me | Check current session |

## Workout endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/workouts | List workouts |
| POST | /api/workouts | Create workout |
| PATCH | /api/workouts/<id> | Update workout |
| DELETE | /api/workouts/<id> | Delete workout |

## Pagination

Example:

    GET /api/workouts?page=1&per_page=10

## Testing

Run automated tests:

    python -m pytest -v

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- SQLite
- Pytest