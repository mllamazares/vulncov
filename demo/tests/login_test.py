import pytest
from flask import Flask
import os 
import sys
sys.path.append(sys.path[0] + "/../src")

from dummyapp import app, init_db, DATABASE  

@pytest.fixture(scope='module')
def client():
    # Initialize the database once before running tests
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    init_db()
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Cleanup the database after tests
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

def test_login_success(client):
    # Test for successful login
    response = client.get('/login?username=admin&password=admin123')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_login_failure(client):
    # Test for failureful login
    response = client.get('/login?username=admin&password=wrongpassword')
    assert response.status_code == 403
    assert b"Invalid credentials" in response.data