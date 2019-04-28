from flask import Flask, Response
from src.players import *
import lxml.etree as ET
import time

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/players/<int:player_id>/')
def player_xml(player_id):
    start_time = time.process_time()
    res = getPlayerXml(player_id)
    res.set('generated', str(time.process_time() - start_time))
    return Response(ET.tostring(res, encoding='unicode', pretty_print=True), mimetype='text/xml')


if __name__ == '__main__':
    app.run(debug=True)
