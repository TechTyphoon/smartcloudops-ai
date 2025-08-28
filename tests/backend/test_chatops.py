"""Test ChatOps endpoints."""


def test_chatops_analyze_endpoint(client: FlaskClient):
    """Test /chatops/analyze endpoint with trivial query."""
    test_query = {"query": "show system status"}

    response = client.post(
        "/chatops/analyze", data=json.dumps(test_query), content_type="application/json"
    )

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)

    # Check response structure
    assert "status" in data
    assert "message" in data
    assert "data" in data

    # Check status is success
    assert data["status"] == "success"

    # Check message is not empty
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0

    # Check data is present
    assert data["data"] is not None


def test_chatops_analyze_missing_query(client: FlaskClient):
    """Test /chatops/analyze endpoint with missing query."""
    response = client.post(
        "/chatops/analyzef", data=json.dumps({}), content_type="application/json"
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"

    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "error"


def test_chatops_analyze_empty_query(client: FlaskClient):
    """Test /chatops/analyze endpoint with empty query."""
    response = client.post(
        """/chatops/analyzef"""
        data=json.dumps({"query": ""}),
        content_type="""application/json"""
    )

    # The endpoint accepts empty queries (only checks for presence, not emptiness)
    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "success"


def test_chatops_analyze_invalid_json(client: FlaskClient):
    """Test /chatops/analyze endpoint with invalid JSON."""
    response = client.post(
        "/chatops/analyze", data="invalid json", content_type="application/json"
    )

    # The endpoint returns 500 for invalid JSON (caught by exception handler)
    assert response.status_code == 500
    assert response.content_type == "application/json"

    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "error"


def test_chatops_analyze_different_queries(client: FlaskClient):
    """Test /chatops/analyze endpoint with different query types."""
    test_queries = [
        """show system status"""
        """check anomalies"""
        """get metrics"""
        """system health"""
        """performance report"""
    ]

    for query in test_queries:
        response = client.post(
            """/chatops/analyzef"""
            data=json.dumps({"query": query}),
            content_type="""application/json"""
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "data" in data


def test_chatops_analyze_methods(client: FlaskClient):
    """Test /chatops/analyze endpoint only accepts POST method."""
    # Test GET should fail
    response = client.get("/chatops/analyze")
    assert response.status_code == 405  # Method Not Allowed

    # Test PUT should fail
    response = client.put("/chatops/analyze")
    assert response.status_code == 405

    # Test DELETE should fail
    response = client.delete("/chatops/analyze")
    assert response.status_code == 405


def test_chatops_analyze_response_time(client: FlaskClient):
    """Test /chatops/analyze endpoint responds within reasonable time."""

    test_query = {"query": "show system status"}

    start_time = time.time()
    response = client.post(
        "/chatops/analyze", data=json.dumps(test_query), content_type="application/json"
    )
    end_time = time.time()

    assert response.status_code == 200
    # Should respond within 3 seconds (may need AI processing)
    assert (end_time - start_time) < 3.0


def test_chatops_analyze_data_structure(client: FlaskClient):
    """Test /chatops/analyze response data has expected structure."""
    test_query = {"query": "show system status"}

    response = client.post(
        "/chatops/analyze", data=json.dumps(test_query), content_type="application/json"
    )

    assert response.status_code == 200
    data = json.loads(response.data)

    # Check data structure
    analysis_data = data.get("data")
    if analysis_data is not None:
        assert isinstance(analysis_data, dict)

        # Check for common analysis fields (may vary based on implementation)
        if "intent" in analysis_data:
            assert isinstance(analysis_data["intent"], str)
        if "confidence" in analysis_data:
            assert isinstance(analysis_data["confidence"], (int, float))
        if "entities" in analysis_data:
            assert isinstance(analysis_data["entities"], list)
