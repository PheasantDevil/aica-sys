import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AICA-SyS" in response.json()["message"]


def test_api_docs():
    """APIドキュメントエンドポイントのテスト"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json():
    """OpenAPI JSONエンドポイントのテスト"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
