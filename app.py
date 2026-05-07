import os
from flask import Flask, render_template, request, jsonify
from innertube import InnerTube

app = Flask(__name__, template_folder='.')

# Initialize Innertube for YouTube Music
client = InnerTube("WEB_REMIX")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    # Search specifically for songs
    data = client.search(query, params="EgWKAQIIAWoKEAMQBBAJEA4QChAF") # Encoded param for 'Songs'
    
    songs = []
    try:
        # Navigating the messy Innertube JSON response
        results = data['contents']['tabbedContentRenderer']['tabs'][0]['content']['sectionListRenderer']['contents'][0]['musicShelfRenderer']['contents']
        
        for item in results:
            track = item['musicTwoColumnItemRenderer']
            video_id = track['navigationEndpoint']['watchEndpoint']['videoId']
            
            songs.append({
                'id': video_id,
                'title': track['title']['runs'][0]['text'],
                'artist': track['subtitle']['runs'][0]['text'],
                'thumbnail': track['thumbnail']['thumbnails'][-1]['url']
            })
    except Exception as e:
        print(f"Parsing error: {e}")
        
    return jsonify(songs)

@app.route('/get_audio', methods=['GET'])
def get_audio():
    video_id = request.args.get('id')
    # This fetches the streaming data
    player_data = client.player(video_id)
    
    # Find the audio-only stream with the best quality
    streaming_data = player_data.get('streamingData', {})
    formats = streaming_data.get('adaptiveFormats', [])
    
    # We look for the audio/mp4 or audio/webm links
    audio_url = ""
    for fmt in formats:
        if "audio" in fmt.get('mimeType', ''):
            audio_url = fmt.get('url')
            break
            
    return jsonify({"url": audio_url})

if __name__ == '__main__':
    app.run(debug=True)
