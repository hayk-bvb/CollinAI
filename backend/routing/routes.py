from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import uuid
from rag import RAG

app = Flask(__name__)
CORS(app)

# Generate session UUID
SESSION_UUID = uuid.uuid4()

rag = RAG(SESSION_UUID)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    print(data)
    query = data['message']

    ai_answer = rag.ask(query=query)

    return jsonify({'ai_answer': ai_answer}), 200


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
