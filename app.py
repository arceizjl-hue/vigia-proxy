from flask import Flask, request, jsonify # 'from' en minúscula
import requests

app = Flask(__name__)

FUENTES = {
    'wahis': 'https://wahis.woah.org/api/v1/public/event/outbreaks',
}

@app.route('/')
def home():
    return {"status": "Vigía Proxy Online", "fuentes": list(FUENTES.keys())}

@app.route('/<fuente>')
def proxy(fuente):
    target_url = FUENTES.get(fuente)
    if not target_url:
        return jsonify({'error': 'fuente no encontrada'}), 404
    
    # Cabeceras para engañar al servidor de WAHIS y que crea que somos un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://wahis.woah.org/'
    }

    try:
        # Pasamos los parámetros que vienen del HTML (startDate, endDate, etc.)
        r = requests.get(target_url, params=request.args, headers=headers, timeout=20)
        
        # Creamos la respuesta con CORS permitido para que tu HTML pueda leerlo
        response = app.response_class(
            response=r.content,
            status=r.status_code,
            mimetype='application/json'
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Importante: Render usa la variable de entorno PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
