from fastapi.testclient import TestClient

from artiisly_automation.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workflow_success_with_social_and_channels() -> None:
    payload = {
        "product": {
            "title": "Botanical Hoodie",
            "niche": "nature",
            "style_prompt": "Bold botanical design with modern typography for hoodie print.",
            "target_channels": ["pod", "website"],
            "base_price": 29.99,
            "destination_url": "https://store.example.com",
        },
        "social": {
            "platforms": ["instagram", "facebook"],
            "hashtags": ["#hoodie", "#nature"],
        },
    }
    response = client.post(
        "/api/v1/automation/workflows",
        json=payload,
        headers={"x-api-key": "change-me-in-prod"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "complete"
    assert len(data["result"]["channel_publications"]) == 2
    assert len(data["result"]["social_posts"]) == 2


def test_workflow_auth_failure() -> None:
    payload = {
        "product": {
            "title": "Botanical Hoodie",
            "niche": "nature",
            "style_prompt": "Bold botanical design with modern typography for hoodie print.",
            "target_channels": ["pod"],
            "base_price": 29.99,
        }
    }
    response = client.post("/api/v1/automation/workflows", json=payload)
    assert response.status_code == 401
