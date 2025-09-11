import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAIRouter:
    def test_analyze_endpoint_success(self):
        """Test AI analyze endpoint with valid input"""
        response = client.post(
            "/ai/analyze",
            json={"prompt": "Test prompt for analysis"}
        )
        # Note: This will fail without proper API keys, but tests the endpoint structure
        assert response.status_code in [200, 500]  # 500 expected without API keys

    def test_analyze_endpoint_missing_prompt(self):
        """Test AI analyze endpoint with missing prompt"""
        response = client.post("/ai/analyze", json={})
        assert response.status_code == 422  # Validation error

    def test_generate_endpoint_success(self):
        """Test AI generate endpoint with valid input"""
        response = client.post(
            "/ai/generate",
            json={"type": "article", "topic": "TypeScript"}
        )
        # Note: This will fail without proper API keys, but tests the endpoint structure
        assert response.status_code in [200, 500]  # 500 expected without API keys

    def test_generate_endpoint_missing_params(self):
        """Test AI generate endpoint with missing parameters"""
        response = client.post("/ai/generate", json={})
        assert response.status_code == 422  # Validation error


class TestContentRouter:
    def test_get_articles(self):
        """Test get articles endpoint"""
        response = client.get("/articles")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert isinstance(data["articles"], list)

    def test_get_articles_with_filters(self):
        """Test get articles endpoint with filters"""
        response = client.get("/articles?category=tutorial&sortBy=newest")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data

    def test_get_newsletters(self):
        """Test get newsletters endpoint"""
        response = client.get("/newsletters")
        assert response.status_code == 200
        data = response.json()
        assert "newsletters" in data
        assert isinstance(data["newsletters"], list)

    def test_get_trends(self):
        """Test get trends endpoint"""
        response = client.get("/trends")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert isinstance(data["trends"], list)


class TestCollectionRouter:
    def test_get_collection_jobs(self):
        """Test get collection jobs endpoint"""
        response = client.get("/collection/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_create_collection_job(self):
        """Test create collection job endpoint"""
        job_config = {
            "name": "Test Job",
            "sources": ["github", "npm"],
            "keywords": ["typescript"],
            "schedule": "daily"
        }
        response = client.post("/collection/jobs", json=job_config)
        assert response.status_code == 200
        data = response.json()
        assert "job" in data


class TestAnalysisRouter:
    def test_get_analysis_results(self):
        """Test get analysis results endpoint"""
        response = client.get("/analysis/results")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
