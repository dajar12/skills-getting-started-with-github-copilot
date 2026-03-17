import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing from {activity_name}"
    
    def test_get_activities_participants_are_lists(self, client, reset_activities):
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            assert len(activity_data["participants"]) > 0


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client, reset_activities):
        # Arrange & Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_successfully(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in reset_activities[activity_name]["participants"]
        assert len(reset_activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_returns_success_message(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_duplicate_student_returns_error(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Art Studio"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in reset_activities[activity_name]["participants"]
        assert email2 in reset_activities[activity_name]["participants"]
    
    def test_signup_does_not_affect_other_activities(self, client, reset_activities):
        # Arrange
        activity1 = "Music Ensemble"
        activity2 = "Robotics Club"
        email = "newstudent@mergington.edu"
        initial_robot_count = len(reset_activities[activity2]["participants"])
        
        # Act
        client.post(f"/activities/{activity1}/signup", params={"email": email})
        
        # Assert
        assert email in reset_activities[activity1]["participants"]
        assert email not in reset_activities[activity2]["participants"]
        assert len(reset_activities[activity2]["participants"]) == initial_robot_count


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participant endpoint"""
    
    def test_remove_existing_participant_successfully(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in reset_activities[activity_name]["participants"]
        assert len(reset_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_returns_success_message(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert "Removed" in data["message"]
    
    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Fake Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_remove_preserves_other_participants(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        other_email = "daniel@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert email_to_remove not in reset_activities[activity_name]["participants"]
        assert other_email in reset_activities[activity_name]["participants"]
    
    def test_removed_participant_can_signup_again(self, client, reset_activities):
        # Arrange
        activity_name = "Tennis Club"
        email = "lucas@mergington.edu"
        
        # Act - Remove participant
        client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        
        # Act - Sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in reset_activities[activity_name]["participants"]
