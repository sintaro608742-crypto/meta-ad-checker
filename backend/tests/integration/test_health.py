"""
============================================
メタ広告審査チェッカー - ヘルスチェックエンドポイント統合テスト
============================================

スライス1-A: ヘルスチェック統合テスト
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


def test_health_check_returns_200(client: TestClient):
    """
    ヘルスチェックエンドポイントが200を返すことを確認
    """
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_response_structure(client: TestClient):
    """
    ヘルスチェックレスポンスの構造を確認
    """
    response = client.get("/api/health")
    data = response.json()

    # 必須フィールドの存在確認
    assert "status" in data
    assert "timestamp" in data


def test_health_check_status_is_healthy(client: TestClient):
    """
    ヘルスチェックのステータスが "healthy" であることを確認
    """
    response = client.get("/api/health")
    data = response.json()

    assert data["status"] == "healthy"


def test_health_check_timestamp_format(client: TestClient):
    """
    タイムスタンプがISO 8601形式であることを確認
    """
    response = client.get("/api/health")
    data = response.json()

    # ISO 8601形式のパースを試みる
    timestamp = data["timestamp"]
    try:
        # "Z"で終わる場合、+00:00に置換してパース
        if timestamp.endswith("Z"):
            timestamp_normalized = timestamp.replace("Z", "+00:00")
            datetime.fromisoformat(timestamp_normalized)
        else:
            datetime.fromisoformat(timestamp)
    except ValueError:
        pytest.fail(f"Invalid ISO 8601 timestamp format: {timestamp}")


def test_health_check_timestamp_is_recent(client: TestClient):
    """
    タイムスタンプが現在時刻に近いことを確認（1分以内）
    """
    response = client.get("/api/health")
    data = response.json()

    timestamp_str = data["timestamp"].replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(timestamp_str)
    now = datetime.utcnow().replace(tzinfo=timestamp.tzinfo)

    # 1分以内であることを確認
    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 60, f"Timestamp is not recent: {time_diff} seconds difference"


def test_health_check_response_content_type(client: TestClient):
    """
    レスポンスのContent-Typeがapplication/jsonであることを確認
    """
    response = client.get("/api/health")
    assert response.headers["content-type"] == "application/json"


def test_health_check_idempotent(client: TestClient):
    """
    複数回呼び出しても同じ構造のレスポンスが返ることを確認（冪等性）
    """
    response1 = client.get("/api/health")
    response2 = client.get("/api/health")

    assert response1.status_code == response2.status_code
    assert response1.json()["status"] == response2.json()["status"]


def test_health_check_no_query_params_required(client: TestClient):
    """
    クエリパラメータなしでアクセス可能であることを確認
    """
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_method_not_allowed_post(client: TestClient):
    """
    POSTメソッドでアクセスすると405エラーが返ることを確認
    """
    response = client.post("/api/health")
    assert response.status_code == 405


def test_health_check_method_not_allowed_put(client: TestClient):
    """
    PUTメソッドでアクセスすると405エラーが返ることを確認
    """
    response = client.put("/api/health")
    assert response.status_code == 405


def test_health_check_method_not_allowed_delete(client: TestClient):
    """
    DELETEメソッドでアクセスすると405エラーが返ることを確認
    """
    response = client.delete("/api/health")
    assert response.status_code == 405
