from flask import Flask, Response, render_template, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from src.players import *
from src.tournaments import *
from src.rate import *
from src.service import *
import lxml.etree as et
import time

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/players/<int:player_id>/')
@app.route('/players/<int:player_id>/xml/')
def player_xml(player_id):
    start_time = time.perf_counter()
    res = getPlayerXml(player_id)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/players/<name>/')
def player_find(name: str):
    return render_template('find.htm', players=findPlayer(name))


@app.route('/players/')
def players_form():
    return "Show user form"


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


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run(debug=True)
