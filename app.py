import os
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

# Look in current directory for index.html
app = Flask(__name__, template_folder='.')

# Try to initialize. If it fails, the app won't crash but search will show the error.
try:
    yt = YTMusic()
except Exception as e:
    print(f"Init Error: {e}")
    yt = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    if yt is None:
        return jsonify({"error": "YTMusic not initialized"}), 500

    try:
        # filter="songs" is strict; sometimes "results" is better for testing
        results = yt.search(query, filter="songs")
        songs = []
        for item in results:
            # Add a check to ensure 'videoId' exists
            if 'videoId' in item:
                songs.append({
                    'id': item['videoId'],
                    'title': item['title'],
                    'artist': item['artists'][0]['name'] if item.get('artists') else 'Unknown',
                    'thumbnail': item['thumbnails'][-1]['url'] if item.get('thumbnails') else ''
                })
        return jsonify(songs)
    except Exception as e:
        print(f"Search Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # For local testing
    app.run(debug=True)
