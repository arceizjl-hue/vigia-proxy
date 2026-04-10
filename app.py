
from flask import Flask, request
import requests

app = Flask(__name__)

FUENTES = {
    'wahis': 'https://wahis.woah.org/api/v1/public/event/outbreaks',
}

@app.route('/<fuente>')
def proxy(fuente):
    url = FUENTES.get(fuente)
    if not url:
        return {'error': 'fuente no encontrada'}, 404
    try:
        r = requests.get(url, params=request.args, timeout=15)
        resp = app.response_class(
            response=r.content,
            status=r.status_code,
            mimetype='application/json'
        )
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run()
