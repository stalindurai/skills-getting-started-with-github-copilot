"""
Tests for the High School Management System API (src/app.py)

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    
    # Arrange: Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Practice soccer skills and compete in friendly matches",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Basketball Club": {
            "description": "Develop basketball skills and play team games",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Practice acting and stage performance",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Build public speaking and critical reasoning skills",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Explore scientific ideas through experiments and projects",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Verify that GET /activities returns all activities"""
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Soccer Club", "Basketball Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Verify that activity data has correct structure"""
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert - Check one activity for correct structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_contains_correct_participants(self, client, reset_activities):
        """Verify that activities have correct initial participants"""
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html"""
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successfully_adds_participant(self, client, reset_activities):
        """Verify successful signup adds participant to activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert - Response is successful
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Assert - Participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]

    def test_signup_prevents_duplicate_registration(self, client, reset_activities):
        """Verify that duplicate signup returns 400 error"""
        # Arrange
        email = "michael@mergington.edu"  # Already registered
        activity = "Chess Club"
        
        # Act - Try to sign up someone already registered
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower() or "already" in data["detail"].lower()

    def test_signup_to_nonexistent_activity_returns_404(self, client, reset_activities):
        """Verify that signup to non-existent activity returns 404"""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_different_participants(self, client, reset_activities):
        """Verify that multiple different participants can sign up"""
        # Arrange
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        activity = "Soccer Club"
        
        # Act - Sign up multiple participants
        for email in emails:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert - Verify all were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        soccer_participants = activities_data[activity]["participants"]
        
        for email in emails:
            assert email in soccer_participants

    def test_signup_maintains_other_activity_data(self, client, reset_activities):
        """Verify that signup doesn't modify other activity data"""
        # Arrange
        email = "newsignup@mergington.edu"
        activity_to_modify = "Chess Club"
        activity_to_check = "Programming Class"
        
        # Act
        client.post(
            f"/activities/{activity_to_modify.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert - Other activities are unchanged
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert activity_to_check in activities_data
        assert len(activities_data[activity_to_check]["participants"]) == 2


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successfully_removes_participant(self, client, reset_activities):
        """Verify successful unregister removes participant from activity"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        
        # Assert - Response is successful
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Assert - Participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self, client, reset_activities):
        """Verify that unregistering non-registered participant returns 400"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Verify that unregistering from non-existent activity returns 404"""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_multiple_participants(self, client, reset_activities):
        """Verify that multiple participants can be unregistered"""
        # Arrange
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        activity = "Soccer Club"
        
        # Arrange - First add participants
        for email in emails:
            client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
        
        # Act - Unregister two of them
        response1 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={emails[0]}"
        )
        response2 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={emails[1]}"
        )
        
        # Assert - Unregister responses are successful
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Assert - Correct participants remain
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        soccer_participants = activities_data[activity]["participants"]
        
        assert emails[0] not in soccer_participants
        assert emails[1] not in soccer_participants
        assert emails[2] in soccer_participants

    def test_unregister_from_empty_activity(self, client, reset_activities):
        """Verify that unregistering from activity with no participants returns 400"""
        # Arrange
        email = "student@mergington.edu"
        activity = "Soccer Club"  # No participants initially
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flow"""

    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Test complete flow: signup then unregister"""
        # Arrange
        email = "testuser@mergington.edu"
        activity = "Basketball Club"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert - Signed up successfully
        assert signup_response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        
        # Assert - Unregistered successfully
        assert unregister_response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]

    def test_cannot_signup_after_unregister_then_signup_again(self, client, reset_activities):
        """Test that participant can signup again after unregistering"""
        # Arrange
        email = "testuser@mergington.edu"
        activity = "Art Club"
        
        # Act - Sign up
        client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
        
        # Act - Unregister
        client.post(f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}")
        
        # Act - Sign up again
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Assert - Re-signup succeeds
        assert response.status_code == 200
        
        # Assert - Participant is signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]

