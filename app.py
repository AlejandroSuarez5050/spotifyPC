import os
from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Lee variables de entorno (carga tus valores reales aquí)
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
REFRESH_TOKEN = os.getenv("SPOTIPY_REFRESH_TOKEN")  # Este lo generas una vez

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

@app.route("/play", methods=["POST"])
def play():
    data = request.get_json()
    song = data.get("song")

    if not song:
        return jsonify({"error": "No song provided"}), 400

    try:
        sp = get_spotify_client()

        results = sp.search(q=song, limit=1, type="track")
        tracks = results.get("tracks", {}).get("items", [])

        if not tracks:
            return jsonify({"error": "No tracks found"}), 404

        track_uri = tracks[0]["uri"]
        sp.start_playback(uris=[track_uri])

        return jsonify({"message": f"Playing {tracks[0]['name']}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
