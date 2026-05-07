import os
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__)

# Initialize YTMusic. 
# Note: If you haven't done 'ytmusicapi oauth' yet, 
# you can initialize without it for public searches: yt = YTMusic()
yt = YTMusic()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    # Search for songs specifically
    results = yt.search(query, filter="songs")
    
    # Simplify the data sent to the frontend
    songs = []
    for item in results:
        songs.append({
            'id': item['videoId'],
            'title': item['title'],
            'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
            'album': item['album']['name'] if item['album'] else '',
            'thumbnail': item['thumbnails'][-1]['url']
        })
    return jsonify(songs)

if __name__ == '__main__':
    app.run(debug=True)
