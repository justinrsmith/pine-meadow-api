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
        'noteId': note_id,
        'content': content,
        'attachment': attachment
    })

@app.route("/note/<string:note_id>", methods=["GET"])
def get_note(note_id):
    resp = client.get_item(
        TableName=NOTES_TABLE,
        Key={
            'noteId': { 'S': note_id }
        }
    )
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'Note does not exist'}), 404
    return jsonify({
        'noteId': item.get('noteId').get('S'),
        'content': item.get('content').get('S'),
        'attachment': item.get('attachment').get('S')
    })

@app.route("/notes", methods=["GET"])
def get_notes():
    response = client.scan(
        TableName=NOTES_TABLE
    )
    return jsonify({
        'data': response['Items']
    })

@app.route("/notes/<string:note_id>", methods=["PUT"])
def update_note(note_id):
    json = request.get_json()
    content = json.get('content', None)
    attachment = json.get('attachement', None)
    response = client.update_item(
        TableName=NOTES_TABLE,
        Key={
            'noteId': { 'S': note_id }
        },
        UpdateExpression="set content = :c, attachment = :a",
        ExpressionAttributeValues={
            ':c': {'S': content},
            ':a': {'S': attachment}
        },
        ReturnValues="UPDATED_NEW"
    )
    return jsonify({
        'noteId': note_id,
        'content': content,
        'attachment': attachment
    })
