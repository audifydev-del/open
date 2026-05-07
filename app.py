import os
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

# Since index.html is in the same folder as app.py
app = Flask(__name__, template_folder='.')

# Initialize without headers for now (public search)
yt = YTMusic()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    try:
        # Get search results
        search_results = yt.search(query, filter="songs")
        songs = []
        
        for item in search_results:
            # We use .get() to avoid "KeyError" if data is missing
            song_id = item.get('videoId')
            if not song_id: continue 

            songs.append({
                'id': song_id,
                'title': item.get('title', 'Unknown Title'),
                'artist': item['artists'][0]['name'] if item.get('artists') else 'Unknown Artist',
                'thumbnail': item['thumbnails'][-1]['url'] if item.get('thumbnails') else ''
            })
        
        return jsonify(songs)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
