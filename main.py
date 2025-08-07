from flask import Flask, request, jsonify

app = Flask(__name__)

# URL base estática
URL_BASE = "https://app.chatgptbuilder.io/webchat/?p=1296809&ref=CanjearMembresia--"

@app.route('/generate-url', methods=['POST'])
def generate_url():
    # Obtiene el ID dinámico del cuerpo de la solicitud
    data = request.get_json()
    dynamic_id = data.get('id')

    # Verifica si el ID fue proporcionado
    if not dynamic_id:
        return jsonify({"error": "ID missing from request"}), 400

    # Construye la URL completa
    complete_url = f"{URL_BASE}{dynamic_id}"

    # Devuelve la URL completa en formato JSON
    return jsonify({"url": complete_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
