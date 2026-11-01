def register(client, username, email):

    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "password123"
        }
    )


def create_workout(client, title="Morning Run"):

    return client.post(
        "/api/workouts",
        json={
            "title": title,
            "workout_type": "Cardio",
            "duration_minutes": 30,
            "notes": "Easy pace"
        }
    )


def test_workout_routes_require_authentication(client):

    assert client.get(
        "/api/workouts"
    ).status_code == 401

    assert create_workout(client).status_code == 401

    assert client.patch(
        "/api/workouts/1",
        json={"title": "Updated"}
    ).status_code == 401

    assert client.delete(
        "/api/workouts/1"
    ).status_code == 401


def test_create_list_update_delete_workout(registered_client):

    created = create_workout(registered_client)

    assert created.status_code == 201

    workout_id = created.get_json()["workout"]["id"]

    listing = registered_client.get("/api/workouts")

    assert listing.status_code == 200

    assert len(
        listing.get_json()["workouts"]
    ) == 1

    updated = registered_client.patch(
        f"/api/workouts/{workout_id}",
        json={"title": "Evening Run"}
    )

    assert updated.status_code == 200

    assert (
        updated.get_json()["workout"]["title"]
        == "Evening Run"
    )

    deleted = registered_client.delete(
        f"/api/workouts/{workout_id}"
    )

    assert deleted.status_code == 200

    assert registered_client.get(
        "/api/workouts"
    ).get_json()["workouts"] == []


def test_user_cannot_access_another_users_workout(client):

    register(
        client,
        "alice",
        "alice@example.com"
    )

    workout = create_workout(client).get_json()["workout"]

    workout_id = workout["id"]

    client.delete("/api/auth/logout")

    register(
        client,
        "bob",
        "bob@example.com"
    )

    assert client.patch(
        f"/api/workouts/{workout_id}",
        json={"title": "Stolen"}
    ).status_code == 404

    assert client.delete(
        f"/api/workouts/{workout_id}"
    ).status_code == 404

    assert client.get(
        "/api/workouts"
    ).get_json()["workouts"] == []


def test_invalid_workout_data_rejected(registered_client):

    response = registered_client.post(
        "/api/workouts",
        json={
            "title": "Run",
            "workout_type": "Cardio",
            "duration_minutes": -5
        }
    )

    assert response.status_code == 400


def test_pagination_metadata(registered_client):

    for number in range(3):
        create_workout(
            registered_client,
            f"Workout {number}"
        )

    response = registered_client.get(
        "/api/workouts?page=1&per_page=2"
    )

    data = response.get_json()

    assert response.status_code == 200
    assert len(data["workouts"]) == 2
    assert data["pagination"]["total"] == 3
    assert data["pagination"]["pages"] == 2
    assert data["pagination"]["has_next"] is True


def test_missing_workout_returns_404(registered_client):

    assert registered_client.patch(
        "/api/workouts/999",
        json={"title": "Missing"}
    ).status_code == 404

    assert registered_client.delete(
        "/api/workouts/999"
    ).status_code == 404