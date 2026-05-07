import os
from flask import Flask, render_template, request, jsonify
from innertube import InnerTube

# Initialize Flask and InnerTube
app = Flask(__name__, template_folder='.')
client = InnerTube("WEB_REMIX")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    # Search specifically for songs using InnerTube
    data = client.search(query)
    
    songs = []
    try:
        # Navigating the InnerTube response to find song results
        # This structure can be complex; we look for the musicShelfRenderer
        tabs = data['contents']['tabbedContentRenderer']['tabs']
        contents = tabs[0]['content']['sectionListRenderer']['contents']
        
        results = []
        for section in contents:
            if 'musicShelfRenderer' in section:
                results = section['musicShelfRenderer']['contents']
                break
        
        for item in results:
            if 'musicTwoColumnItemRenderer' in item:
                track = item['musicTwoColumnItemRenderer']
                video_id = track['navigationEndpoint']['watchEndpoint']['videoId']
                
                songs.append({
                    'id': video_id,
                    'title': track['title']['runs'][0]['text'],
                    'artist': track['subtitle']['runs'][0]['text'] if 'runs' in track['subtitle'] else 'Unknown',
                    'thumbnail': track['thumbnail']['thumbnails'][-1]['url']
                })
    except Exception as e:
        print(f"Parsing error: {e}")
        
    return jsonify(songs)

@app.route('/get_audio', methods=['GET'])
def get_audio():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "No ID provided"}), 400

    # Fetch player data to get streaming URLs
    player_data = client.player(video_id)
    streaming_data = player_data.get('streamingData', {})
    formats = streaming_data.get('adaptiveFormats', [])
    
    # Filter for the highest quality audio-only stream
    audio_url = ""
    for fmt in formats:
        if "audio" in fmt.get('mimeType', ''):
            audio_url = fmt.get('url')
            # If the URL is missing, it might be in 'signatureCipher' (requires more complex decoding)
            if audio_url: break
            
    return jsonify({"url": audio_url})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
