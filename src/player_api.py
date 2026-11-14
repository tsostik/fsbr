import hmac

from flask import Blueprint, current_app, jsonify, request
from werkzeug.datastructures import MultiDict

from src.db import getCities
from src.forms import AddPlayer
from src.players import addPlayer
from src.users import base_unlocked


player_api = Blueprint('player_api', __name__)


@player_api.post('/api/players/')
def create_player():
    token = current_app.config.get('PLAYER_API_TOKEN', '')
    if not token:
        return jsonify(error='api_not_configured'), 503

    scheme, _, supplied = request.headers.get('Authorization', '').partition(' ')
    if scheme.lower() != 'bearer' or not hmac.compare_digest(
            supplied.encode('utf-8'), token.encode('utf-8')):
        response = jsonify(error='unauthorized')
        response.headers['WWW-Authenticate'] = 'Bearer'
        return response, 401

    if not request.is_json:
        return jsonify(error='json_required'), 415
    try:
        request.get_data().decode('utf-8')
    except UnicodeDecodeError:
        return jsonify(error='invalid_encoding', message='JSON body must be encoded as UTF-8.'), 400
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='invalid_json'), 400

    fields = {'lastname', 'firstname', 'fathername', 'sex', 'city',
              'birthdate', 'is_sputnik', 'sputnik_first', 'notes', 'author_id'}
    errors = {}
    author = payload.get('author_id')
    if type(author) is not int or author <= 0:
        errors['author_id'] = ['Required positive integer.']
    for key, value in payload.items():
        if key not in fields:
            errors[key] = ['Unknown field.']
        elif key == 'author_id':
            continue
        elif key == 'is_sputnik':
            if not isinstance(value, bool):
                errors[key] = ['Expected a boolean.']
        elif not isinstance(value, str):
            errors[key] = ['Expected a string.']
    for key in ('lastname', 'firstname'):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            errors[key] = ['Required non-empty string.']
    if errors:
        return jsonify(error='validation_failed', fields=errors), 400

    data = {key: value for key, value in payload.items() if key not in ('is_sputnik', 'author_id')}
    data['notes'] = f'External API creation\n{data.get("notes", "")}'
    if payload.get('is_sputnik', False):
        data['is_sputnik'] = 'y'
    # Only this token-authenticated form skips CSRF; browser forms retain it.
    form = AddPlayer(formdata=MultiDict(data), meta={'csrf': False})
    form.city.choices = [(str(value), name) for name, value in getCities().items()]
    if not form.validate():
        return jsonify(error='validation_failed', fields=form.errors), 400
    if not base_unlocked():
        return jsonify(error='database_locked'), 503
    result = addPlayer(form, author=author)
    if result <= 0:
        return jsonify(error='player_creation_failed'), 500
    return jsonify(id=result), 201
