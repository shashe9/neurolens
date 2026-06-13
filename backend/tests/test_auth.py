import pytest
from fastapi.testclient import TestClient
from fastapi import status
from main import app
from app.api.dependencies import get_current_parent
from app.database.session import get_db
from app.models.models import Parent, Child
from app.core.security import get_password_hash, create_access_token

def test_authentication_flow(db):
    # Ensure any global overrides are cleared for get_current_parent
    # so we test the actual production authentication dependency.
    original_overrides = app.dependency_overrides.copy()
    if get_current_parent in app.dependency_overrides:
        del app.dependency_overrides[get_current_parent]

    # Set the test DB override
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db

    try:
        # 1. Create a test parent in the db
        email = "auth.tester@example.com"
        password = "secure_test_password"
        hashed = get_password_hash(password)
        
        test_parent = Parent(
            first_name="Auth",
            last_name="Tester",
            email=email,
            hashed_password=hashed
        )
        db.add(test_parent)
        db.commit()
        db.refresh(test_parent)

        from datetime import date
        # Also create a child for this parent to test data isolation / successful query
        test_child = Child(
            first_name="Testy",
            last_name="Tester",
            date_of_birth=date(2024, 1, 1),
            gender="male"
        )
        test_child.parents.append(test_parent)
        db.add(test_child)
        db.commit()

        # Initialize the TestClient inside this context
        with TestClient(app) as test_client:
            # A. Test Login with correct credentials
            response = test_client.post(
                "/auth/login",
                json={"email": email, "password": password}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["email"] == email
            assert data["parent_id"] == str(test_parent.id)
            
            token = data["access_token"]

            # B. Test Login with incorrect credentials
            response_fail_pw = test_client.post(
                "/auth/login",
                json={"email": email, "password": "wrong_password"}
            )
            assert response_fail_pw.status_code == status.HTTP_401_UNAUTHORIZED
            assert response_fail_pw.json()["detail"] == "Invalid email or password"

            response_fail_email = test_client.post(
                "/auth/login",
                json={"email": "nonexistent@example.com", "password": password}
            )
            assert response_fail_email.status_code == status.HTTP_401_UNAUTHORIZED

            # C. Access protected endpoint (GET /children) without token
            response_unauth = test_client.get("/children")
            assert response_unauth.status_code == status.HTTP_401_UNAUTHORIZED
            assert "detail" in response_unauth.json()

            # D. Access protected endpoint with invalid token header
            response_invalid_tok = test_client.get(
                "/children",
                headers={"Authorization": "Bearer invalid_token_value"}
            )
            assert response_invalid_tok.status_code == status.HTTP_401_UNAUTHORIZED

            # E. Access protected endpoint with correct token
            response_success = test_client.get(
                "/children",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response_success.status_code == status.HTTP_200_OK
            children_list = response_success.json()
            assert len(children_list) == 1
            assert children_list[0]["first_name"] == "Testy"

    finally:
        # Restore original dependency overrides
        app.dependency_overrides = original_overrides
