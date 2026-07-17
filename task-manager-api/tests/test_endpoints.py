"""Regressão de contrato: endpoints originais respondem com o mesmo formato."""


def test_index_and_health(client):
    assert client.get('/').status_code == 200
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'


def test_list_tasks_returns_list(client):
    resp = client.get('/tasks')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_task_crud_flow(client, seeded_user, seeded_category):
    created = client.post('/tasks', json={
        'title': 'Nova task',
        'priority': 2,
        'user_id': seeded_user['id'],
        'category_id': seeded_category['id'],
        'due_date': '2020-01-01',
        'tags': ['a', 'b'],
    })
    assert created.status_code == 201
    task = created.get_json()
    assert task['tags'] == ['a', 'b']

    fetched = client.get(f"/tasks/{task['id']}")
    assert fetched.status_code == 200
    assert fetched.get_json()['overdue'] is True  # due_date no passado

    listed = client.get('/tasks').get_json()
    assert listed[0]['user_name'] == 'Alice'
    assert listed[0]['category_name'] == 'Backend'

    updated = client.put(f"/tasks/{task['id']}", json={'status': 'done'})
    assert updated.status_code == 200
    assert updated.get_json()['status'] == 'done'

    stats = client.get('/tasks/stats').get_json()
    assert stats['total'] == 1
    assert stats['done'] == 1
    assert stats['completion_rate'] == 100.0

    deleted = client.delete(f"/tasks/{task['id']}")
    assert deleted.status_code == 200


def test_task_validation_errors(client):
    assert client.post('/tasks', json={'title': 'ab'}).status_code == 400
    assert client.post('/tasks', json={}).status_code == 400
    assert client.get('/tasks/9999').status_code == 404
    assert client.put('/tasks/9999', json={'title': 'abc'}).status_code == 404


def test_search_tasks(client, seeded_user):
    client.post('/tasks', json={'title': 'Comprar leite', 'user_id': seeded_user['id']})
    client.post('/tasks', json={'title': 'Lavar carro'})
    resp = client.get('/tasks/search?q=leite')
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_create_user_does_not_leak_password(client):
    resp = client.post('/users', json={
        'name': 'Bob',
        'email': 'bob@example.com',
        'password': 'senha-forte-1',
    })
    assert resp.status_code == 201
    assert 'password' not in resp.get_json()


def test_login_flow(client, seeded_user):
    ok = client.post('/login', json={
        'email': seeded_user['email'],
        'password': seeded_user['password'],
    })
    assert ok.status_code == 200
    body = ok.get_json()
    assert body['token']
    assert 'password' not in body['user']

    bad = client.post('/login', json={
        'email': seeded_user['email'],
        'password': 'errada',
    })
    assert bad.status_code == 401


def test_users_listing_and_report(client, seeded_user):
    users = client.get('/users')
    assert users.status_code == 200
    assert users.get_json()[0]['task_count'] == 0

    report = client.get(f"/reports/user/{seeded_user['id']}")
    assert report.status_code == 200
    assert report.get_json()['statistics']['total_tasks'] == 0

    assert client.get('/reports/user/9999').status_code == 404


def test_summary_report_keys(client):
    resp = client.get('/reports/summary')
    assert resp.status_code == 200
    body = resp.get_json()
    for key in ('overview', 'tasks_by_status', 'tasks_by_priority',
                'overdue', 'recent_activity', 'user_productivity'):
        assert key in body


def test_category_crud(client, seeded_category):
    listed = client.get('/categories')
    assert listed.status_code == 200
    assert listed.get_json()[0]['task_count'] == 0

    created = client.post('/categories', json={'name': 'Docs'})
    assert created.status_code == 201

    cat_id = created.get_json()['id']
    updated = client.put(f'/categories/{cat_id}', json={'color': '#ffffff'})
    assert updated.status_code == 200
    assert updated.get_json()['color'] == '#ffffff'

    assert client.delete(f'/categories/{cat_id}').status_code == 200
    assert client.delete('/categories/9999').status_code == 404


def test_secret_key_comes_from_env(monkeypatch):
    """Regressão do finding CRITICAL: SECRET_KEY hardcoded."""
    import importlib

    monkeypatch.setenv('SECRET_KEY', 'valor-do-ambiente')
    import config.settings as settings
    importlib.reload(settings)
    assert settings.Config.SECRET_KEY == 'valor-do-ambiente'

    monkeypatch.delenv('SECRET_KEY')
    importlib.reload(settings)
    assert settings.Config.SECRET_KEY == 'dev-only-change-me'
