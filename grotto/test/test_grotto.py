#!/usr/bin/env python3
import os
import pytest
import sys
sys.path.append("..")
from flask import current_app
from application import create_app

### In Development ###

@pytest.fixture
def test_client():
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_client = test_app.test_client()

    # Establish an application context before running the tests.
    ctx = test_app.app_context()
    ctx.push()
 
    yield test_client  # this is where the testing happens!
    # Clean testing environment
    ctx.pop()

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
