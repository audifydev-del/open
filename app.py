import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # This allows your HTML to talk to the Python backend

# 1. ROOT ROUTE (What you see in your screenshot)
@app.route('/')
def home():
    return "Audify Backend is Running!"

# 2. SEARCH ROUTE
@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch10',
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            results = []
            for entry in info.get('entries', []):
                results.append({
                    'title': entry.get('title'),
                    'artist': entry.get('uploader'),
                    'videoId': entry.get('id'),
                    'thumbnail': entry.get('thumbnail')
                })
            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# 3. GET AUDIO ROUTE (The part giving you the 500 error)
@app.route('/get_audio/<video_id>')
def get_audio(video_id):
    # These options are CRITICAL for Render to work without getting blocked
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        # YouTube blocks headless servers sometimes; this pretends we are a browser
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(url, download=False)
            # Find the actual direct .mp3 / .webm URL
            audio_url = info.get('url')
            
            if audio_url:
                return jsonify({"url": audio_url})
            else:
                return jsonify({"error": "Could not extract audio URL"}), 404
        except Exception as e:
            print(f"CRASH LOG: {str(e)}") # This shows in your Render logs
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render uses the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
