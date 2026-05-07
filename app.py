from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic
import yt_dlp
import os

app = Flask(__name__, template_folder='.')

# Initialize YTMusic
# Note: If you face issues on Render, you might need to use a pre-authenticated 
# headers_auth.json file, but for basic search, this works fine.
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
                # Thumbnail HD Logic
                raw_thumb = s['thumbnails'][-1]['url'] if s.get('thumbnails') else ""
                if "=" in raw_thumb:
                    high_res_thumb = raw_thumb.split('=')[0] + "=w544-h544-l90-rj"
                else:
                    high_res_thumb = raw_thumb

                songs.append({
                    "title": s['title'],
                    "artist": s['artists'][0]['name'] if s.get('artists') else "Unknown",
                    "thumbnail": high_res_thumb,
                    "videoId": s['videoId'] # Renamed to videoId for JS consistency
                })
            except Exception:
                continue 
                
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_audio/<video_id>')
def get_audio(video_id):
    """
    This route extracts the direct audio-only stream URL.
    This is much more stable than an iframe embed.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        # Render's disk is read-only in many spots, so we ensure no files are written
        'skip_download': True, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # Returns the direct URL to the .m4a or .webm audio stream
            return jsonify({"url": info['url']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Local development settings
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
