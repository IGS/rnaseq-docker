import os
import pytest
import sys
sys.path.append("..")
from flask import current_app

### In Development ###

@pytest.fixture
def client():
    current_app.config['TESTING'] = True
    client = current_app.test_client()
    yield client

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_login_logout(client):
    """Make sure login and logout works."""

    rv = login(client, current_app.config['USERNAME'], current_app.config['PASSWORD'])
    assert b'You were logged in' in rv.data

    rv = logout(client)
    assert b'You were logged out' in rv.data

    rv = login(client, current_app.config['USERNAME'] + 'x', current_app.config['PASSWORD'])
    assert b'Invalid username' in rv.data

    rv = login(client, current_app.config['USERNAME'], current_app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in rv.data
