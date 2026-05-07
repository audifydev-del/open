import os
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__, template_folder='.')

# --- v1.12.0 Implementation ---
# To use the API you linked correctly, we initialize with oauth.json 
# This is what allows you to bypass restrictions on "Official Audio"
try:
    if os.path.exists('oauth.json'):
        # This uses the authenticated session you mentioned
        yt = YTMusic('oauth.json')
        print("v1.12.0: Authenticated session loaded.")
    else:
        # Fallback to guest if you haven't uploaded the json yet
        yt = YTMusic()
        print("v1.12.0: Running as Guest (Some audio may be blocked).")
except Exception as e:
    print(f"Init Error: {e}")
    yt = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query or not yt:
        return jsonify([])

    try:
        # Using the v1.12.0 search method with the songs filter
        # This specifically targets 'Official Audio' Topic tracks
        search_results = yt.search(query, filter="songs")
        
        songs = []
        for item in search_results:
            # v1.12.0 returns videoId, title, and artist arrays
            video_id = item.get('videoId')
            if not video_id:
                continue

            songs.append({
                'id': video_id,
                'title': item.get('title'),
                'artist': item['artists'][0]['name'] if item.get('artists') else 'Unknown',
                'album': item.get('album', {}).get('name', 'Single'),
                'thumbnail': item['thumbnails'][-1]['url'] if item.get('thumbnails') else '',
                'duration': item.get('duration')
            })
        
        return jsonify(songs)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500

# This is the feature you found in the repo! 
# Adding a song to a playlist via the API.
@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    data = request.json
    playlist_id = data.get('playlistId')
    video_id = data.get('videoId')
    
    if yt and playlist_id and video_id:
        try:
            # Exact method from the repo docs you found
            response = yt.add_playlist_items(playlist_id, [video_id])
            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Missing data"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
