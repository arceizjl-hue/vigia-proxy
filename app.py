from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuración de fuentes
FUENTES = {
    'wahis': 'https://wahis.woah.org/api/v1/public/event/outbreaks',
}

@app.route('/')
def home():
    return {
        "status": "Vigía Proxy Online", 
        "info": "Proxy activo para el repositorio WAHIS",
        "rutas_disponibles": ["/wahis"]
    }

@app.route('/<fuente>')
def proxy(fuente):
    target_url = FUENTES.get(fuente)
    if not target_url:
        return jsonify({'error': 'Fuente no configurada en el servidor'}), 404
    
    # 1. Construcción de parámetros exactos para evitar BAD_REQUEST
    # WAHIS a menudo requiere estos campos para procesar la petición GET
    params = {
        'page': request.args.get('page', 0),
        'size': request.args.get('size', 1000),
        'sort': 'reportDate,desc',
        'lang': 'en'
    }
    
    # Añadimos las fechas que vienen de tu archivo HTML
    if request.args.get('startDate'):
        params['startDate'] = request.args.get('startDate')
    if request.args.get('endDate'):
        params['endDate'] = request.args.get('endDate')

    # 2. Cabeceras imprescindibles para saltar el bloqueo de seguridad de WAHIS
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://wahis.woah.org',
        'Referer': 'https://wahis.woah.org/'
    }

    try:
        # Hacemos la petición a la API oficial
        r = requests.get(target_url, params=params, headers=headers, timeout=20)
        
        # Si la API responde con error (como el 400 que viste), 
        # devolvemos ese error pero con las cabeceras CORS para poder leerlo en la consola
        if r.status_code != 200:
            resp_err = jsonify({
                "error_de_fuente": "WAHIS ha rechazado la petición",
                "status_code": r.status_code,
                "detalle": r.text
            })
            resp_err.headers['Access-Control-Allow-Origin'] = '*'
            return resp_err, r.status_code

        # Si todo va bien, devolvemos los datos
        response = app.response_class(
            response=r.content,
            status=r.status_code,
            mimetype='application/json'
        )
        # Esto permite que tu HTML (desde cualquier dominio) lea los datos
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        return jsonify({'error': 'Fallo de conexión en el proxy', 'msj': str(e)}), 500

if __name__ == '__main__':
    # Configuración necesaria para que Render asigne el puerto automáticamente
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
