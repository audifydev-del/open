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
    query = request.args.get('q', 'trending songs')
    try:
        yt = YTMusic()
        results = yt.search(query, filter="songs")
        songs = []
        for s in results[:15]:
            # Get the highest res thumbnail
            thumb = s['thumbnails'][-1]['url'] if s.get('thumbnails') else ""
            songs.append({
                "title": s['title'],
                "artist": s['artists'][0]['name'] if s.get('artists') else "Unknown",
                "thumbnail": thumb,
                "id": s['videoId']
            })
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "No ID provided"}), 400
        
    # ba/wa is Best Audio or Worst Audio (saves RAM on your 2GB device)
    ydl_opts = {
        'format': 'ba/wa', 
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            if 'url' in info:
                return jsonify({"url": info['url']})
            else:
                return jsonify({"error": "No stream URL found"}), 500
    except Exception as e:
        print(f"Stream Error: {str(e)}") # This shows in your Render logs
        return jsonify({"error": "Stream failed", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
