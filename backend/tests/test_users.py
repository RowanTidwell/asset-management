import pytest


def test_signup_and_get_me(client):
    # signup
    resp = client.post('/auth/signup', json={'username': 'user1', 'email': 'user1@example.com', 'password': 'pw123', 'display_name': 'User One'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['username'] == 'user1'

    # login
    resp = client.post('/auth/token', data={'username': 'user1', 'password': 'pw123'})
    assert resp.status_code == 200
    token = resp.json()['access_token']

    # get me
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/users/me', headers=headers)
    assert resp.status_code == 200
    assert resp.json()['username'] == 'user1'


def test_admin_create_and_list_users(client, admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    # admin creates a user with role
    payload = {'username': 'dev', 'email': 'dev@example.com', 'password': 'devpw', 'display_name': 'Dev'}
    resp = client.post('/users/', json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data['username'] == 'dev'

    # admin lists users
    resp = client.get('/users/', headers=headers)
    assert resp.status_code == 200
    assert any(u['username'] == 'dev' for u in resp.json())


def test_user_update_and_password(client):
    # signup new user
    resp = client.post('/auth/signup', json={'username': 'up', 'email': 'up@example.com', 'password': 'oldpw', 'display_name': 'Up'})
    assert resp.status_code == 200
    resp = client.post('/auth/token', data={'username': 'up', 'password': 'oldpw'})
    token = resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # update display name (use /users/{id})
    me = client.get('/users/me', headers=headers).json()
    uid = me['id']
    resp = client.patch(f'/users/{uid}', json={'display_name': 'Updated'}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()['display_name'] == 'Updated'

    # change password (with old)
    resp = client.post(f'/users/{uid}/change-password', json={'old_password': 'oldpw', 'new_password': 'newpw'}, headers=headers)
    assert resp.status_code == 200

    # login with new password
    resp = client.post('/auth/token', data={'username': 'up', 'password': 'newpw'})
    assert resp.status_code == 200

