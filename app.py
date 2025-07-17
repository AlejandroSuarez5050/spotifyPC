from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)

# Configura tus credenciales de Spotify aquí
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

SCOPE = "user-read-playback-state,user-modify-playback-state"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

@app.route('/play', methods=['POST'])
def play():
    data = request.get_json()
    song = data.get('song', '')

    # Autenticación con token (esto usa un token ya guardado en cache)
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    # Buscar la canción
    results = sp.search(q=song, limit=1, type='track')
    tracks = results.get('tracks', {}).get('items', [])

    if not tracks:
        return jsonify({'error': 'Canción no encontrada'}), 404

    track_uri = tracks[0]['uri']

    # Obtener dispositivos
    devices = sp.devices()['devices']
    if not devices:
        return jsonify({'error': 'No hay dispositivos activos'}), 400

    device_id = devices[0]['id']

    # Iniciar reproducción
    sp.start_playback(device_id=device_id, uris=[track_uri])

    return jsonify({'status': 'playing', 'song': song})

@app.route('/')
def home():
    return 'API de Música PC está activa.'

