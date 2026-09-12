import pytest


@pytest.fixture(scope='function')
def project_id(client, admin_token):
    """Create a project once per module and return its id.

    Using a fixture avoids module-level global state (e.g., `global project_id`)
    which makes tests harder to reason about and can create ordering
    dependencies. The fixture is created before tests that request it run.
    """
    headers = {'Authorization': f'Bearer {admin_token}'}
    payload = {'name': 'Test Project', 'code': 'TP1', 'description': 'desc'}
    resp = client.post('/projects/', json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data['name'] == 'Test Project'
    assert data['code'] == 'TP1'
    return data['id']


def test_get_project(client, project_id):
    resp = client.get(f'/projects/{project_id}')
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == project_id


def test_patch_project_as_admin(admin_token, client, project_id):
    headers = {'Authorization': f'Bearer {admin_token}'}
    resp = client.patch(f'/projects/{project_id}', json={'description': 'updated'}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data['description'] == 'updated'


def test_delete_project_as_admin(admin_token, client, project_id):
    headers = {'Authorization': f'Bearer {admin_token}'}
    resp = client.delete(f'/projects/{project_id}', headers=headers)
    assert resp.status_code == 200
    assert resp.json()['status'] == 'deleted'


def test_project_code_validation(admin_token, client):
    headers = {'Authorization': f'Bearer {admin_token}'}
    # invalid code with spaces
    resp = client.post('/projects/', json={'name': 'Bad', 'code': 'bad code'}, headers=headers)
    assert resp.status_code == 422
