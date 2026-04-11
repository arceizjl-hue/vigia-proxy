from flask import Flask
import requests
import xml.etree.ElementTree as ET
import re

app = Flask(__name__)

@app.route('/wahis')
def proxy_promed():
    url = 'https://promedmail.org/promed-posts/feed/'
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'VIGIA/1.0'})
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall('.//item')[:100]:
            title = item.findtext('title') or ''
            date  = item.findtext('pubDate') or ''
            link  = item.findtext('link') or ''
            items.append({'title': title, 'date': date, 'link': link})
        resp = app.response_class(
            response=__import__('json').dumps({'source':'ProMED','data':items}),
            status=200, mimetype='application/json'
        )
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/test')
def test():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run()
