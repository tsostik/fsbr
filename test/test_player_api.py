import json
from unittest.mock import Mock

import pytest
from flask import Flask

from src import player_api
from src.players import addPlayer


@pytest.fixture
def api(monkeypatch):
    app = Flask(__name__)
    app.config.update(TESTING=True, PLAYER_API_TOKEN='test-secret')
    app.register_blueprint(player_api.player_api)
    create = Mock(return_value=123)
    unlocked = Mock(return_value=True)
    monkeypatch.setattr(player_api, 'addPlayer', create)
    monkeypatch.setattr(player_api, 'base_unlocked', unlocked)
    return app, app.test_client(), create, unlocked


def post(client, payload=None, token='test-secret', **kwargs):
    return client.post('/api/players/', json=payload, headers={'Authorization': 'Bearer ' + token}, **kwargs)


def valid():
    return dict(author_id=42, lastname='Иванов', firstname='Иван', city='16', sex='1',
                birthdate='2000/01/02', is_sputnik=False)


def test_create(api):
    _, client, create, _ = api
    response = post(client, valid())
    assert response.status_code == 201
    assert response.json == {'id': 123}
    form = create.call_args.args[0]
    assert form.birthdate.data.isoformat() == '2000-01-02'
    assert form.is_sputnik.data is False
    assert create.call_args.kwargs == {'author': 42}


@pytest.mark.parametrize('token', ['', 'wrong', 'секрет'])
def test_bad_auth(api, token):
    _, client, create, unlocked = api
    assert post(client, valid(), token).status_code == 401
    create.assert_not_called()
    unlocked.assert_not_called()


@pytest.mark.parametrize('setting,value', [('PLAYER_API_TOKEN', '')])
def test_disabled(api, setting, value):
    app, client, create, _ = api
    app.config[setting] = value
    assert post(client, valid()).status_code == 503
    create.assert_not_called()


@pytest.mark.parametrize('changes', [dict(lastname='  '), dict(city='999'), dict(sex='2'),
                                   dict(birthdate='bad'), dict(is_sputnik='false'),
                                   dict(notes='x' * 256), dict(author=1), dict(firstname=[] )])
def test_invalid_fields(api, changes):
    _, client, create, _ = api
    assert post(client, valid() | changes).status_code == 400
    create.assert_not_called()


@pytest.mark.parametrize('author', [None, 0, -1, '42', True, 1.5, [], {}])
def test_invalid_author(api, author):
    _, client, create, _ = api
    payload = valid()
    if author is None:
        payload.pop('author_id')
    else:
        payload['author_id'] = author
    response = post(client, payload)
    assert response.status_code == 400
    assert 'author_id' in response.json['fields']
    create.assert_not_called()


def test_author_from_request(api):
    _, client, create, _ = api
    assert post(client, valid() | {'author_id': 73}).status_code == 201
    assert create.call_args.kwargs == {'author': 73}


def test_bad_body(api):
    _, client, create, _ = api
    headers = {'Authorization': 'Bearer test-secret'}
    assert client.post('/api/players/', data='x', headers=headers).status_code == 415
    assert client.post('/api/players/', data='{', content_type='application/json', headers=headers).status_code == 400
    assert post(client, []).status_code == 400
    create.assert_not_called()


@pytest.mark.parametrize('encoding,status', [('utf-8', 201), ('cp1251', 400)])
def test_json_encoding(api, encoding, status):
    _, client, create, unlocked = api
    response = client.post(
        '/api/players/',
        data=json.dumps(valid(), ensure_ascii=False).encode(encoding),
        content_type='application/json',
        headers={'Authorization': 'Bearer test-secret'},
    )
    assert response.status_code == status
    if status == 400:
        assert response.json['error'] == 'invalid_encoding'
        create.assert_not_called()
        unlocked.assert_not_called()
    else:
        assert create.call_args.args[0].lastname.data == 'Иванов'


def test_locked_and_failure(api):
    _, client, create, unlocked = api
    unlocked.return_value = False
    assert post(client, valid()).status_code == 503
    create.assert_not_called()
    unlocked.return_value = True
    create.return_value = -1
    assert post(client, valid()).status_code == 500


def test_explicit_author_without_login(monkeypatch):
    from src import players
    base = Mock()
    base.addNewPlayer.return_value = 123
    context = Mock()
    context.__enter__ = Mock(return_value=base)
    context.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(players, 'BaseIFace', Mock(return_value=context))
    app = Flask(__name__)
    with app.test_request_context():
        from src.forms import AddPlayer
        form = AddPlayer(data=valid(), meta={'csrf': False})
        assert addPlayer(form, author=42) == 123
    assert base.addNewPlayer.call_args.args[1] == 42
