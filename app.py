import os
import json
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

# Initialize Flask
# We tell it to look in the current directory ('.') for index.html
app = Flask(__name__, template_folder='.')

# --- YTMusic Initialization ---
# This checks for 'oauth.json' first. 
# If it doesn't exist, it falls back to guest mode (no login).
try:
    if os.path.exists('oauth.json'):
        yt = YTMusic('oauth.json')
        print("Initialized YTMusic with OAuth")
    else:
        yt = YTMusic()
        print("Initialized YTMusic as Guest")
except Exception as e:
    print(f"Critical Init Error: {e}")
    yt = None

@app.route('/')
def index():
    """Serves the main Spotify-style interface."""
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    """Handles search queries from the frontend."""
    query = request.args.get('q')
    if not query:
        return jsonify([])

    if yt is None:
        return jsonify({"error": "YTMusic API is not initialized"}), 500

    try:
        # filter="songs" ensures we get 'Official Audio' (Topic tracks)
        # instead of fan-made videos or music videos.
        search_results = yt.search(query, filter="songs")
        
        parsed_songs = []
        for item in search_results:
            # Skip items that don't have a videoId (prevents crashes)
            video_id = item.get('videoId')
            if not video_id:
                continue

            # Safely extract artist name
            artist_name = "Unknown Artist"
            if item.get('artists'):
                artist_name = item['artists'][0]['name']

            # Safely extract thumbnail
            thumb = ""
            if item.get('thumbnails'):
                thumb = item['thumbnails'][-1]['url']

            parsed_songs.append({
                'id': video_id,
                'title': item.get('title', 'Unknown Title'),
                'artist': artist_name,
                'album': item.get('album', {}).get('name', 'Single'),
                'thumbnail': thumb,
                'duration': item.get('duration', '0:00')
            })

        return jsonify(parsed_songs)

    except Exception as e:
        print(f"Search error for query '{query}': {e}")
        return jsonify({"error": "Failed to fetch search results"}), 500

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    """Example of how you'd use that code you found (Requires OAuth)."""
    if not os.path.exists('oauth.json'):
        return jsonify({"error": "OAuth login required for this feature"}), 403
    
    data = request.json
    name = data.get('name', 'New Playlist')
    desc = data.get('description', 'Created via My Music App')
    
    try:
        playlist_id = yt.create_playlist(name, desc)
        return jsonify({"status": "success", "playlistId": playlist_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use port 5000 for local development
    # Render will automatically use its own port via Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
