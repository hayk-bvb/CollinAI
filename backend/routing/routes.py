from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# Generate session UUID
SESSION_UUID = uuid.uuid4()


@app.route('/api/chat', methods=['POST'])
def chat():
    # Call to LLM happens here
    data = request.get_json()
    return jsonify({'you_sent': data})

@app.route('/api/get_uuid', methods=['GET'])
def get_uuid():
    return jsonify({
        'session_id' : SESSION_UUID
    })

"""
chat:
    query
    session_id
"""
