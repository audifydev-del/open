from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic
import yt_dlp
import os

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', 'trending songs') # Default search
    try:
        yt = YTMusic()
        results = yt.search(query, filter="songs")
        songs = []
        for s in results[:15]:
            songs.append({
                "title": s['title'],
                "artist": s['artists'][0]['name'],
                "thumbnail": s['thumbnails'][-1]['url'], # Best quality thumb
                "id": s['videoId']
            })
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    # Best for 2GB RAM: lower bitrate audio to prevent crashing
    ydl_opts = {'format': 'wa', 'quiet': True} 
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return jsonify({"url": info['url']})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
