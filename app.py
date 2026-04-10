from flask import Flask, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/wahis')
def proxy_wahis():
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    year_start = datetime(now.year, 1, 1)

    end_str   = now.strftime('%Y-%m-%d')
    week_str  = week_ago.strftime('%Y-%m-%d')
    year_str  = year_start.strftime('%Y-%m-%d')

    payload = {
        "startDate": year_str,
        "endDate": end_str,
        "page": 0,
        "pageSize": 500
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://wahis.woah.org",
        "Referer": "https://wahis.woah.org/"
    }

    try:
        r = requests.post(
            'https://wahis.woah.org/api/v1/public/event/outbreaks',
            json=payload,
            headers=headers,
            timeout=20
        )
        resp = app.response_class(
            response=r.content,
            status=r.status_code,
            mimetype='application/json'
        )
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/test')
def test():
    return {'status': 'ok', 'message': 'VIGIA proxy activo'}

if __name__ == '__main__':
    app.run()
