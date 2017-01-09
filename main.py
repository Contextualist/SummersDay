import requests
from flask import Flask, jsonify, render_template, request
from os import environ as env
from time import time
from traceback import format_exc

app = Flask(__name__)

KS = (env['key'], env['secret'])
IMAGE = 'contextualist/summer-session'
import re
ippattern = re.compile(r'\-'.join([r'(2(5[0-5]|[0-4]\d)|1?\d\d)'] * 4))

cid = app_id = ''

def _fetch_json(url):
    return requests.get('https://app.arukas.io/api' + url, auth=KS).json()
def _post(url, json_data=None):
    requests.post('https://app.arukas.io/api' + url, auth=KS, json=json_data)
def _delete(url):
    requests.delete('https://app.arukas.io/api' + url, auth=KS)

def get_container():
    global c_id, app_id
    containers = _fetch_json('/containers')['data']
    for c in containers:
        if c['attributes']['image_name'] == IMAGE:
            c_id, app_id = c['id'], c['attributes']['app_id']
            return c

def check_status():
    attr = get_container()['attributes']
    if attr is None:
        attr = {'is_running': False,
                'status_text': 'container not found'}
    rv = {}
    if attr['is_running']:
        rv['ip'] = '.'.join(ippattern.search(attr['port_mappings'][0][0]['host']).group().split('-'))
        rv['port'] = str(attr['port_mappings'][0][0]['service_port'])
    else:
        rv['ip'] = '---.---.---.---'
        rv['port'] = '-----'
    rv['status'] = {'booting':'deploying...'}.get(attr['status_text'], attr['status_text'])
    return rv

@app.route('/api/start')
def start():
    if check_status()['status'] == 'stopped':
        _post('/containers/{c_id}/power'.format(c_id=c_id))
    return '', 204
    
@app.route('/api/stop')
def stop():
    if check_status()['status'] != 'stopped':
        _delete('/containers/{c_id}/power'.format(c_id=c_id))
    return '', 204

@app.route('/api/refresh')
def refresh():
    return jsonify(**check_status())

@app.route('/api/renew')
def renew():
    _delete('/apps/{app_id}'.format(app_id=app_id))
    _post('/app-sets', json_data={
            'data': [
              {
                'type': 'containers',
                'attributes': {
                  'image_name': IMAGE,
                  'instances': 1,
                  'mem': 256,
                  'ports': [
                    {
                      'number': 443,
                      'protocol': 'tcp'
                    }
                  ]
                }
              },
              {
                'type': 'apps',
                'attributes': {
                  'name': 'Tc'+str(time())[-6:]
                }
              }
            ]
    })
    return jsonify(status='new container generated')

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(Exception)
def handle_exception(e):
    tb = format_exc()
    return "<pre>%s</pre>" % tb, getattr(e, 'code', 500)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
