from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic
import yt_dlp
import os

# Tell Flask to look for HTML files in the current folder (.)
app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    # Now it will find index.html in the parent folder
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    try:
        yt = YTMusic()
        results = yt.search(query, filter="songs")
        songs = []
        for s in results[:10]:
            songs.append({
                "title": s['title'],
                "artist": s['artists'][0]['name'],
                "thumb": s['thumbnails'][0]['url'],
                "id": s['videoId']
            })
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    # Using worstaudio to save RAM on your 2gb device
    ydl_opts = {'format': 'bestaudio/worstaudio', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return jsonify({"url": info['url']})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
