from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic
import os

app = Flask(__name__, template_folder='.')

# Initialize YTMusic once to save memory
yt = YTMusic()

@app.route('/')
def index():
    # Serves your index.html from the root directory
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', 'trending songs')
    try:
        # Search for songs specifically
        results = yt.search(query, filter="songs")
        songs = []
        
        for s in results[:15]:
            try:
                # Get the raw thumbnail URL from the last (largest) item in the list
                raw_thumb = s['thumbnails'][-1]['url'] if s.get('thumbnails') else ""
                
                # Logic to force High Definition (544x544)
                if "=" in raw_thumb:
                    # Strips the low-res size and adds the HD parameter
                    high_res_thumb = raw_thumb.split('=')[0] + "=w544-h544-l90-rj"
                else:
                    high_res_thumb = raw_thumb

                songs.append({
                    "title": s['title'],
                    "artist": s['artists'][0]['name'] if s.get('artists') else "Unknown",
                    "thumbnail": high_res_thumb,
                    "id": s['videoId']
                })
            except Exception:
                continue # Skip any song that has broken data
                
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render requires the app to run on a specific port provided by the environment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
