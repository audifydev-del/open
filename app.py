from flask import Flask, jsonify, request
from flask_cors import CORS
import yt_dlp
import os

# This helps find audio tools on cloud servers like Render
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)  # Allows your HTML to talk to this Python backend

@app.route('/')
def home():
    return "Audify Backend is Running!"

@app.route('/get_audio/<video_id>')
def get_audio(video_id):
    # These settings are optimized for 2GB RAM and Cloud Hosting
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt',  # Uses the file you just uploaded
        'source_address': '0.0.0.0',
        'nocheckcertificate': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(video_url, download=False)
            
            # This returns the direct audio stream URL to your HTML
            return jsonify({
                "status": "success",
                "url": info['url'],
                "title": info.get('title', 'Unknown Title')
            })
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
