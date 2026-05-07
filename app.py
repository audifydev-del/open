import os
from flask import Flask, render_template, request, jsonify
from innertube import InnerTube

app = Flask(__name__, template_folder='.')

# Initialize InnerTube with the YouTube Music "WEB_REMIX" client
client = InnerTube("WEB_REMIX")

def find_keys(node, key):
    """Recursively find all instances of a key in a dictionary/list."""
    if isinstance(node, list):
        for i in node:
            for x in find_keys(i, key):
                yield x
    elif isinstance(node, dict):
        if key in node:
            yield node[key]
        for j in node.values():
            for x in find_keys(j, key):
                yield x

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    try:
        # 1. Fetch raw data from InnerTube
        data = client.search(query)
        
        # 2. Find all 'musicResponsiveListItemRenderer' objects (these are the song rows)
        # This is way more reliable than hardcoding the JSON path
        results = list(find_keys(data, 'musicResponsiveListItemRenderer'))
        
        songs = []
        for item in results:
            try:
                # Extract columns that hold text (Title, Artist, Album)
                flex_columns = item.get('flexColumns', [])
                
                # Column 0 is usually the Title
                title = flex_columns[0]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
                
                # Column 1 is usually Artist & Album
                artist = "Unknown Artist"
                if len(flex_columns) > 1:
                    artist_runs = flex_columns[1]['musicResponsiveListItemFlexColumnRenderer']['text']['runs']
                    artist = artist_runs[0]['text']

                # Extract Video ID
                video_id = item.get('playlistItemData', {}).get('videoId')
                if not video_id:
                    # Fallback path for videoId
                    video_id = item.get('navigationEndpoint', {}).get('watchEndpoint', {}).get('videoId')

                # Extract Thumbnail
                thumb = ""
                thumb_container = item.get('thumbnail', {}).get('musicThumbnailRenderer', {})
                if thumb_container:
                    thumb = thumb_container['thumbnail']['thumbnails'][-1]['url']

                if video_id and title:
                    songs.append({
                        'id': video_id,
                        'title': title,
                        'artist': artist,
                        'thumbnail': thumb
                    })
            except Exception:
                continue # Skip if this specific item is malformed

        # Return unique songs (YouTube sometimes repeats results)
        seen = set()
        unique_songs = []
        for s in songs:
            if s['id'] not in seen:
                unique_songs.append(s)
                seen.add(s['id'])

        return jsonify(unique_songs[:20])

    except Exception as e:
        print(f"Search error: {e}")
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
        
        # We need to find an audio stream that has a direct URL
        # Note: Some high-copyright songs may use 'signatureCipher' which this 
        # simple logic won't decode, but it works for most tracks.
        audio_url = ""
        for fmt in formats:
            if "audio" in fmt.get('mimeType', ''):
                if 'url' in fmt:
                    audio_url = fmt['url']
                    break
                
        return jsonify({"url": audio_url})
    except Exception as e:
        print(f"Audio error: {e}")
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Use port 5000 for local, Render handles the port automatically
    app.run(host='0.0.0.0', port=5000, debug=True)
