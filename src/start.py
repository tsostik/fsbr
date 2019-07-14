from flask import Flask, Response, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from src.players import *
from src.tournaments import *
from src.rate import *
import lxml.etree as et
import time

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/players/<int:player_id>/')
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


@app.route('/tourns/<int:tournament_id>/')
def tournament_xml(tournament_id):
    start_time = time.perf_counter()
    res = getTornamentXml(tournament_id)
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/rate/fulllist/')
def fullList_xml():
    start_time = time.perf_counter()
    res = getFullList()
    res.set('generated', str(time.perf_counter() - start_time))
    return Response(et.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


@app.route('/rate/')
@app.route('/rate/<rdate>/')
def rate_xml(rdate: str=None):
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


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run(debug=True)
