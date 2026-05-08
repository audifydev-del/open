import subprocess
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__)
ytmusic = YTMusic()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    results = ytmusic.search(query, filter="songs")
    songs = [{
        'id': r['videoId'],
        'title': r['title'],
        'artist': r['artists'][0]['name'] if r['artists'] else 'Unknown',
        'thumbnail': r['thumbnails'][-1]['url']
    } for r in results]
    return jsonify(songs)

@app.route('/get_url')
def get_url():
    video_id = request.args.get('id')
    # This uses yt-dlp to get a direct audio-only URL from the video ID
    cmd = f"yt-dlp -g -f bestaudio --get-url https://www.youtube.com/watch?v={video_id}"
    try:
        url = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return jsonify({'url': url})
    except:
        return jsonify({'error': 'Could not get stream URL'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
