import pytest
from arxiv_sns_proto.db import get_db

def test_register(client):
    response = client.post('/auth/register', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302  # Redirect after successful registration

def test_login(client):
    # First, register a user
    client.post('/auth/register', data={'username': 'testuser', 'password': 'testpass'})
    
    # Then, try to log in
    response = client.post('/auth/login', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302  # Redirect after successful login

def test_logout(client):
    # First, register and log in a user
    client.post('/auth/register', data={'username': 'testuser', 'password': 'testpass'})
    client.post('/auth/login', data={'username': 'testuser', 'password': 'testpass'})
    
    # Then, log out
    response = client.get('/auth/logout')
    assert response.status_code == 302  # Redirect after logout
    
