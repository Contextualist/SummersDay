import requests
from flask import Flask, jsonify, render_template, request
from time import sleep
from traceback import format_exc

app = Flask(__name__)

ks = ("a0a15f16-6071-4af8-aa17-960a6351bd2c",
      "pCgloEerxjKEuMc0sj0828dVQJpiwQpGU1BQ"
      "UbrGPJlNLlQKgmpAUyCUTRcPbL0J")
import re
ippattern = re.compile(r'\-'.join([r'(2(5[0-5]|[0-4]\d)|1?\d\d)'] * 4))

cid = ''

def _fetch_json(url):
    return requests.get('https://app.arukas.io/api' + url, auth=ks).json()
def _post(url, data=None):
    requests.post('https://app.arukas.io/api' + url, auth=ks, data=data)
def _delete(url):
    requests.delete('https://app.arukas.io/api' + url, auth=ks)

def get_container():
    containers = _fetch_json('/containers')
    for c in containers:
        if c['attributes']['image_name'] == 'contextualist/summer-session':
            return c

def check_status():
    attr = get_container()['attributes']
    rv = {}
    if attr['is_running']:
        rv['ip'] = '.'.join(ippattern.search(attr['port_mapping']['host']).group().split('-'))
        rv['port'] = str(attr['port_mapping']['service_port'])
    else:
        rv['ip'] = '-.-.-.-'
        rv['port'] = '-'
    rv['status'] = attr['status_text']
    return rv

@app.route('/api/start')
def start():
    s = check_status()
    if s['status'] != 'running':
        _post('/containers/{cid}/power'.format(cid=cid))
        while s['status'] != 'running':
            sleep(5000)
            s = check_status()
    return jsonify(**s)
    
@app.route('/api/stop')
def stop():
    s = check_status()
    if s['status'] == 'running':
        _delete('/containers/{cid}/power'.format(cid=cid))
        while s['status'] == 'running':
            sleep(5000)
            s = check_status()
    return jsonify(**s)

@app.route('/api/refresh')
def refresh():
    return jsonify(**check_status())

@app.route('/')
def index():
    cid = get_container()['id']
    return render_template('index.html')

@app.errorhandler(Exception)
def handle_exception(e):
    tb = format_exc()
    return "<pre>%s</pre>" % tb, getattr(e, 'code', 500)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
