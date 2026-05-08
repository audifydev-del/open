from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__)
ytmusic = YTMusic()

@app.route('/')
def index():
    # This serves your HTML file
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    # Search for songs on YT Music
    search_results = ytmusic.search(query, filter="songs")
    
    # Simplify the results for the frontend
    songs = []
    for result in search_results:
        songs.append({
            'id': result['videoId'],
            'title': result['title'],
            'artist': result['artists'][0]['name'] if result['artists'] else 'Unknown',
            'thumbnail': result['thumbnails'][-1]['url']
        })
    
    return jsonify(songs)

if __name__ == '__main__':
    app.run(debug=True)
