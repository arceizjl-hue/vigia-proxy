from flask import Flask
import requests
import json
import re

app = Flask(__name__)

@app.route('/wahis')
def proxy_promed():
    url = 'https://promedmail.org/promed-posts/feed/'
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'VIGIA/1.0'})
        text = r.text

        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', text)
        dates  = re.findall(r'<pubDate>(.*?)</pubDate>', text)
        links  = re.findall(r'<link>(.*?)</link>', text)

        # quitar primeros (son del canal, no de posts)
        titles = titles[1:] if len(titles) > 1 else titles
        links  = links[1:]  if len(links)  > 1 else links
        dates  = dates[1:]  if len(dates)  > 1 else dates

        items = []
        for i in range(min(len(titles), 80)):
            items.append({
                'title': titles[i] if i < len(titles) else '',
                'date':  dates[i]  if i < len(dates)  else '',
                'link':  links[i]  if i < len(links)  else ''
            })

        resp = app.response_class(
            response=json.dumps({'source': 'ProMED', 'data': items}),
            status=200,
            mimetype='application/json'
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
