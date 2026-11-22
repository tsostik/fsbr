import hmac

from flask import Blueprint, current_app, jsonify, request
from werkzeug.datastructures import MultiDict

from src.db import getCities
from src.forms import AddPlayer
from src.players import addPlayer, findPlayer
from src.users import base_unlocked


player_api = Blueprint('player_api', __name__)


def check_authorization(request):
    token = current_app.config.get('PLAYER_API_TOKEN', '')
    if not token:
        raise Exception('API not configured')

    scheme, _, supplied = request.headers.get('Authorization', '').partition(' ')
    return scheme.lower() == 'bearer' and hmac.compare_digest(
            supplied.encode('utf-8'), token.encode('utf-8')
    )



@player_api.post('/api/addplayer/')
def create_player():
    try:
        if not check_authorization(request):
            response = jsonify(error='unauthorized')
            response.headers['WWW-Authenticate'] = 'Bearer'
            return response, 401
    except Exception as e:
        return jsonify(error=str(e)), 503

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


@player_api.route('/api/findplayer/', methods=['GET', 'POST'])
@player_api.get('/api/findplayer/<name>')
def find_player(name=None):
    if request.method == 'POST':
        if not request.is_json:
            return jsonify(error='json_required'), 415
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error='invalid_json'), 400
        name = data.get('surname', '')
        newonly = data.get('newonly', False)
    else:
        name = name if name is not None else request.args.get('surname', '')
        newonly = request.args.get('newonly', 'false')
        if 'newonly' in request.args and newonly == '':
            newonly = True

    if not isinstance(name, str):
        return jsonify(error='validation_failed', fields={'surname': ['Expected a string.']}), 400
    if isinstance(newonly, bool):
        pass
    elif isinstance(newonly, str) and newonly.lower() in ('1', 'true', '0', 'false', ''):
        newonly = newonly.lower() in ('1', 'true')
    elif type(newonly) is int and newonly in (0, 1):
        newonly = bool(newonly)
    else:
        return jsonify(error='validation_failed', fields={'newonly': ['Expected a boolean.']}), 400

    name = name.strip()
    players = findPlayer(name) if name else None
    if newonly:
        players = [player for player in players if player[-1] == 1] if players else []
    return jsonify(players), 201 if players else 404
