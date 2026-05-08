from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic

app = Flask(__name__)
CORS(app)  # Allows your GitHub Pages site to talk to your Render server
ytmusic = YTMusic()

@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Search for songs only
    search_results = ytmusic.search(query, filter="songs")
    
    results = []
    for item in search_results:
        results.append({
            "title": item.get("title"),
            "artist": item.get("artists")[0].get("name") if item.get("artists") else "Unknown",
            "videoId": item.get("videoId"),
            "thumbnail": item.get("thumbnails")[-1].get("url") if item.get("thumbnails") else ""
        })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
