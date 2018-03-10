import uuid

from flask import Flask, request, jsonify

import boto3
import os
import requests

app = Flask(__name__)

NOTES_TABLE = os.environ['NOTES_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    client = boto3.client('dynamodb')

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

@app.route("/note", methods=["POST"])
def create_note():
    note_id = str(uuid.uuid4())
    content = request.json.get('content')
    attachment = request.json.get('attachement')
    if not content:
        return jsonify({'error': 'Must have content in your message.'})

    resp = client.put_item(
        TableName=NOTES_TABLE,
        Item={
            'noteId': {'S': note_id},
            'content': {'S': content},
            'attachment': {'S': attachment}
        }
    )
    return jsonify({
        'content': content,
        'attachment': attachment
    })
