import os
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

# Tell Flask to look in the current directory ('.') for HTML files
app = Flask(__name__, template_folder='.')

yt = YTMusic()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    try:
        results = yt.search(query, filter="songs")
        songs = []
        for item in results:
            songs.append({
                'id': item['videoId'],
                'title': item['title'],
                'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                'thumbnail': item['thumbnails'][-1]['url']
            })
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
