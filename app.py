from flask import Flask, redirect, request, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")

# Configuración de Spotify
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "https://spotifypc.onrender.com/callback")
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=None,
    show_dialog=True
)

# Ruta de inicio
@app.route("/")
def home():
    return "🎶 API de Música PC está activa. Visita /login para autorizar."

# Redirige a Spotify
@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Recibe el callback con el código de autorización
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No se recibió código", 400

    token_info = sp_oauth.get_access_token(code, as_dict=True)
    session["token_info"] = token_info
    return "✅ Login exitoso. Ya puedes usar /play"

# Devuelve una instancia de Spotify autenticada
def get_spotify():
    token_info = session.get("token_info")
    if not token_info:
        return None

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    return spotipy.Spotify(auth=token_info["access_token"])

# Reproduce una canción
@app.route("/play", methods=["POST"])
def play():
    sp = get_spotify()
    if not sp:
        return redirect("/login")

    data = request.get_json()
    song = data.get("song")
    if not song:
        return jsonify({"error": "Debes enviar 'song' en el cuerpo del JSON"}), 400

    results = sp.search(q=song, limit=1, type='track')
    tracks = results.get("tracks", {}).get("items", [])

    if not tracks:
        return jsonify({"error": "Canción no encontrada"}), 404

    track_uri = tracks[0]["uri"]

    devices = sp.devices().get("devices", [])
    if not devices:
        return jsonify({"error": "No hay dispositivos activos"}), 400

    sp.start_playback(device_id=devices[0]["id"], uris=[track_uri])

    return jsonify({"status": "Reproduciendo", "track": tracks[0]["name"]})


# Debug endpoint opcional
@app.route("/me")
def me():
    sp = get_spotify()
    if not sp:
        return redirect("/login")
    user = sp.me()
    return jsonify(user)