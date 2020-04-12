from flask import Flask, Response, render_template, url_for, jsonify, request, session, flash, redirect
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_script import Manager
from werkzeug.middleware.proxy_fix import ProxyFix

from src.players import addPlayer, findPlayer, getPlayerXml, getPlayerInfoJSON
from src.rate import getFullList, getRate, getRateForecast
from src.service import getRateTourns, getRazrChange, getClubStat
from src.tournaments import getCities, getTournamentList, getTournamentXml
from src.users import User, db as db_users, find_or_add_user, has_permission

from src.forms import AddPlayer
from src.oauth import OAuthSignIn

import datetime
import lxml.etree as et
import time

app = Flask(__name__)
app.config.from_object('defaults')
app.config.from_object('settings')

db_users.init_app(app)
lm = LoginManager(app)
manager = Manager(app)
HTMLMIN(app)


# блок для работы flask_script
@manager.command
def initdatabase():
    import src.users
    src.users.db.create_all()


# Эта функция нужна для корректной работы LoginManager
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Определяем дополнительные функции доступные в кондексте Jinja2
@app.context_processor
def utility_processor():
    return dict(has_permission=has_permission)


@app.route('/')
def index():
    return render_template("index.htm")


@app.route('/authorize/<provider>/')
def oauth_authorize(provider):
    redirect_url = request.args['next'] if 'next' in request.args else url_for(index)
    if not current_user.is_anonymous:
        return redirect(redirect_url)
    session['next'] = redirect_url
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>/')
def oauth_callback(provider):
    redirect_url = session.get('next') if 'next' in session else url_for(index)
    if not current_user.is_anonymous:
        return redirect(redirect_url)
    oauth = OAuthSignIn.get_provider(provider)
    user_info = oauth.callback()
    if user_info is None:
        flash('Authentication failed.')
        return redirect(redirect_url)
    user = find_or_add_user(user_info)
    login_user(user, True)
    if 'next' in session:
        session.pop('next', None)
    return redirect(redirect_url)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/players/', methods=['post', 'get'])
@app.route('/players/<name>/')
def find_player(name: str = None):
    if request.form.get('name'):
        return redirect(url_for('find_player', name=request.form.get('name'), _method='GET'))
    return render_template('find.htm', name=name, players=findPlayer(name) if name else None)


@app.route('/players/add/', methods=['post', 'get'])
@login_required
def add_player():
    answer = None
    form = AddPlayer()
    form.city.choices = [(str(v), k) for k, v in getCities().items()]
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('validate_on_submit failed')
            flash(str(form.errors))
        else:
            result = addPlayer(form)
            if result > 0:
                flash('Игрок успешно добавлен. Новый ID: ' + str(result))
                answer = redirect(url_for('index'))
            else:
                flash('Неожиданная ошибка при добавлении игрока')
    return answer or render_template('addplayer.htm', form=form)


# маршруты для бэкенда rest api TODO вынести в отдельный файл
@app.route('/players/<int:player_id>/')
@app.route('/players/<int:player_id>/xml/')
def player_xml(player_id):
    start_time = time.perf_counter()
    res = getPlayerXml(player_id)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/players/<int:player_id>/info/')
def player_info(player_id):
    res = getPlayerInfoJSON(player_id)
    resp = jsonify(res)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/tourns/rate/')
@app.route('/tourns/rate/<int:year>/')
@app.route('/rate/tourns/')
@app.route('/rate/tourns/<int:year>/')
@app.route('/tourns/rate/xml/')
@app.route('/tourns/rate/<int:year>/xml/')
@app.route('/rate/tourns/xml/')
@app.route('/rate/tourns/<int:year>/xml/')
def rate_tournaments(year: int = 0):
    start_time = time.perf_counter()
    res = getRateTourns(year)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/tourns/<int:tournament_id>/')
@app.route('/tourns/<int:tournament_id>/xml/')
def tournament_xml(tournament_id):
    start_time = time.perf_counter()
    res = getTournamentXml(tournament_id)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/tourns/')
@app.route('/tourns/xml/')
def tournament_list_xml():
    start_time = time.perf_counter()
    res = getTournamentList()
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/rate/fulllist/')
@app.route('/rate/fulllist/xml/')
def fullList_xml():
    start_time = time.perf_counter()
    res = getFullList()
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/rate/')
@app.route('/rate/xml/')
@app.route('/rate/<rdate>/')
@app.route('/rate/<rdate>/xml/')
def rate_xml(rdate: str = None):
    start_time = time.perf_counter()
    if rdate is None:
        dt = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    else:
        try:
            dt = datetime.datetime.strptime(rdate, '%Y-%m-%d').date()
        except ValueError:
            dt = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    res = getRate(dt)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/rate/forecast/')
@app.route('/rate/forecast/xml/')
def rate_forecast_xml():
    start_time = time.perf_counter()
    res = getRateForecast()
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/misc/razrchange/')
@app.route('/misc/razrchange/xml/')
@app.route('/misc/razrchange/<date>/')
@app.route('/misc/razrchange/<date>/xml/')
def razr_change(date: str = None):
    start_time = time.perf_counter()
    if date is None:
        dt = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    else:
        try:
            dt = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            dt = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    res = getRazrChange(dt)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/misc/clubs/')
@app.route('/misc/clubs/xml/')
def clubs():
    start_time = time.perf_counter()
    res = getClubStat()
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    manager.run()
