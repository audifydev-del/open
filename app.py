import os
from flask import Flask, render_template, request, jsonify
from innertube import InnerTube

app = Flask(__name__, template_folder='.')

# Initialize the client for YouTube Music
client = InnerTube("WEB_REMIX")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    try:
        # Search using InnerTube
        data = client.search(query)
        
        # Navigate to the song results
        # We target the 'musicShelfRenderer' specifically
        sections = data['contents']['tabbedContentRenderer']['tabs'][0]['content']['sectionListRenderer']['contents']
        
        results = []
        for section in sections:
            if 'musicShelfRenderer' in section:
                results = section['musicShelfRenderer']['contents']
                break
        
        songs = []
        for item in results:
            if 'musicTwoColumnItemRenderer' in item:
                track = item['musicTwoColumnItemRenderer']
                video_id = track['navigationEndpoint']['watchEndpoint']['videoId']
                
                songs.append({
                    'id': video_id,
                    'title': track['title']['runs'][0]['text'],
                    'artist': track['subtitle']['runs'][0]['text'],
                    'thumbnail': track['thumbnail']['thumbnails'][-1]['url']
                })
        return jsonify(songs)
    except Exception as e:
        print(f"Search Error: {e}")
        return jsonify([])

@app.route('/get_audio', methods=['GET'])
def get_audio():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "No ID"})

    try:
        player_data = client.player(video_id)
        streaming_data = player_data.get('streamingData', {})
        formats = streaming_data.get('adaptiveFormats', [])
        
        # Get the best audio-only stream
        audio_url = ""
        for fmt in formats:
            if "audio" in fmt.get('mimeType', ''):
                audio_url = fmt.get('url')
                if audio_url: break
                
        return jsonify({"url": audio_url})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
