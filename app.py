import os
from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Lee variables de entorno
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
REFRESH_TOKEN = os.getenv("SPOTIPY_REFRESH_TOKEN")
ALEXA_SECRET_KEY = os.environ.get("ALEXA_SECRET_KEY")

# Usa un auth manager temporal, solo para refrescar el token
def get_spotify_client():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )

    # Refresca token usando el refresh_token
    token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
    access_token = token_info["access_token"]

    return spotipy.Spotify(auth=access_token)

@app.route('/')
def home():
    return 'API de Música PC activa con seguridad 🔐'

@app.route('/play', methods=['POST'])
def play():
    # Verifica la llave secreta
    received_key = request.headers.get('x-alexa-key')
    if received_key != ALEXA_SECRET_KEY:
        abort(403, description="Clave inválida")

    data = request.get_json()
    song = data.get('song', '')

    sp = get_spotify_client()

    # Buscar canción
    results = sp.search(q=song, limit=1, type='track')
    tracks = results.get('tracks', {}).get('items', [])

    if not tracks:
        return jsonify({'error': 'Canción no encontrada'}), 404

    track_uri = tracks[0]['uri']

    # Obtener dispositivo y reproducir
    devices = sp.devices()['devices']
    if not devices:
        return jsonify({'error': 'No hay dispositivos activos'}), 400

    device_id = devices[0]['id']
    sp.start_playback(device_id=device_id, uris=[track_uri])

    return jsonify({'status': 'playing', 'song': song})

if __name__ == "__main__":
    app.run(debug=True)
