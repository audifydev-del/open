from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import os

app = Flask(__name__)
CORS(app)
ytmusic = YTMusic()

@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
