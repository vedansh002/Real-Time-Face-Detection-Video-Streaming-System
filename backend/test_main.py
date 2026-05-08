from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

def test_get_roi():
    """
    Test that the REST API correctly returns a 200 OK status 
    and the expected JSON structure for historical data.
    """
    #fake GET request to the endpoint
    response = client.get("/api/roi?limit=5")
    
    #check 
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "error"]
    
    #ensure 'data' is actually a list
    if data["status"] == "success":
        assert isinstance(data["data"], list)