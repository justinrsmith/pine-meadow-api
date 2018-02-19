from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/streamstatus", methods=["GET"])
def stream_status():
    try:
        r = requests.head('http://73.74.197.134:48461')
        response = jsonify({'online': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
    except Exception:
        response = jsonify({'online': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
    return response
