import requests
from flask import Flask, jsonify, render_template, request
from time import sleep, clock
from traceback import format_exc

app = Flask(__name__)

KS = ("a0a15f16-6071-4af8-aa17-960a6351bd2c",
      "pCgloEerxjKEuMc0sj0828dVQJpiwQpGU1BQ"
      "UbrGPJlNLlQKgmpAUyCUTRcPbL0J")
IMAGE = 'contextualist/summer-session'
import re
ippattern = re.compile(r'\-'.join([r'(2(5[0-5]|[0-4]\d)|1?\d\d)'] * 4))

cid = app_id = ''

def _fetch_json(url):
    return requests.get('https://app.arukas.io/api' + url, auth=KS).json()
def _post(url, data=None):
    requests.post('https://app.arukas.io/api' + url, auth=KS, data=data)
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
        rv['port'] = '----'
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

@app.route('/api/reboot')
def reboot():
    _delete('/app/{app_id}'.format(app_id=app_id))
    _post('/app-sets', data={
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
                  'name': 'Tc'+str(clock())
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

exec requests.get("https://gist.githubusercontent.com/Contextualist"
                  "/589b59f72becb237de96d9a6a8002c24/raw"
                  "/c39f5ae816fa42d9967c0ec099b81db6379720fb/WakeUp.py").text
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
